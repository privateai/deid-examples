import argparse
import hashlib
import os
import dotenv
import requests
import base64
import time
import json
import shutil
from datetime import datetime

dotenv.load_dotenv()

url = None


# ── Staging helpers ───────────────────────────────────────────────────────────
def _file_checksum(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _find_existing_staging(input_path, staging_path, output_path):
    """Return a staging subfolder with pending work, or None.

    Scans every staging subfolder and skips any that are empty or already have
    complete output. Among the remaining (files present, output incomplete):

      - If one matches the current input files exactly (by name + checksum),
        it is returned immediately — the input is already staged, resume it.
      - Otherwise the first incomplete staging subfolder found is returned so
        any interrupted batch is not silently abandoned.

    Returns None only when every staging subfolder is empty or fully output.
    """
    if not os.path.isdir(staging_path):
        return None

    input_files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
    input_checksums = {f: _file_checksum(os.path.join(input_path, f)) for f in input_files} if input_files else {}

    first_incomplete = None

    for name in sorted(os.listdir(staging_path)):
        subfolder = os.path.join(staging_path, name)
        if not os.path.isdir(subfolder):
            continue
        staged = [f for f in os.listdir(subfolder) if os.path.isfile(os.path.join(subfolder, f))]
        if not staged:
            continue
        output_sub = os.path.join(output_path, name)
        if _is_batch_complete(subfolder, output_sub):
            continue
        if first_incomplete is None:
            first_incomplete = subfolder
        if input_checksums and len(staged) == len(input_files) and all(
            os.path.isfile(os.path.join(subfolder, f))
            and _file_checksum(os.path.join(subfolder, f)) == cs
            for f, cs in input_checksums.items()
        ):
            return subfolder

    return first_incomplete


def _is_batch_complete(staging_folder, output_folder):
    """Return True if every file in staging_folder has both expected redacted outputs and a report in output_folder."""
    batch_name = os.path.basename(staging_folder)
    if not os.path.isdir(output_folder):
        return False
    if not os.path.isfile(os.path.join(output_folder, f"{batch_name}.report.txt")):
        return False
    for name in os.listdir(staging_folder):
        if not os.path.isfile(os.path.join(staging_folder, name)):
            continue
        _, ext = os.path.splitext(name)
        root = os.path.splitext(name)[0]
        if not os.path.isfile(os.path.join(output_folder, f"{root}{ext}.redacted{ext}")):
            return False
        if not os.path.isfile(os.path.join(output_folder, f"{name}.redacted.json")):
            return False
    return True


def _find_unprocessed_batches(staging_path, output_path):
    """Return list of (batch_name, staging_subfolder, output_subfolder) for every incomplete batch."""
    if not os.path.isdir(staging_path):
        return []
    result = []
    for name in sorted(os.listdir(staging_path)):
        staging_sub = os.path.join(staging_path, name)
        if not os.path.isdir(staging_sub):
            continue
        output_sub = os.path.join(output_path, name)
        if not _is_batch_complete(staging_sub, output_sub):
            result.append((name, staging_sub, output_sub))
    return result


# ── Redaction Job ──────────────────────────────────────────────────────────────
def _make_pai_call_file(data, content_type):
    """POST a single base64-encoded file to the Limina /process/files/base64 endpoint.

    Sends a fixed entity detection configuration that enables PII types covering names,
    contact details, locations, and financial identifiers. Raises on any non-2xx response.

    Args:
        data:         Base64-encoded file content as a UTF-8 string.
        content_type: MIME type of the file (e.g. 'application/pdf', 'text/plain').

    Returns:
        Parsed JSON response dict from the API.
    """
    request = {
        "file": {
            "data": data,
            "content_type": content_type
        },
        "entity_detection": {
            "entity_types": [
                {
                    "type": "ENABLE",
                    "value": [
                        "EMAIL_ADDRESS", "LOCATION", "LOCATION_ADDRESS",
                        "LOCATION_ADDRESS_STREET", "LOCATION_CITY", "LOCATION_COUNTRY",
                        "LOCATION_STATE", "LOCATION_ZIP", "NAME", "NAME_FAMILY",
                        "NAME_GIVEN", "PHONE_NUMBER", "BANK_ACCOUNT", "CREDIT_CARD",
                        "CREDIT_CARD_EXPIRATION", "CVV", "ROUTING_NUMBER"
                    ]
                }
            ]
        }
    }

    response = requests.post(f"{url}process/files/base64", json=request)
    response.raise_for_status()
    return response.json()


def _redact_file(input_file_path, mime_type, output_dir):
    """Redact a single file and write both outputs to output_dir.

    Reads the file, calls the Limina API, then writes:
      - <stem>.<ext>.redacted.<ext>  — the redacted file decoded from the base64 response
      - <original_name>.redacted.json — the full API response with 'processed_file' stripped out

    Args:
        input_file_path: Absolute path to the source file.
        mime_type:       MIME type to declare when sending the file to the API.
        output_dir:      Directory where both output files will be written.

    Returns:
        API response dict (without 'processed_file'), or None if the file was not found
        or the response contained no redacted file.
    """
    response = None
    print(f"pai_redactFile")
    stt = time.time()

    if os.path.isfile(input_file_path):
        with open(input_file_path, "rb") as f:
            file_bytes = f.read()
            b64_str = base64.b64encode(file_bytes).decode("utf-8")
            response = _make_pai_call_file(b64_str, mime_type)

    print(f"Done: Total Time {time.time() - stt:.2f}")

    if response and 'processed_file' in response:
        b64_data = response['processed_file']
        _, ext = os.path.splitext(input_file_path)
        base_name = os.path.basename(input_file_path)
        root_name = os.path.splitext(base_name)[0]

        redacted_file_path = os.path.join(output_dir, f"{root_name}{ext}.redacted{ext}")
        with open(redacted_file_path, 'wb') as output_file:
            output_file.write(base64.b64decode(b64_data))
        print(f"File saved to {redacted_file_path}")

        del response['processed_file']

        json_file_path = os.path.join(output_dir, f"{base_name}.redacted.json")
        response_content = json.dumps(response, indent=4)
        with open(json_file_path, 'wb') as output_file:
            output_file.write(response_content.encode('utf-8'))
        print(f"File saved to {json_file_path}")

    else:
        print("Response does not contain 'file: data'")

    return response


def run_redaction_job(staging_folder, output_folder):
    """Walk staging_folder recursively and redact every file via the Limina API.

    MIME type is inferred from file extension; unknown extensions fall back to
    'application/octet-stream'. Failures are caught per-file so a single bad file
    does not abort the rest of the batch.

    Args:
        staging_folder: Root folder of staged input files (read-only — files are not moved).
        output_folder:  Destination folder for redacted files and JSON sidecars; created if absent.

    Returns:
        List of dicts, one per file: {'path', 'ok': True, 'response'} on success,
        {'path', 'ok': False, 'error'} on failure.
    """
    os.makedirs(output_folder, exist_ok=True)

    ext_mime = {
        '.pdf':  'application/pdf',
        '.dcm':  'application/dicom',
        '.txt':  'text/plain',
        '.csv':  'text/csv',
        '.json': 'application/json',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png':  'image/png',
        '.wav':  'audio/wav',
        '.mp3':  'audio/mp3',
        '.m4a':  'audio/m4a',        
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    }

    results = []
    for root, dirs, files in os.walk(staging_folder):
        for name in files:
            file_path = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()
            mime = ext_mime.get(ext, 'application/octet-stream')
            print(f"Processing {file_path} (mime={mime})")
            try:
                res = _redact_file(file_path, mime, output_folder)
                results.append({'path': file_path, 'ok': True, 'response': res})
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                results.append({'path': file_path, 'ok': False, 'error': str(e)})
    return results


# ── Report Generation ──────────────────────────────────────────────────────────
def generate_report(folder_path, report_output_path,
                    entity_simple_annotation=None, entity_search=None, verbose_mode=False):
    """Scan folder_path for redaction JSON sidecars and write a summary report.

    Reads every .json file in folder_path (recursively), aggregates processed_text lengths,
    and optionally performs two lightweight entity checks:
      - Annotation count: substring search in processed_text for entity_simple_annotation,
        useful as a naive surrogate for recall when inputs follow a fixed format.
      - Label count: counts how many detected entities carry the best_label matching
        entity_search, with optional per-detection page/text detail in verbose mode.

    Args:
        folder_path:              Directory containing .redacted.json sidecar files to analyse.
        report_output_path:       Full path where the report .txt file will be written.
        entity_simple_annotation: Optional text pattern to count in processed_text (e.g. 'Date of Birth').
        entity_search:            Optional entity label to count across detections (e.g. 'DOB').
        verbose_mode:             When True, include per-detection page and text for entity_search.
    """
    json_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))

    print(f"Found {len(json_files)} JSON file(s)")
    for file in json_files:
        print(f"  - {file}")

    results = {}
    total_length = 0
    failed_files = []
    entity_annotation_counts = {}
    best_label_counts = {}
    total_entity_annotations = 0
    total_best_label_matches = 0
    verbose_details = {}

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            filename = os.path.basename(json_file)

            if 'processed_text' in json_data:
                processed_text = json_data['processed_text']
                text_length = len(processed_text)
                results[filename] = text_length
                total_length += text_length

                if entity_simple_annotation is not None:
                    annotation_count = processed_text.count(entity_simple_annotation)
                    entity_annotation_counts[filename] = annotation_count
                    total_entity_annotations += annotation_count
            else:
                results[filename] = "No 'processed_text' key"
                entity_annotation_counts[filename] = 0

            label_count = 0
            verbose_list = []
            if 'entities' in json_data and isinstance(json_data['entities'], list):
                for entity in json_data['entities']:
                    if isinstance(entity, dict) and 'best_label' in entity:
                        if entity['best_label'] == entity_search:
                            label_count += 1
                            if verbose_mode:
                                page = entity.get('location', {}).get('page', 'N/A')
                                text = entity.get('text', 'N/A')
                                verbose_list.append((page, text))

            best_label_counts[filename] = label_count
            total_best_label_matches += label_count
            if verbose_mode:
                verbose_details[filename] = verbose_list

        except json.JSONDecodeError as e:
            filename = os.path.basename(json_file)
            failed_files.append((filename, f"Invalid JSON: {str(e)}"))
            results[filename] = "Error"
            entity_annotation_counts[filename] = 0
            best_label_counts[filename] = 0
            if verbose_mode:
                verbose_details[filename] = []
            print(f"Error parsing {filename}: {str(e)}")

        except Exception as e:
            filename = os.path.basename(json_file)
            failed_files.append((filename, str(e)))
            results[filename] = "Error"
            entity_annotation_counts[filename] = 0
            best_label_counts[filename] = 0
            if verbose_mode:
                verbose_details[filename] = []
            print(f"Error reading {filename}: {str(e)}")

    report_lines = []

    def add(line: str):
        report_lines.append(line)

    add("=" * 80)
    add("ENHANCED PROCESSED TEXT ANALYSIS")
    add("=" * 80)
    add(f"\nTotal JSON files processed: {len(json_files)}")
    add(f"Successfully processed: {len(results)}")
    add(f"Failed files: {len(failed_files)}")

    add("\n" + "-" * 80)
    add("TEXT LENGTH ANALYSIS")
    add("-" * 80)
    add(f"Total cumulative length of all 'processed_text' entries: {total_length:,} characters")
    add(f"Average length per file: {total_length // len(results) if results else 0:,} characters")

    add("\n" + "-" * 80)
    add(f"ENTITY ANNOTATION ANALYSIS ('{entity_simple_annotation}')")
    add("-" * 80)
    add(f"Total occurrences across all files: {total_entity_annotations:,}")

    add("\n" + "-" * 80)
    add(f"BEST LABEL ANALYSIS ('{entity_search}')")
    add("-" * 80)
    add(f"Total occurrences across all files: {total_best_label_matches:,}")

    add("\n" + "-" * 80)
    add("DETAILED RESULTS PER FILE")
    add("-" * 80)
    add(f"{'Filename':<50} | {'Length':<10} | {'Annotations':<11} | {'Labels':<6}")
    add("-" * 80)

    for filename in sorted(results.keys()):
        length_info = f"{results[filename]:,}" if isinstance(results[filename], int) else str(results[filename])
        annotation_count = entity_annotation_counts.get(filename, 0)
        label_count = best_label_counts.get(filename, 0)
        add(f"{filename:<50} | {length_info:<10} | {annotation_count:<11} | {label_count:<6}")

    if failed_files:
        add("\n" + "-" * 80)
        add("Failed Files:")
        add("-" * 80)
        for filename, error in failed_files:
            add(f"{filename}: {error}")

    if verbose_mode and verbose_details:
        add("\n" + "=" * 80)
        add(f"VERBOSE DETAILS - {entity_search} DETECTIONS")
        add("=" * 80)

        for filename in sorted(verbose_details.keys()):
            details = verbose_details[filename]
            if details:
                add(f"\n{filename}:")
                add(f"  {'Page':<6} | {'Text'}")
                add(f"  {'-'*6} | {'-'*50}")
                for page, text in details:
                    truncated_text = text[:47] + "..." if len(text) > 50 else text
                    add(f"  {page:<6} | {truncated_text}")

        add(f"\nTotal {entity_search} detections with verbose details: "
            f"{sum(len(details) for details in verbose_details.values())}")

    final_report = "\n".join(report_lines)
    print(final_report)

    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"Report saved to {report_output_path}")


