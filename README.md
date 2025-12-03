# AQ - CSV to JSON Converter

This repository contains a script to convert CSV data from Google Sheets into individual JSON files following the Worlds Rocker format.

## CSV to JSON Conversion

### Overview

The `generate_worlds_rocker_json.py` script reads `Please Convert - Sheet1.csv` and converts each row into a separate JSON file. Each JSON file follows a structured format with the question, answer, steps, rubric, and metadata.

### Setup

#### Requirements

- Python 3.6 or higher (tested on Python 3.8+)
- No external dependencies required (uses only Python standard library)

#### Optional: Virtual Environment

While not required, using a virtual environment is recommended:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Usage

1. Ensure `Please Convert - Sheet1.csv` is in the same directory as the script.

2. Run the conversion script:

```bash
python3 generate_worlds_rocker_json.py
```

3. The script will:
   - Read the CSV file
   - Create an `output/` directory if it doesn't exist
   - Generate one JSON file per CSV row
   - Name each file using a slug created from the question text
   - Log progress every 10 rows

### Output Format

Each JSON file follows this structure:

```json
{
  "id": "calculate-the-ev-ebitda-and-ev-revenue",
  "title": "Calculate the EV/EBITDA and EV/Revenue metrics for Qualcomm...",
  "description": "1. Calculate the Enterprise Value...\n2. Extract common shares...",
  "answer": "EV/EBITDA = 13.69×; EV/Revenue = 4.31×.",
  "rubric": [
    {
      "criteria": "Include Common shares outstanding = 1,074M as input",
      "operator": "correctness"
    }
  ],
  "metadata": {
    "source": "google-sheets",
    "row_index": 1,
    "filing_links": ["https://www.sec.gov/Archives/..."],
    "pass_at_10": "1",
    "mean": "0.1",
    "variance": "0.09"
  }
}
```

### Features

- **Automatic slug generation**: Creates URL-friendly filenames from question text
- **Duplicate handling**: Adds numeric suffixes for duplicate questions
- **Rubric parsing**: Automatically parses JSON rubric data
- **Progress logging**: Shows progress every 10 rows
- **Empty row handling**: Safely skips empty rows
- **UTF-8 encoding**: Properly handles special characters

### Troubleshooting

**File not found error:**
- Ensure `Please Convert - Sheet1.csv` is in the same directory as the script
- Check the filename matches exactly (including spaces and capitalization)

**Permission errors:**
- Ensure you have write permissions in the current directory
- The script will create the `output/` directory automatically

**Encoding issues:**
- The script uses UTF-8 encoding by default
- If you encounter encoding errors, the CSV may need to be re-exported from Google Sheets

### Directory Structure

```
.
├── generate_worlds_rocker_json.py  # Conversion script
├── Please Convert - Sheet1.csv      # Input CSV file
├── output/                          # Generated JSON files
│   ├── calculate-the-ev-ebitda-and-ev-revenue.json
│   ├── question-about-revenue.json
│   └── ...
└── README.md                        # This file
```
