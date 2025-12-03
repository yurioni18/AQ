#!/usr/bin/env python3
"""
Convert CSV rows to Docker Worlds JSON format.
Each row becomes a separate JSON file in the output/ directory.
"""

import csv
import json
import os
from pathlib import Path


def read_csv_and_generate_json(csv_path, output_dir):
    """
    Read CSV file and generate JSON files in Docker Worlds format.

    Args:
        csv_path: Path to the input CSV file
        output_dir: Directory where JSON files will be created
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Read the CSV file
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Get the headers and detect column names (case-insensitive)
        headers = reader.fieldnames
        print(f"Detected headers: {headers[:5]}...")  # Show first 5 headers

        # Find the correct column names (case-insensitive matching)
        question_col = None
        rubric_col = None

        for header in headers:
            if header.lower() == 'question':
                question_col = header
            elif header.lower() == 'rubric':
                rubric_col = header

        if not question_col or not rubric_col:
            raise ValueError(f"Could not find 'question' or 'rubric' columns. Found headers: {headers}")

        print(f"Using columns: Question='{question_col}', Rubric='{rubric_col}'")

        # Process each row
        row_count = 0
        skipped_count = 0
        for idx, row in enumerate(reader, start=1):
            question = row[question_col].strip()
            rubric_raw = row[rubric_col].strip()

            # Skip empty rows
            if not question:
                print(f"⚠ Skipping row {idx}: empty question")
                skipped_count += 1
                continue

            # Generate sequential ID
            task_id = f"task_{idx:03d}"

            # Parse the rubric JSON array
            rubric_points = []
            if rubric_raw:
                try:
                    rubric_points = json.loads(rubric_raw)
                    if not isinstance(rubric_points, list):
                        print(f"⚠ Warning row {idx}: rubric is not a JSON array, treating as empty")
                        rubric_points = []
                except json.JSONDecodeError as e:
                    print(f"⚠ Warning row {idx}: invalid rubric JSON ({str(e)}), treating as empty")
                    rubric_points = []
            else:
                print(f"⚠ Warning row {idx}: empty rubric column, creating task with no rubrics")

            # Build rubrics array - one rubric entry per point
            rubrics = []
            for point_idx, point in enumerate(rubric_points, start=1):
                criteria = point.get("criteria", f"Criterion {point_idx}")
                operator = point.get("operator", "correctness")

                rubric_entry = {
                    "name": criteria,
                    "weight": 1.0,
                    "score": {
                        "type": "discrete",
                        "outcomes": [
                            {"label": "yes", "score": 1.0},
                            {"label": "no", "score": 0.0}
                        ]
                    },
                    "messages": [
                        {
                            "type": "text",
                            "content": criteria,
                            "operator": operator
                        }
                    ],
                    "dependencies": []
                }
                rubrics.append(rubric_entry)

            # If no rubrics parsed, create at least one default rubric
            if not rubrics:
                rubrics.append({
                    "name": "Task completion",
                    "weight": 1.0,
                    "score": {
                        "type": "discrete",
                        "outcomes": [
                            {"label": "yes", "score": 1.0},
                            {"label": "no", "score": 0.0}
                        ]
                    },
                    "messages": [
                        {
                            "type": "text",
                            "content": "Was the task completed successfully?"
                        }
                    ],
                    "dependencies": []
                })

            # Create the JSON structure
            json_data = {
                "prompt": [
                    {
                        "type": "text",
                        "content": question
                    }
                ],
                "rubrics": rubrics,
                "include_files": False,
                "use_docker": False
            }

            # Write JSON file
            output_path = os.path.join(output_dir, f"{task_id}.json")
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)

            row_count += 1
            if row_count % 10 == 0:
                print(f"Processed {row_count} rows...")

        print(f"\n✓ Successfully generated {row_count} JSON files in '{output_dir}/'")
        if skipped_count > 0:
            print(f"⚠ Skipped {skipped_count} rows due to missing data")
        return row_count


def main():
    csv_path = "Please Convert - Sheet1.csv"
    output_dir = "output"

    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found!")
        return

    print(f"Reading CSV: {csv_path}")
    print(f"Output directory: {output_dir}/")
    print("-" * 50)

    row_count = read_csv_and_generate_json(csv_path, output_dir)

    print("-" * 50)
    print(f"Done! Created {row_count} JSON files.")
    print(f"Files are named: task_001.json, task_002.json, ... task_{row_count:03d}.json")


if __name__ == "__main__":
    main()