# ── Validation ────────────────────────────────────────────────────────────────
def validate_output(staging_folder, output_folder, report_path):
    """Verify that every file in staging_folder produced both expected outputs in output_folder.

    For each staged file <stem>.<ext>, checks for:
      - <stem>.<ext>.redacted.<ext>  — the redacted file
      - <stem>.<ext>.redacted.json   — the API response sidecar
    Also checks that the batch report exists at report_path.

    Prints a summary of present and missing files. Staging should only be deleted
    when this returns True, ensuring no outputs were silently dropped.

    Args:
        staging_folder: Folder containing the original staged input files.
        output_folder:  Folder where redacted outputs and JSON sidecars were written.
        report_path:    Expected path of the batch report file.

    Returns:
        True if all expected files are present, False if any are missing.
    """
    missing = []
    present = []

    for _, _, files in os.walk(staging_folder):
        for name in files:
            _, ext = os.path.splitext(name)
            root_name = os.path.splitext(name)[0]

            expected_redacted = os.path.join(output_folder, f"{root_name}{ext}.redacted{ext}")
            expected_json     = os.path.join(output_folder, f"{name}.redacted.json")

            for expected in (expected_redacted, expected_json):
                if os.path.isfile(expected):
                    present.append(expected)
                else:
                    missing.append(expected)

    if os.path.isfile(report_path):
        present.append(report_path)
    else:
        missing.append(report_path)

    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)
    print(f"Present : {len(present)}")
    print(f"Missing : {len(missing)}")

    if missing:
        print("\nMissing files:")
        for f in missing:
            print(f"  MISSING  {f}")
    else:
        print("\nAll expected output files verified.")

    return len(missing) == 0


