# batch_redact.py

Batch redaction script for the [Limina](https://getlimina.ai) API. Moves a folder of input files into a timestamped staging area, redacts each file, writes outputs to a matching output folder, generates a summary report, validates completeness, and cleans up staging.

## Prerequisites

- Python 3.8+
- A running Limina instance (local or community endpoint)
- Required packages:

```bash
pip install requests python-dotenv
```

## Configuration

The API host can be supplied via the `--host` CLI flag. If omitted, it falls back to the `PRIVATEAI_LOCAL_HOST` environment variable, then defaults to `localhost`.

Optionally create a `.env` file in the same directory to set the default host:

```
PRIVATEAI_LOCAL_HOST=localhost
```

## Usage

```
python batch_redact.py [-h] [--host HOST] [--annotation TEXT] [--label LABEL] [--verbose]
                       [--repeat SECONDS] input_path staging_path output_path
```

### Positional arguments

| Argument | Description |
|---|---|
| `input_path` | Folder containing the files to redact |
| `staging_path` | Parent folder where the timestamped batch staging subfolder will be created |
| `output_path` | Parent folder where the timestamped batch output subfolder will be created |

### Optional arguments

| Flag | Description |
|---|---|
| `--host HOST` | Hostname or IP of the Limina API server (default: `PRIVATEAI_LOCAL_HOST` env var or `localhost`) |
| `--annotation TEXT` | Text pattern to count in `processed_text` for naive recall estimation (e.g. `"Date of Birth"`) |
| `--label LABEL` | Entity `best_label` value to count across all detections (e.g. `DOB`, `SSN`, `NAME`) |
| `--verbose` | Include per-detection page and text details for the `--label` entity in the report |
| `--repeat SECONDS` | Re-run the full pipeline in a loop, waiting `SECONDS` between each iteration (runs indefinitely until interrupted with Ctrl+C) |
| `-h`, `--help` | Show help message and exit |

## Examples

Minimal — redact everything in `C:\input`:

```bash
python batch_redact.py C:\input C:\staging C:\output
```

With an explicit host:

```bash
python batch_redact.py C:\input C:\staging C:\output --host 192.168.1.10
```

With annotation recall check:

```bash
python batch_redact.py C:\input C:\staging C:\output --annotation "Date of Birth" --label DOB
```

With verbose entity breakdown in the report:

```bash
python batch_redact.py C:\input C:\staging C:\output --label SSN --verbose
```

Watch a folder and redact new files every 60 seconds:

```bash
python batch_redact.py C:\input C:\staging C:\output --repeat 60
```

## Workflow

Each run starts by checking for existing work before staging anything new:

1. **Resume check** — the script scans `staging_path` for incomplete batches. If the current `input_path` files (matched by name and checksum) are already present in a staging subfolder, they are recognized as already staged. Every incomplete batch is processed before new input is staged, so interrupted work is not silently abandoned.
2. **Stage** — if no existing work was found, all files in `input_path` are moved into a new subfolder named `batch_YYYY-MM-DD_HH-MM-SS-mmm` under `staging_path`.
3. **Redact** — each file is base64-encoded and posted to the Limina `/process/files/base64` endpoint. For each file, two outputs are written to the matching subfolder under `output_path`:
   - `<name>.<ext>.redacted.<ext>` — the redacted file
   - `<name>.<ext>.redacted.json` — the API response metadata (including entities); the base64 `processed_file` payload is omitted
4. **Report** — a summary report is written to `output_path/<batch_name>/<batch_name>.report.txt`. It summarizes the JSON sidecars, processed-text lengths, and annotation/label counts.
5. **Validate** — the script checks that every expected redacted file, JSON sidecar, and the report are present in the batch output folder.
6. **Cleanup** — if validation passes, the staging folder is deleted. If any files are missing, staging is retained for inspection.

Only regular files directly inside `input_path` are moved into a new batch. Files in nested input subfolders are not staged.

## Supported file types

| Extension | MIME type |
|---|---|
| `.pdf` | `application/pdf` |
| `.dcm` | `application/dicom` |
| `.txt` | `text/plain` |
| `.csv` | `text/csv` |
| `.json` | `application/json` |
| `.jpg` / `.jpeg` | `image/jpeg` |
| `.png` | `image/png` |
| `.wav` | `audio/wav` |
| `.mp3` | `audio/mp3` |
| `.m4a` | `audio/m4a` |
| `.pptx` | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |

Files with unrecognised extensions are sent as `application/octet-stream`.

## Output structure

```
output_path/
└── batch_2026-05-25_10-30-45-123/
    ├── document.pdf.redacted.pdf
    ├── document.pdf.redacted.json
    ├── notes.txt.redacted.txt
    ├── notes.txt.redacted.json
    └── batch_2026-05-25_10-30-45-123.report.txt
```

## Report format

The report scans JSON sidecars in the batch output folder and covers:

- Number of JSON files scanned and JSON files that could not be read or parsed
- Cumulative and average `processed_text` character counts
- Count of a text annotation pattern across files with `processed_text` (`--annotation`; zero when omitted)
- Count of a specific entity label across all detections (`--label`; zero when omitted)
- Optional: per-file page and text breakdown for the label (`--verbose`)

Redaction/API errors are logged while processing. Validation detects missing outputs and retains the staging batch when any expected output is absent.
