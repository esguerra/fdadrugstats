"""Main script for FDA drug approval statistics."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from fda_client import FDAClient
from plotting import (
    create_approval_plots,
    create_company_plots,
    create_adverse_event_plots,
    save_approval_data,
    save_approved_drugs,
    save_adverse_events_data,
)
from statistics import calculate_summary_stats, format_statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Results directory
RESULTS_DIR = Path(__file__).parent.parent / "results"


def main() -> None:
    """Run the main script to retrieve and display drug approval statistics."""
    try:
        api_key: Optional[str] = os.getenv("FDA_API_KEY")

        logger.info("Initializing FDA API client...")
        client = FDAClient(api_key=api_key)

        with client:
            # Get all approvals (Type 1-4 and Type 10)
            logger.info(
                "Fetching all drug approvals by year "
                "(Type 1-4, 10)..."
            )
            all_approvals = client.get_drug_approvals_by_year(
                include_all_types=True
            )

            # Get all approved drugs (Type 1-4 and Type 10)
            logger.info("Fetching all approved drug names...")
            all_drugs = client.get_approved_drugs(
                include_all_types=True
            )

            # Get NME-only approvals (Type 1)
            logger.info(
                "Fetching new molecular entity approvals by year "
                "(Type 1 only)..."
            )
            nme_approvals = client.get_drug_approvals_by_year(
                include_all_types=False
            )

            # Get NME-only approved drugs (Type 1)
            logger.info("Fetching NME approved drug names...")
            nme_drugs = client.get_approved_drugs(
                include_all_types=False
            )

            if all_approvals:
                print("\n" + "=" * 70)
                print("FDA DRUG APPROVALS BY YEAR")
                print("=" * 70)
                print(
                    "\nALL APPROVALS (Type 1-4, 10 - New Molecular Entities,"
                )
                print("Active Ingredients, Dosage Forms, Combinations, New "
                      "Indications):")
                print("-" * 70)
                print(format_statistics(all_approvals))

                stats = calculate_summary_stats(all_approvals)
                print("\nSummary Statistics (All Types):")
                print("-" * 70)
                print(f"  Total Approvals: {stats['total']:,}")
                print(f"  Average per Year: {stats['average']}")
                print(f"  Minimum: {stats['min']} (Year {stats['min_year']})")
                print(f"  Maximum: {stats['max']} (Year {stats['max_year']})")

            if nme_approvals:
                print("\n" + "-" * 70)
                print("\nNEW MOLECULAR ENTITIES ONLY (Type 1):")
                print("-" * 70)
                print(format_statistics(nme_approvals))

                stats_nme = calculate_summary_stats(nme_approvals)
                print("\nSummary Statistics (NME Only):")
                print("-" * 70)
                print(f"  Total NME Approvals: {stats_nme['total']:,}")
                print(f"  Average per Year: {stats_nme['average']}")
                print(
                    f"  Minimum: {stats_nme['min']} "
                    f"(Year {stats_nme['min_year']})"
                )
                print(
                    f"  Maximum: {stats_nme['max']} "
                    f"(Year {stats_nme['max_year']})"
                )
                print("=" * 70)

                # Save results to files
                logger.info(
                    f"Saving results to {RESULTS_DIR}..."
                )
                save_approval_data(
                    all_approvals,
                    nme_approvals,
                    RESULTS_DIR,
                )
                save_approved_drugs(
                    all_drugs,
                    nme_drugs,
                    RESULTS_DIR,
                )
                create_approval_plots(
                    all_approvals,
                    nme_approvals,
                    RESULTS_DIR,
                )
                create_company_plots(RESULTS_DIR)

                # Adverse event summaries
                logger.info("Fetching adverse event summaries...")
                events_by_year = client.get_adverse_events_by_year()
                top_drugs = client.get_top_reported_drugs(limit=50)
                top_reactions = client.get_top_reactions(limit=50)

                save_adverse_events_data(
                    events_by_year,
                    top_drugs,
                    top_reactions,
                    RESULTS_DIR,
                )

                # Create plots for adverse event summaries
                create_adverse_event_plots(
                    events_by_year,
                    top_drugs,
                    top_reactions,
                    RESULTS_DIR,
                    top_n=25,
                )

                print(f"\n✓ Results saved to: {RESULTS_DIR}")
                print(f"  - CSV files with approval statistics")
                print(f"  - CSV files with drug names and details")
                print(f"  - PNG plots with visualizations")
                print("\n")
            else:
                logger.warning("No approval data retrieved from FDA API")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
