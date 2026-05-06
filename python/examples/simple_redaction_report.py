# Import Required Libraries
import os
import json
import re
from collections import defaultdict, Counter
from pathlib import Path

'''
This code creates a simple report outlining:
- The total number of processed files in a redaction batch run
- The total number of characters processed
- Optionally this reporting allows for "Naive" recall reporting on a single entity type. Searching for a text pattern (an extremely naive anolog for annotation), and detected label counts.
  This enables some level of a quick at a glance indication of recall assuming a very fixed set of known inputs, and is suitable when all input files are of identical format, and contain clear
  patterns that can be used as a surrogate for annotations.

This code assumes that:
- A Limina redaction job has been run against a folder of files (see process_file_directory_base64-rest.py as an example)
- The resulting json files for each request are saved in a target folder or subfolders
'''

# Define the folder path
folder_path = r"C:\MY_INPUT_FOLDER"

# Configuration for naive entity analysis / false annotation
entity_simple_annotation = None  # Text pattern to search for in processed_text eg. "Date of Birth"
entity_search = None  # Label to search for in "best_label" fields eg. DOB

verbose_mode = False  # Set to True to display page numbers and text values for each entity detection

# Verify the folder exists
if os.path.exists(folder_path):
    print(f"Folder found: {folder_path}")
else:
    print(f"Folder not found: {folder_path}")


# Find all JSON files in the folder and subdirectories
json_files = []

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.json'):
            json_files.append(os.path.join(root, file))

print(f"Found {len(json_files)} JSON file(s)")
for file in json_files:
    print(f"  - {file}")


# Dictionary to store results: filename -> length of processed_text
results = {}
total_length = 0
failed_files = []

# New counters for entity analysis
entity_annotation_counts = {}  # filename -> count of entity_simple_annotation in processed_text
best_label_counts = {}  # filename -> count of entity_search in best_label fields
total_entity_annotations = 0
total_best_label_matches = 0

# Verbose mode data collection
verbose_details = {}  # filename -> list of (page, text) tuples for matching entities

for json_file in json_files:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
            # Get just the filename for cleaner output
            filename = os.path.basename(json_file)
            
            # Check if 'processed_text' key exists
            if 'processed_text' in json_data:
                processed_text = json_data['processed_text']
                text_length = len(processed_text)
                results[filename] = text_length
                total_length += text_length
                
                # Count occurrences of entity_simple_annotation in processed_text
                if entity_simple_annotation is not None:
                    annotation_count = processed_text.count(entity_simple_annotation)
                    entity_annotation_counts[filename] = annotation_count
                    total_entity_annotations += annotation_count
                
            else:
                results[filename] = "No 'processed_text' key"
                entity_annotation_counts[filename] = 0
            
            # Count occurrences of entity_search in best_label fields and collect verbose details
            label_count = 0
            verbose_list = []
            if 'entities' in json_data and isinstance(json_data['entities'], list):
                for entity in json_data['entities']:
                    if isinstance(entity, dict) and 'best_label' in entity:
                        if entity['best_label'] == entity_search:
                            label_count += 1
                            # Collect verbose details if enabled
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


import os

report_path = os.path.join(folder_path, "report.txt")

# Buffer for all report lines
report_lines = []

def add(line: str):
    report_lines.append(line)

# Clear previous report
open(report_path, "w", encoding="utf-8").close()

# Display individual file results
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

# FINAL OUTPUT
final_report = "\n".join(report_lines)

print(final_report)

with open(report_path, "w", encoding="utf-8") as f:
    f.write(final_report)
