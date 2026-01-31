"""Integration tests for adverse-event endpoints against the live FDA API.

These tests call the real openFDA endpoints and are marked with the `integration`
pytest marker. Run them explicitly with:

    pytest -m integration

Note: These tests may be slower and are subject to public API rate limits.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest

# Project test style imports (for type-checking in tests)
from _pytest.capture import CaptureFixture
from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock.plugin import MockerFixture

# Ensure src is importable
sys.path.insert(0, "src")

from fda_client import FDAClient  # type: ignore


@pytest.mark.integration
def test_get_adverse_events_by_year_live() -> None:
    """Integration: get adverse events aggregated by year from openFDA.

    Verifies that the method returns a non-empty dict of integer year -> count
    pairs and that at least one recent year (>= 2021) is present.
    """
    client = FDAClient()
    with client:
        events = client.get_adverse_events_by_year()

    assert isinstance(events, dict)
    assert events, "Expected non-empty events-by-year dictionary"
    assert all(isinstance(y, int) and isinstance(c, int) for y, c in events.items())
    assert max(events.keys()) >= 2021, "Expected recent years in the results"


@pytest.mark.integration
def test_get_top_reported_drugs_live() -> None:
    """Integration: get top reported medicinal products from openFDA.

    Verifies that the result is a non-empty list of dicts with `term` and `count`.
    """
    client = FDAClient()
    with client:
        top = client.get_top_reported_drugs(limit=10)

    assert isinstance(top, list)
    assert top, "Expected at least one top-reported drug"
    assert all(isinstance(t, dict) and "term" in t and "count" in t for t in top)
    assert all(isinstance(t["term"], str) and isinstance(t["count"], int) for t in top)


@pytest.mark.integration
def test_get_top_reactions_live() -> None:
    """Integration: get top reaction MedDRA PTs from openFDA.

    Verifies that the result is a non-empty list of dicts with `term` and `count`.
    """
    client = FDAClient()
    with client:
        top = client.get_top_reactions(limit=10)

    assert isinstance(top, list)
    assert top, "Expected at least one top reaction"
    assert all(isinstance(t, dict) and "term" in t and "count" in t for t in top)
    assert all(isinstance(t["term"], str) and isinstance(t["count"], int) for t in top)
