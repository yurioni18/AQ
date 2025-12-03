#!/usr/bin/env python3
"""
Generate Docker Worlds JSON files from CSV with proper rubric parsing.
Each rubric point becomes a separate content entry in messages[0].content.
"""

import csv
import json
import os
import sys
from pathlib import Path


def generate_world_json(row_id, question, rubric_json_str):
    """
    Generate a Docker Worlds JSON structure for a single row.

    Args:
        row_id: Unique identifier for the question
        question: The question text (title)
        rubric_json_str: JSON string containing array of rubric points

    Returns:
        dict: Docker Worlds formatted structure
    """
    # Parse rubric points
    content_entries = []

    if rubric_json_str and rubric_json_str.strip():
        try:
            rubric_points = json.loads(rubric_json_str)

            # Build one content entry per rubric point
            for point in rubric_points:
                content_entry = {
                    "type": "text",
                    "text": point.get("criteria", ""),
                    "operator": point.get("operator", "correctness")
                }
                content_entries.append(content_entry)

        except json.JSONDecodeError as e:
            print(f"WARNING: Invalid JSON in rubric for row {row_id}: {e}", file=sys.stderr)
            print(f"  Rubric content: {rubric_json_str[:100]}...", file=sys.stderr)
            # Continue with empty content array

    # Build the Docker Worlds structure
    world_json = {
        "id": row_id,
        "title": question,
        "weight": 1,
        "score_type": "discrete",
        "outcomes": [
            {"label": "yes", "value": 1},
            {"label": "no", "value": 0}
        ],
        "docker": False,
        "include_files": False,
        "messages": [
            {
                "role": "system",
                "content": content_entries
            }
        ]
    }

    return world_json


def main():
    # Input and output paths
    csv_file = "Please Convert - Sheet1.csv"
    output_dir = Path("output")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Read CSV and generate JSON files
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=1):
            # Generate ID from row number
            row_id = f"rocker_{row_num:03d}"

            question = row.get('Question', '').strip()
            rubric = row.get('Rubric', '').strip()

            if not question:
                print(f"WARNING: Skipping row {row_num} - no question found", file=sys.stderr)
                continue

            # Generate JSON structure
            world_json = generate_world_json(row_id, question, rubric)

            # Write to file
            output_file = output_dir / f"{row_id}.json"
            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(world_json, out_f, indent=2, ensure_ascii=False)

            print(f"Generated: {output_file} ({len(world_json['messages'][0]['content'])} rubric points)")

    print(f"\n✓ Done! Generated JSON files in {output_dir}/")


if __name__ == "__main__":
    main()
