"""Sync results into the `docs/` folder for GitHub Pages deployment.

This script copies CSV and PNG files from the project's `results/` folder
into `docs/results/` so they are included in the static site.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS_RESULTS = ROOT / "docs" / "results"


def sync_results(force: bool = False) -> None:
    """Copy results files into docs/results/.

    If ``force`` is False existing files will be skipped. When True, files are
    overwritten.
    """
    DOCS_RESULTS.mkdir(parents=True, exist_ok=True)

    for p in RESULTS.glob("*"):
        if p.suffix.lower() in {".csv", ".png", ".json"}:
            dest = DOCS_RESULTS / p.name
            if dest.exists() and not force:
                print(f"Skipping existing {dest} (use --force to overwrite)")
                continue
            shutil.copy2(p, dest)
            print(f"Copied {p} -> {dest}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync results/ into docs/results/")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files in docs/results/")
    args = parser.parse_args()

    sync_results(force=args.force)
