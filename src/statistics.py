"""Statistics module for analyzing drug approval data."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_statistics(data: dict[int, int]) -> str:
    """Format statistics data for display.

    Args:
        data: Dictionary mapping year to count.

    Returns:
        Formatted string representation of the statistics.
    """
    if not data:
        return "No data available"

    sorted_years = sorted(data.keys())
    output_lines = []

    for year in sorted_years:
        count = data[year]
        output_lines.append(f"  {year}: {count:,}")

    return "\n".join(output_lines)


def calculate_summary_stats(data: dict[int, int]) -> dict[str, Any]:
    """Calculate summary statistics from approval data.

    Args:
        data: Dictionary mapping year to count.

    Returns:
        Dictionary containing summary statistics.
    """
    if not data:
        return {
            "total": 0,
            "average": 0,
            "min": 0,
            "max": 0,
            "min_year": None,
            "max_year": None,
        }

    counts = list(data.values())
    total = sum(counts)
    average = total / len(counts) if counts else 0
    min_count = min(counts)
    max_count = max(counts)

    min_year = [year for year, count in data.items() if count == min_count][0]
    max_year = [year for year, count in data.items() if count == max_count][0]

    return {
        "total": total,
        "average": round(average, 2),
        "min": min_count,
        "max": max_count,
        "min_year": min_year,
        "max_year": max_year,
    }
