#!/usr/bin/env python3
"""
Convert CSV rows from 'Please Convert - Sheet1.csv' into individual JSON files
following the Worlds Rocker format.
"""

import csv
import json
import os
import re
from pathlib import Path


def create_slug(text, max_length=50):
    """Create a URL-friendly slug from text."""
    if not text:
        return "untitled"

    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')

    # Truncate to max_length
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('-', 1)[0]

    return slug or "untitled"


def parse_rubric(rubric_text):
    """Parse rubric column. If it's JSON, parse it; otherwise return as-is."""
    if not rubric_text or not rubric_text.strip():
        return ""

    try:
        # Try to parse as JSON array
        rubric_data = json.loads(rubric_text)
        return rubric_data
    except json.JSONDecodeError:
        # If it's not valid JSON, return as plain text
        return rubric_text


def convert_csv_to_json(csv_path='Please Convert - Sheet1.csv', output_dir='output'):
    """
    Read CSV file and create individual JSON files for each row.

    Args:
        csv_path: Path to the CSV file
        output_dir: Directory where JSON files will be created
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Track statistics
    processed_count = 0
    skipped_count = 0
    filename_counts = {}  # Track duplicate filenames

    print(f"Reading CSV file: {csv_path}")
    print(f"Output directory: {output_path.absolute()}\n")

    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row_index, row in enumerate(reader, start=1):
                # Skip completely empty rows
                if not any(row.values()):
                    skipped_count += 1
                    continue

                # Extract key fields from CSV
                question = row.get('Question', '').strip()
                answer = row.get('Answer', '').strip()
                steps = row.get('Steps', '').strip()
                rubric_text = row.get('Rubric', '').strip()
                filing_links = row.get('Filing Links', '').strip()

                # Create a unique ID from the question (or use row number)
                if question:
                    base_slug = create_slug(question)

                    # Handle duplicate slugs by adding a counter
                    if base_slug in filename_counts:
                        filename_counts[base_slug] += 1
                        slug = f"{base_slug}-{filename_counts[base_slug]}"
                    else:
                        filename_counts[base_slug] = 0
                        slug = base_slug
                else:
                    slug = f"row-{row_index}"

                # Parse the rubric
                rubric_data = parse_rubric(rubric_text)

                # Build JSON object following Worlds Rocker format
                json_data = {
                    "id": slug,
                    "title": question if question else f"Question {row_index}",
                    "description": steps if steps else "",
                    "answer": answer,
                    "rubric": rubric_data,
                    "metadata": {
                        "source": "google-sheets",
                        "row_index": row_index,
                        "filing_links": filing_links.split(',') if filing_links else []
                    }
                }

                # Add additional fields if they exist and are non-empty
                if row.get('Pass@10'):
                    json_data['metadata']['pass_at_10'] = row['Pass@10']
                if row.get('Mean'):
                    json_data['metadata']['mean'] = row['Mean']
                if row.get('Variance'):
                    json_data['metadata']['variance'] = row['Variance']

                # Write JSON file
                output_file = output_path / f"{slug}.json"
                with open(output_file, 'w', encoding='utf-8') as jsonfile:
                    json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)

                processed_count += 1

                # Log progress every 10 rows
                if processed_count % 10 == 0:
                    print(f"Processed {processed_count} rows...")

        # Final summary
        print(f"\n{'='*60}")
        print(f"Conversion complete!")
        print(f"{'='*60}")
        print(f"Total rows processed: {processed_count}")
        print(f"Rows skipped (empty): {skipped_count}")
        print(f"JSON files created in: {output_path.absolute()}")

    except FileNotFoundError:
        print(f"Error: Could not find CSV file at '{csv_path}'")
        print("Please ensure the file exists in the current directory.")
        return False
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = convert_csv_to_json()
    exit(0 if success else 1)
