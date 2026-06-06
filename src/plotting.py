"""Plotting module for drug approval statistics."""

import logging
import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

logger = logging.getLogger(__name__)

plt.style.use("seaborn-v0_8-whitegrid")


def _thousands(x: float, _pos: int) -> str:
    """Format axis ticks with thousands separators."""
    return f"{int(x):,}"


def _finish_axes(ax: plt.Axes, grid_axis: str = "y") -> None:
    """Apply shared chart polish for static PNG fallbacks."""
    ax.grid(axis=grid_axis, alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(FuncFormatter(_thousands))


def _finish_horizontal_axes(ax: plt.Axes) -> None:
    """Apply shared polish for horizontal bar charts."""
    ax.grid(axis="x", alpha=0.25, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_formatter(FuncFormatter(_thousands))


def _wrap_labels(labels: list[Any], width: int = 34) -> list[str]:
    """Wrap long horizontal bar labels so PNGs remain readable."""
    return [textwrap.fill(str(label), width=width, break_long_words=False) for label in labels]


def create_approval_plots(
    all_approvals: dict[int, int],
    nme_approvals: dict[int, int],
    output_dir: Path,
) -> None:
    """Create and save plots for drug approval statistics.

    Args:
        all_approvals: Dictionary mapping year to all approval counts.
        nme_approvals: Dictionary mapping year to NME approval counts.
        output_dir: Directory to save plot images.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Plot 1: All Approvals
    years_all = sorted(all_approvals.keys())
    counts_all = [all_approvals[year] for year in years_all]

    axes[0].bar(years_all, counts_all, color="#2563eb", alpha=0.85, width=0.82)
    axes[0].set_xlabel("Year", fontsize=12)
    axes[0].set_ylabel("Number of Approvals", fontsize=12)
    axes[0].set_title(
        "FDA Drug Approvals by Year (Type 1-4, 10)",
        fontsize=14,
        fontweight="bold",
    )
    _finish_axes(axes[0])
    axes[0].set_xlim(years_all[0] - 1, years_all[-1] + 1)

    # Plot 2: NME Approvals
    years_nme = sorted(nme_approvals.keys())
    counts_nme = [nme_approvals[year] for year in years_nme]

    axes[1].bar(years_nme, counts_nme, color="#059669", alpha=0.85, width=0.82)
    axes[1].set_xlabel("Year", fontsize=12)
    axes[1].set_ylabel("Number of NME Approvals", fontsize=12)
    axes[1].set_title(
        "FDA New Molecular Entity (NME) Approvals by Year (Type 1)",
        fontsize=14,
        fontweight="bold",
    )
    _finish_axes(axes[1])
    axes[1].set_xlim(years_nme[0] - 1, years_nme[-1] + 1)

    plt.tight_layout()
    plot_path = output_dir / "drug_approvals.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    logger.info(f"Saved approval plots to {plot_path}")
    plt.close()

    # Create comparison plot for recent years
    fig, ax = plt.subplots(figsize=(14, 7))

    # Filter for recent years (last 15 years)
    recent_cutoff = max(years_all) - 15
    recent_years = sorted(
        set(years_all + years_nme).intersection(
            set(range(recent_cutoff, max(years_all) + 1))
        )
    )

    all_recent = [all_approvals.get(year, 0) for year in recent_years]
    nme_recent = [nme_approvals.get(year, 0) for year in recent_years]

    x = range(len(recent_years))
    width = 0.35

    ax.bar(
        [i - width / 2 for i in x],
        all_recent,
        width,
        label="All Approvals (Type 1-4, 10)",
        color="#2563eb",
        alpha=0.85,
    )
    ax.bar(
        [i + width / 2 for i in x],
        nme_recent,
        width,
        label="New Molecular Entities (Type 1)",
        color="#f97316",
        alpha=0.85,
    )

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Number of Approvals", fontsize=12)
    ax.set_title(
        "FDA Drug Approvals Comparison - Recent Years",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(recent_years, rotation=45)
    ax.legend(fontsize=11, frameon=False)
    _finish_axes(ax)

    plt.tight_layout()
    comparison_path = output_dir / "approvals_comparison_recent.png"
    plt.savefig(comparison_path, dpi=300, bbox_inches="tight")
    logger.info(f"Saved comparison plot to {comparison_path}")
    plt.close()


def save_approval_data(
    all_approvals: dict[int, int],
    nme_approvals: dict[int, int],
    output_dir: Path,
) -> None:
    """Save approval data to CSV files.

    Args:
        all_approvals: Dictionary mapping year to all approval counts.
        nme_approvals: Dictionary mapping year to NME approval counts.
        output_dir: Directory to save CSV files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create combined dataframe
    all_years = sorted(
        set(all_approvals.keys()).union(set(nme_approvals.keys()))
    )
    df = pd.DataFrame(
        {
            "Year": all_years,
            "All_Approvals_Type1to4_10": [
                all_approvals.get(year, 0) for year in all_years
            ],
            "NME_Approvals_Type1": [
                nme_approvals.get(year, 0) for year in all_years
            ],
        }
    )

    # Save to CSV
    csv_path = output_dir / "drug_approvals_by_year.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved approval data to {csv_path}")

    # Save individual CSV files
    all_df = pd.DataFrame(
        {
            "Year": sorted(all_approvals.keys()),
            "Count": [
                all_approvals[year]
                for year in sorted(all_approvals.keys())
            ],
        }
    )
    all_csv_path = output_dir / "all_approvals.csv"
    all_df.to_csv(all_csv_path, index=False)
    logger.info(f"Saved all approvals data to {all_csv_path}")

    nme_df = pd.DataFrame(
        {
            "Year": sorted(nme_approvals.keys()),
            "Count": [
                nme_approvals[year]
                for year in sorted(nme_approvals.keys())
            ],
        }
    )
    nme_csv_path = output_dir / "nme_approvals.csv"
    nme_df.to_csv(nme_csv_path, index=False)
    logger.info(f"Saved NME approvals data to {nme_csv_path}")


def save_approved_drugs(
    all_drugs: list[dict[str, Any]],
    nme_drugs: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    """Save approved drug names and details to CSV files.

    Args:
        all_drugs: List of all approved drugs with details.
        nme_drugs: List of NME approved drugs with details.
        output_dir: Directory to save CSV files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save all approved drugs
    if all_drugs:
        all_df = pd.DataFrame(all_drugs)
        all_df = all_df.sort_values("approval_year")
        all_drugs_path = output_dir / "approved_drugs_all.csv"
        all_df.to_csv(all_drugs_path, index=False)
        logger.info(f"Saved all approved drugs to {all_drugs_path}")

    # Save NME approved drugs
    if nme_drugs:
        nme_df = pd.DataFrame(nme_drugs)
        nme_df = nme_df.sort_values("approval_year")
        nme_drugs_path = output_dir / "approved_drugs_nme.csv"
        nme_df.to_csv(nme_drugs_path, index=False)
        logger.info(f"Saved NME approved drugs to {nme_drugs_path}")


def create_company_plots(output_dir: Path) -> None:
    """Create and save plots showing drugs per company.

    Args:
        output_dir: Directory containing approved_drugs_all.csv.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read the approved drugs data
    csv_path = output_dir / "approved_drugs_all.csv"
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # Group by company and count drugs
    drugs_per_company = (
        df.groupby("company").size().sort_values(ascending=False)
    )

    # Create plot for top 30 companies
    top_n = 30
    top_companies = drugs_per_company.head(top_n)

    fig, ax = plt.subplots(figsize=(14, 10))

    bars = ax.barh(range(len(top_companies)), top_companies.values,
                    color="#059669", alpha=0.9)

    # Color bars with a stable gradient (including the single-value case)
    min_count = top_companies.values.min()
    max_count = top_companies.values.max()
    if max_count == min_count:
        gradient_values = [0.65 for _ in top_companies.values]
    else:
        gradient_values = (
            (top_companies.values - min_count) / (max_count - min_count)
        )
    colors = plt.cm.viridis(gradient_values)
    for bar, color in zip(bars, colors):
        bar.set_color(color)

    ax.set_yticks(range(len(top_companies)))
    ax.set_yticklabels(_wrap_labels(list(top_companies.index)), fontsize=9)
    ax.set_xlabel("Number of Approved Drugs", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Top {top_n} Pharmaceutical Companies by Number of Approved Drugs",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.invert_yaxis()
    _finish_horizontal_axes(ax)

    # Add value labels on bars
    for i, v in enumerate(top_companies.values):
        ax.text(v + 0.5, i, f"{v:,}", va="center", fontsize=9)

    plt.tight_layout()
    plot_path = output_dir / "drugs_per_company_top30.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    logger.info(f"Saved company drugs plot to {plot_path}")
    plt.close()

    # Create plot for all companies (scatter/distribution)
    fig, ax = plt.subplots(figsize=(14, 8))

    # Create histogram of company sizes
    ax.hist(drugs_per_company.values, bins=50, color="#2563eb",
            alpha=0.75, edgecolor="white", linewidth=0.8)

    ax.set_xlabel("Number of Approved Drugs per Company", fontsize=12,
                  fontweight="bold")
    ax.set_ylabel("Number of Companies", fontsize=12, fontweight="bold")
    ax.set_title(
        "Distribution of Approved Drugs Across Pharmaceutical Companies",
        fontsize=14,
        fontweight="bold",
    )
    _finish_axes(ax)

    # Add statistics
    stats_text = (
        f"Total Companies: {len(drugs_per_company)}\n"
        f"Total Drugs: {drugs_per_company.sum()}\n"
        f"Mean: {drugs_per_company.mean():.1f}\n"
        f"Median: {drugs_per_company.median():.1f}\n"
        f"Max: {drugs_per_company.max()}"
    )
    ax.text(
        0.97,
        0.97,
        stats_text,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    dist_path = output_dir / "company_distribution.png"
    plt.savefig(dist_path, dpi=300, bbox_inches="tight")
    logger.info(f"Saved company distribution plot to {dist_path}")
    plt.close()


def create_adverse_event_plots(
    events_by_year: dict[int, int],
    top_drugs: list[dict[str, int]],
    top_reactions: list[dict[str, int]],
    output_dir: Path,
    top_n: int = 20,
) -> None:
    """Create plots for adverse event summaries.

    Args:
        events_by_year: Mapping year -> adverse event count.
        top_drugs: List of dicts with keys `term` and `count` for top drugs.
        top_reactions: List of dicts with keys `term` and `count` for top reactions.
        output_dir: Directory to save plots.
        top_n: Number of top items to plot for drugs/reactions.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Time series of adverse events by year
    if events_by_year:
        years = sorted(events_by_year.keys())
        counts = [events_by_year[y] for y in years]

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(years, counts, marker="o", color="#dc2626", linewidth=2.5)
        ax.fill_between(years, counts, color="#dc2626", alpha=0.12)
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Number of Reports", fontsize=12)
        ax.set_title("Adverse Event Reports by Year", fontsize=14, fontweight="bold")
        _finish_axes(ax)
        plt.tight_layout()
        path = output_dir / "adverse_events_by_year.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved adverse events time series to {path}")
        plt.close()

    # Top reported drugs bar chart
    if top_drugs:
        df_drugs = pd.DataFrame(top_drugs).head(top_n)
        fig, ax = plt.subplots(figsize=(12, max(6, top_n * 0.34)))
        y_pos = range(len(df_drugs))
        ax.barh(y_pos, df_drugs["count"], color="#7c3aed", alpha=0.9)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(_wrap_labels(df_drugs["term"].tolist()), fontsize=9)
        ax.set_xlabel("Number of Reports", fontsize=12)
        ax.set_title(f"Top {min(top_n, len(df_drugs))} Reported Drugs", fontsize=14, fontweight="bold")
        ax.invert_yaxis()
        _finish_horizontal_axes(ax)
        for i, v in enumerate(df_drugs["count"]):
            ax.text(v + max(df_drugs["count"]) * 0.01, i, f"{int(v):,}", va="center", fontsize=9)
        plt.tight_layout()
        path = output_dir / "top_reported_drugs.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved top reported drugs plot to {path}")
        plt.close()

    # Top reactions bar chart
    if top_reactions:
        df_rxn = pd.DataFrame(top_reactions).head(top_n)
        fig, ax = plt.subplots(figsize=(12, max(6, top_n * 0.34)))
        y_pos = range(len(df_rxn))
        ax.barh(y_pos, df_rxn["count"], color="#92400e", alpha=0.9)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(_wrap_labels(df_rxn["term"].tolist()), fontsize=9)
        ax.set_xlabel("Number of Reports", fontsize=12)
        ax.set_title(f"Top {min(top_n, len(df_rxn))} Reported Reactions", fontsize=14, fontweight="bold")
        ax.invert_yaxis()
        _finish_horizontal_axes(ax)
        for i, v in enumerate(df_rxn["count"]):
            ax.text(v + max(df_rxn["count"]) * 0.01, i, f"{int(v):,}", va="center", fontsize=9)
        plt.tight_layout()
        path = output_dir / "top_reactions.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved top reactions plot to {path}")
        plt.close()


def save_adverse_events_data(
    events_by_year: dict[int, int],
    top_drugs: list[dict[str, int]],
    top_reactions: list[dict[str, int]],
    output_dir: Path,
) -> None:
    """Save adverse events summaries to CSV files.

    Args:
        events_by_year: Dict mapping year to adverse event counts.
        top_drugs: List of dicts returned by API with keys `term` and `count`.
        top_reactions: List of dicts returned by API with keys `term` and `count`.
        output_dir: Directory to save CSV files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save events by year
    if events_by_year:
        df_year = pd.DataFrame(
            {
                "Year": sorted(events_by_year.keys()),
                "Count": [events_by_year[y] for y in sorted(events_by_year.keys())],
            }
        )
        year_path = output_dir / "adverse_events_by_year.csv"
        df_year.to_csv(year_path, index=False)
        logger.info(f"Saved adverse events per year to {year_path}")

    # Save top reported drugs
    if top_drugs:
        df_drugs = pd.DataFrame(top_drugs)
        df_drugs = df_drugs.rename(columns={"term": "Drug", "count": "Reports"})
        drugs_path = output_dir / "top_reported_drugs.csv"
        df_drugs.to_csv(drugs_path, index=False)
        logger.info(f"Saved top reported drugs to {drugs_path}")

    # Save top reactions
    if top_reactions:
        df_rxn = pd.DataFrame(top_reactions)
        df_rxn = df_rxn.rename(columns={"term": "Reaction", "count": "Reports"})
        rxn_path = output_dir / "top_reactions.csv"
        df_rxn.to_csv(rxn_path, index=False)
        logger.info(f"Saved top reactions to {rxn_path}")
