# Drug Stats

A Python application and static reporting site for retrieving and analyzing FDA drug approval and adverse event statistics using openFDA API endpoints.

## Overview

This application retrieves and analyzes FDA drug approval statistics using openFDA. It provides:

1. **All New Drug Approvals** (Type 1-4 and Type 10): Counts new molecular entities, active ingredients, dosage forms, combinations, and new indications.

2. **New Molecular Entities Only** (Type 1): Tracks new molecular entity approvals, which matches the FDA's official "new drug approval" count.

3. **Adverse Event Summaries**: Reports by year plus top reported drugs and reactions from the FDA adverse event endpoint.

The generated CSVs and static PNG plots are published in `docs/results/`, and `docs/index.html` renders interactive Plotly charts for the deployed GitHub Pages site.

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
│   ├── __init__.py
│   └── test_adverse_events_live.py
├── results/                 # Output folder (auto-generated)
│   ├── drug_approvals.png
│   ├── approvals_comparison_recent.png
│   ├── drugs_per_company_top30.png
│   ├── adverse_events_by_year.png
│   ├── top_reported_drugs.png
│   ├── top_reactions.png
│   ├── company_distribution.png
│   ├── drug_approvals_by_year.csv
│   ├── all_approvals.csv
│   ├── nme_approvals.csv
│   ├── approved_drugs_all.csv
│   ├── approved_drugs_nme.csv
│   ├── adverse_events_by_year.csv
│   ├── top_reported_drugs.csv
│   └── top_reactions.csv
├── docs/                    # GitHub Pages static site
│   ├── index.html
│   ├── js/plotly_charts.js
│   └── results/             # Synced CSV/PNG outputs for deployment
├── scripts/
│   └── sync_results.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the project and enter the repository:

```bash
git clone https://github.com/esguerra/fdadrugstats.git
cd fdadrugstats
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

This fetches approval and adverse-event summaries, writes CSV files to `results/`, and generates static PNG plots.

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
  - Counts original (`ORIG`) submissions with approved (`AP`) submission status for the selected submission class codes

- **Adverse Events**: `https://api.fda.gov/drug/event.json`
  - Aggregates adverse event reports by received date
  - Retrieves top reported drugs and top reactions

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
  - CSV files with approval statistics
  - CSV files with drug names and details
  - PNG plots with visualizations
```

## Results Output

When you run the script, it generates the following files in the `results/` folder:

### CSV Files

- **drug_approvals_by_year.csv** - Combined data with all approvals and NME counts by year
- **all_approvals.csv** - All approval counts by year (Type 1-4, 10)
- **nme_approvals.csv** - NME approval counts by year (Type 1 only)
- **approved_drugs_all.csv** - Approved drug details for all included approval types
- **approved_drugs_nme.csv** - Approved drug details for NMEs only
- **adverse_events_by_year.csv** - Adverse event report counts by year
- **top_reported_drugs.csv** - Top drugs reported in adverse event records
- **top_reactions.csv** - Top reactions reported in adverse event records

### Plots (PNG)

- **drug_approvals.png** - Two-panel chart showing:
  - Top: All drug approvals by year
  - Bottom: NME approvals by year
- **approvals_comparison_recent.png** - Side-by-side comparison of all approvals vs NME for the last 15 years
- **drugs_per_company_top30.png** - Top pharmaceutical companies by approved drug count
- **company_distribution.png** - Distribution of approved drugs across companies
- **adverse_events_by_year.png** - Adverse event reports by year
- **top_reported_drugs.png** - Top reported drugs in adverse event records
- **top_reactions.png** - Top reported reactions in adverse event records

## Publishing results (GitHub Pages)

This project can publish generated CSVs and plots as a static site via GitHub Pages. The repository includes a workflow `.github/workflows/pages.yml` that runs on push to `main` and performs the following steps:

- Installs dependencies (`pip install -r requirements.txt`)
- Runs `python src/main.py` to generate `results/`
- Runs `python scripts/sync_results.py --force` to copy results into `docs/results/`
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

The published page uses interactive Plotly charts by default and includes a toggle to use static PNG plots for slow connections.

> Add `FDA_API_KEY` as a repository secret (`Settings → Secrets → Actions`) to avoid rate limits when the workflow runs. Live API tests and deployment can fail with openFDA `403`/rate-limit responses if no valid key is available.

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

## References

- [FDA API Documentation](https://open.fda.gov/)
- [FDA Drug Approvals Endpoint](https://open.fda.gov/apis/drug/drugsfda/)
- [FDA Adverse Events Endpoint](https://open.fda.gov/apis/drug/event/)
