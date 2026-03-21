# Drug Stats

A Python application for retrieving and analyzing FDA drug approval statistics using the official FDA API endpoints.

## Overview

This application retrieves and analyzes FDA drug approval statistics using the official FDA API endpoints. It provides two views of the data:

1. **All New Drug Approvals** (Type 1-4 and Type 10): Counts new molecular entities, active ingredients, dosage forms, combinations, and new indications
2. **New Molecular Entities Only** (Type 1): Tracks new molecular entity approvals, which matches the FDA's official "new drug approval" count

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

1. Create a virtual environment (using `uv`):

```bash
uv venv
source .venv/bin/activate
```

1. Install dependencies:

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

## Publishing results (GitHub Pages)

This project can publish generated CSVs and plots as a static site via GitHub Pages. The repository includes a workflow `.github/workflows/pages.yml` that runs on push to `main` and performs the following steps:

- Installs dependencies (`pip install -r requirements.txt`)
- Runs `python src/main.py` to generate `results/`
- Runs `python scripts/sync_results.py` to copy results into `docs/results/`
- Deploys the `docs/` folder to GitHub Pages (the repo contains `docs/CNAME` configured for `fdadrugstats.mesguerra.org`)

If you prefer local control, run:

```bash
python src/main.py
python scripts/sync_results.py --force
```

To view the generated site locally, serve the `docs/` folder and open http://localhost:8000 in your browser:

```bash
python -m http.server 8000 --directory docs
# then open http://localhost:8000
```

Note: The CI workflow runs `python scripts/sync_results.py` without `--force`, so it will skip overwriting existing files in `docs/results/`. If you want the workflow to always publish newly generated files, either update the workflow to call `python scripts/sync_results.py --force` or modify the sync script to overwrite when files differ.

> Add `FDA_API_KEY` as a repository secret (`Settings → Secrets → Actions`) to avoid rate limits when the workflow runs.


## Development

Running integration tests (live API)

To execute tests that call the live FDA API (these are slower and subject to rate limits), run:

```bash
pytest -m integration
```



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