# ── Batch runner ──────────────────────────────────────────────────────────────
def _process_batch(batch_name, batch_staging_path, batch_output_path, args):
    """Run redaction, report, validate, and cleanup for a single staging batch."""
    print(f"\nBatch:   {batch_name}")
    print(f"Staging: {batch_staging_path}")
    print(f"Output:  {batch_output_path}")

    results = run_redaction_job(batch_staging_path, batch_output_path)

    if results != None:
        report_path = os.path.join(batch_output_path, f"{batch_name}.report.txt")
        generate_report(
            batch_output_path,
            report_path,
            entity_simple_annotation=args.entity_simple_annotation,
            entity_search=args.entity_search,
            verbose_mode=args.verbose_mode,
        )

        if validate_output(batch_staging_path, batch_output_path, report_path):
            shutil.rmtree(batch_staging_path)
            print(f"Staging folder deleted: {batch_staging_path}")
        else:
            print(f"Validation failed — staging folder retained: {batch_staging_path}")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    """Entry point: parse CLI arguments and run the full batch redaction pipeline.

    Orchestrates the four pipeline stages in order:
      1. Stage   — move input files into a timestamped subfolder under staging_path.
      2. Redact  — call run_redaction_job to process every staged file via the Limina API.
      3. Report  — call generate_report to write a summary of results to the output folder.
      4. Validate & cleanup — call validate_output; delete staging only if all outputs are confirmed.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Batch redact a folder of files using the Private AI API.\n\n"
            "Workflow:\n"
            "  1. Files in INPUT_PATH are moved into a timestamped subfolder under STAGING_PATH.\n"
            "  2. Each file is sent to the Private AI API for redaction; outputs are written to\n"
            "     a matching subfolder under OUTPUT_PATH.\n"
            "  3. A summary report is saved as <batch_name>.report.txt in the output folder.\n"
            "  4. Output is validated; if all files are present the staging folder is deleted.\n\n"
            "Examples:\n"
            "  python batch_redact.py C:\\input C:\\staging C:\\output\n"
            "  python batch_redact.py /data/in /data/staging /data/out --host 192.168.1.10\n"
            "  python batch_redact.py /data/in /data/staging /data/out --annotation \"Date of Birth\" --label DOB\n"
            "  python batch_redact.py /data/in /data/staging /data/out --label SSN --verbose\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--host",
        default=os.environ.get("PRIVATEAI_LOCAL_HOST", "localhost"),
        metavar="HOST",
        help="Hostname or IP of the Limina API server (default: PRIVATEAI_LOCAL_HOST env var or 'localhost')",
    )

    parser.add_argument("input_path",   help="Folder containing files to redact")
    parser.add_argument("staging_path", help="Parent folder where the timestamped batch staging subfolder will be created")
    parser.add_argument("output_path",  help="Parent folder where the timestamped batch output subfolder will be created")

    parser.add_argument(
        "--annotation",
        dest="entity_simple_annotation",
        default=None,
        metavar="TEXT",
        help="Text pattern to count in processed_text for naive recall estimation (e.g. 'Date of Birth')",
    )
    parser.add_argument(
        "--label",
        dest="entity_search",
        default=None,
        metavar="LABEL",
        help="Entity best_label value to count across all detections (e.g. DOB, SSN, NAME)",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose_mode",
        action="store_true",
        default=False,
        help="Include per-detection page and text details for the --label entity in the report",
    )
    parser.add_argument(
        "--repeat",
        dest="repeat_timer",
        type=int,
        default=None,
        metavar="SECONDS",
        help="Re-run the full pipeline in a loop, waiting SECONDS between each iteration (runs indefinitely until interrupted)",
    )

    args = parser.parse_args()

    global url
    url = f"{args.host}/"

    while True:
        existing = _find_existing_staging(args.input_path, args.staging_path, args.output_path)
        if existing:
            print(f"Input files already staged in: {existing}")
            print("Scanning for unprocessed batches...")
            unprocessed = _find_unprocessed_batches(args.staging_path, args.output_path)
            if not unprocessed:
                print("No unprocessed batches found.")
            else:
                print(f"Found {len(unprocessed)} unprocessed batch(es).")
                for batch_name, batch_staging_path, batch_output_path in unprocessed:
                    _process_batch(batch_name, batch_staging_path, batch_output_path, args)
        else:
            input_files = [f for f in os.listdir(args.input_path) if os.path.isfile(os.path.join(args.input_path, f))]
            if not input_files:
                print("No files found in input folder. Nothing to process.")
            else:
                _now = datetime.now()
                batch_name = "batch_" + _now.strftime("%Y-%m-%d_%H-%M-%S-") + f"{_now.microsecond // 1000:03d}"
                batch_staging_path = os.path.join(args.staging_path, batch_name)
                batch_output_path  = os.path.join(args.output_path, batch_name)

                print(f"\nCreating staging folder: {batch_staging_path}")
                os.makedirs(batch_staging_path, exist_ok=True)

                moved = 0
                for entry in os.listdir(args.input_path):
                    src = os.path.join(args.input_path, entry)
                    if os.path.isfile(src):
                        shutil.move(src, os.path.join(batch_staging_path, entry))
                        moved += 1
                print(f"Moved {moved} file(s) to staging")

                _process_batch(batch_name, batch_staging_path, batch_output_path, args)

        if args.repeat_timer is None:
            break
        print(f"\nWaiting {args.repeat_timer}s before next run... (Ctrl+C to stop)")
        time.sleep(args.repeat_timer)

    print("Done")


if __name__ == "__main__":
    main()
