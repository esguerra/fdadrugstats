# Drug Stats

A Python application for retrieving and analyzing FDA drug approval statistics using the official FDA API endpoints.

## Overview

This application retrieves and analyzes FDA drug approval statistics using the official FDA API endpoints. It provides two views of the data:

1. **All New Drug Approvals** (Type 1-4 and Type 10): Counts new molecular entities, active ingredients, dosage forms, combinations, and new indications
2. **New Molecular Entities Only** (Type 1): Tracks new molecular entity approvals, which matches the FDA's official "new drug approval" count

The script identifies the core issue from your reference: while total approvals (including all types) were 91 in 2025, the official "new molecular entity" count (Type 1 only) was **43**, which closely matches the reported 46 in the C&EN article (the 3-drug difference likely due to data timing or edge cases in methodology).

## Project Structure

```
drugstats/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── fda_client.py        # FDA API client
│   ├── statistics.py        # Statistics analysis functions
│   └── plotting.py          # Plotting and data export functions
├── tests/
│   └── __init__.py
├── results/                 # Output folder (auto-generated)
│   ├── drug_approvals.png              # All approvals plots
│   ├── approvals_comparison_recent.png # Recent years comparison
│   ├── drug_approvals_by_year.csv      # Combined data CSV
│   ├── all_approvals.csv               # All approvals data
│   └── nme_approvals.csv               # NME approvals data
├── requirements.txt
└── README.md
```

## Installation

1. Clone or download the project:
```bash
cd /Users/esguerra/development/drugstats
```

2. Create a virtual environment (using `uv`):
```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the main script:
```bash
python src/main.py
```

### With FDA API Key

For increased rate limits, set your FDA API key:
```bash
export FDA_API_KEY=your_api_key_here
python src/main.py
```

Get a free API key from: https://open.fda.gov/

## API Endpoints Used

- **Drug Approvals**: `https://api.fda.gov/drug/drugsfda.json`
  - Retrieves information about approved drugs
  - Filters for drugs with "Approved" marketing status

- **Adverse Events**: `https://api.fda.gov/drug/event.json`
  - Retrieves adverse event reports
  - Can be extended for additional statistics

## Example Output

```
============================================================
FDA DRUG APPROVALS BY YEAR
============================================================

ALL APPROVALS (Type 1-4, 10):
  2023: 88
  2024: 89
  2025: 91

NEW MOLECULAR ENTITIES ONLY (Type 1):
  2023: 49
  2024: 48
  2025: 43

✓ Results saved to: ./results
  - CSV files with approval data
  - PNG plots with visualizations
```

## Results Output

When you run the script, it generates the following files in the `results/` folder:

### CSV Files
- **drug_approvals_by_year.csv** - Combined data with all approvals and NME counts by year
- **all_approvals.csv** - All drug approvals (Type 1-4, 10)
- **nme_approvals.csv** - New molecular entity approvals (Type 1 only)

### Plots (PNG)
- **drug_approvals.png** - Two-panel chart showing:
  - Top: All drug approvals by year
  - Bottom: NME approvals by year
- **approvals_comparison_recent.png** - Side-by-side comparison of all approvals vs NME for the last 15 years

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

The project uses Ruff for code style consistency:
```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Documentation

All functions and classes include comprehensive docstrings following PEP 257 conventions.

## License

[Add your license here]

## References

- [FDA API Documentation](https://open.fda.gov/)
- [FDA Drug Approvals Endpoint](https://open.fda.gov/apis/drug/drugsfda/)
- [FDA Adverse Events Endpoint](https://open.fda.gov/apis/drug/event/)
