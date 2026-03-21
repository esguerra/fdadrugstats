"""FDA API client for retrieving drug approval data."""

import logging
from typing import Any
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class FDAClient:
    """Client for interacting with FDA API endpoints."""

    BASE_URL = "https://api.fda.gov/drug/event.json"
    APPROVAL_BASE_URL = "https://api.fda.gov/drug/drugsfda.json"

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize FDA API client.

        Args:
            api_key: Optional FDA API key for increased rate limits.
        """
        # Prefer explicit parameter, otherwise read from the FDA_API_KEY
        # environment variable. Do not hardcode API keys in source.
        import os

        self.api_key = api_key or os.getenv("FDA_API_KEY")
        self.session = requests.Session()
        # Set a sensible default User-Agent and Accept header so the
        # OpenFDA service can identify callers. Including a repo URL
        # or contact helps reduce the chance of being blocked.
        self.session.headers.update(
            {
                "User-Agent": "fdadrugstats/1.0 (https://github.com/esguerra/fdadrugstats)",
                "Accept": "application/json",
            }
        )

    def _make_request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make a request to FDA API.

        Args:
            url: The endpoint URL.
            params: Query parameters for the request.

        Returns:
            JSON response from the API.

        Raises:
            requests.RequestException: If the request fails.
        """
        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Provide additional guidance for 403 responses which often
            # indicate missing/insufficient API keys, rate limits, or that
            # the caller was blocked. The HTTPError may carry a response
            # object we can inspect for status code.
            status = None
            try:
                status = e.response.status_code  # type: ignore[attr-defined]
            except Exception:
                status = None

            if status == 403:
                logger.error(
                    "Received 403 Forbidden from FDA API — this may be due to missing/insufficient "
                    "API key, rate limits, or blocked requests. Ensure you've set `FDA_API_KEY` as a "
                    "secret and include a valid User-Agent header. See https://open.fda.gov/ for details."
                )

            logger.error(f"FDA API request failed: {e}")
            raise

    def get_drug_approvals_by_year(
        self, include_all_types: bool = True
    ) -> dict[int, int]:
        """Retrieve the number of drug approvals per year.

        Counts new molecular entities (NME) and related drug approvals
        as tracked by the FDA's Center for Drug Evaluation and Research
        (CDER). Counts based on the original (ORIG) approval date, not
        supplemental updates.

        Args:
            include_all_types: If True, counts Type 1-4 and Type 10
                submissions. If False, counts only Type 1 (New Molecular
                Entity) submissions, matching official FDA counts more
                closely.

        Note: The FDA API limits pagination to skip <= 25000, so we can
        retrieve approximately the first 26,000 most recent drug records.

        Returns:
            Dictionary mapping year to count of approvals.
        """
        approvals_by_year: dict[int, int] = {}

        try:
            # FDA API limits results to 1000 per request
            # and skip parameter to maximum 25000
            limit = 1000
            skip = 0
            max_skip = 25000  # FDA API limit
            total_processed = 0

            while skip <= max_skip:
                # Use the drugsfda API endpoint with pagination
                params = {
                    "limit": limit,
                    "skip": skip,
                }

                response = self._make_request(self.APPROVAL_BASE_URL, params)

                if "results" not in response or not response["results"]:
                    logger.info("No more results from FDA API")
                    break

                results = response["results"]
                logger.debug(
                    f"Processing {len(results)} drugs "
                    f"(skip={skip}, limit={limit})"
                )

                for drug in results:
                    # Extract approval year from original submissions
                    # Count only ORIG (original) submissions with specific
                    # submission classes that represent new drug approvals
                    if "submissions" in drug:
                        # Find the ORIG submission
                        for submission in drug["submissions"]:
                            if submission.get("submission_type") == "ORIG":
                                class_desc = submission.get(
                                    "submission_class_code_description", ""
                                )
                                status = submission.get(
                                    "submission_status", ""
                                )

                                # Determine which types to count
                                should_count = False
                                if include_all_types:
                                    # Count Type 1-4 and Type 10
                                    should_count = (
                                        status == "AP"
                                        and (
                                            "Type 1 - New Molecular Entity"
                                            in class_desc
                                            or "Type 2 - New Active Ingredient"
                                            in class_desc
                                            or "Type 3 - New Dosage Form"
                                            in class_desc
                                            or "Type 4 - New Combination"
                                            in class_desc
                                            or "Type 10 - New Indication"
                                            in class_desc
                                        )
                                    )
                                else:
                                    # Count only Type 1 (NME)
                                    should_count = (
                                        status == "AP"
                                        and "Type 1 - New Molecular Entity"
                                        in class_desc
                                    )

                                if should_count:
                                    submission_date = submission.get(
                                        "submission_status_date", ""
                                    )
                                    if submission_date and len(
                                        submission_date
                                    ) >= 4:
                                        try:
                                            year = int(
                                                submission_date[:4]
                                            )
                                            approvals_by_year[year] = (
                                                approvals_by_year.get(
                                                    year, 0
                                                )
                                                + 1
                                            )
                                        except (ValueError, IndexError):
                                            logger.debug(
                                                f"Could not parse date: "
                                                f"{submission_date}"
                                            )
                                # Only process first ORIG submission
                                break

                total_processed += len(results)
                skip += limit

                # Stop if we've processed all available results
                if len(results) < limit:
                    break

            type_str = (
                "drug approvals (Type 1-4, 10)"
                if include_all_types
                else "new molecular entities (Type 1)"
            )
            logger.info(
                f"Successfully retrieved {total_processed} drugs with "
                f"{type_str} for {len(approvals_by_year)} years"
            )
            return approvals_by_year

        except Exception as e:
            logger.error(f"Error retrieving drug approvals: {e}")
            raise

    def get_adverse_events_by_year(self) -> dict[int, int]:
        """Retrieve the number of adverse events reported per year.

        This implementation uses the API's aggregation (`count=receivedate`) to
        obtain counts per report date and then aggregates them by year. This
        is more reliable and scalable than fetching raw event records.

        Returns:
            Dictionary mapping year to count of adverse events.
        """
        events_by_year: dict[int, int] = {}

        try:
            # Use the API's count aggregation on receivedate to obtain date-bucketed counts
            params = {
                "count": "receivedate",
                "limit": 1000,
            }

            response = self._make_request(self.BASE_URL, params)

            if "results" not in response or not response["results"]:
                logger.warning("No adverse event aggregates found in FDA API response")
                return events_by_year

            for entry in response["results"]:
                time = entry.get("time") or entry.get("term")
                count = entry.get("count", 0)
                if not time:
                    continue
                # time comes as YYYYMMDD strings; aggregate by year
                try:
                    year = int(str(time)[:4])
                    events_by_year[year] = events_by_year.get(year, 0) + int(count)
                except (ValueError, TypeError):
                    logger.debug(f"Could not parse time: {time}")

            logger.info(
                f"Successfully retrieved adverse event counts for {len(events_by_year)} years"
            )
            return dict(sorted(events_by_year.items()))

        except Exception as e:
            logger.error(f"Error retrieving adverse events by year: {e}")
            raise

    def get_top_reported_drugs(self, limit: int = 20) -> list[dict[str, int]]:
        """Return top reported medicinal products in adverse event reports.

        Args:
            limit: Number of top terms to return.

        Returns:
            List of dicts with keys `term` and `count`.
        """
        params = {"count": "patient.drug.medicinalproduct.exact", "limit": limit}
        resp = self._make_request(self.BASE_URL, params)
        return resp.get("results", [])

    def get_top_reactions(self, limit: int = 20) -> list[dict[str, int]]:
        """Return top reported reaction MedDRA Preferred Terms (PT).

        Args:
            limit: Number of top reactions to return.

        Returns:
            List of dicts with keys `term` and `count`.
        """
        params = {"count": "patient.reaction.reactionmeddrapt.exact", "limit": limit}
        resp = self._make_request(self.BASE_URL, params)
        return resp.get("results", [])

    def get_adverse_event_counts(self, count_field: str, limit: int = 100) -> list[dict[str, int]]:
        """Generic helper to get aggregated counts for a given field using API count.

        Args:
            count_field: Field to aggregate on (e.g., 'companynumb', 'patient.reaction.reactionmeddrapt.exact').
            limit: Max number of buckets to retrieve.

        Returns:
            List of aggregation results as returned by the API.
        """
        params = {"count": count_field, "limit": limit}
        resp = self._make_request(self.BASE_URL, params)
        return resp.get("results", [])

    def get_approved_drugs(
        self, include_all_types: bool = True
    ) -> list[dict[str, Any]]:
        """Retrieve list of approved drugs with details.

        Args:
            include_all_types: If True, includes Type 1-4 and Type 10
                submissions. If False, includes only Type 1 (NME).

        Returns:
            List of dictionaries containing drug information with keys:
            - application_number: FDA application number
            - brand_name: Brand name(s) of the drug
            - generic_name: Generic name(s) of the drug
            - company: Manufacturer company name
            - approval_year: Year of approval
            - submission_type: Type of submission (ORIG, SUPPL, etc.)
            - submission_class: Class of submission
        """
        drugs_list: list[dict[str, Any]] = []

        try:
            limit = 1000
            skip = 0
            max_skip = 25000

            while skip <= max_skip:
                params = {
                    "limit": limit,
                    "skip": skip,
                }

                response = self._make_request(
                    self.APPROVAL_BASE_URL, params
                )

                if "results" not in response or not response["results"]:
                    logger.info("No more results from FDA API")
                    break

                results = response["results"]
                logger.debug(
                    f"Processing {len(results)} drugs "
                    f"(skip={skip}, limit={limit})"
                )

                for drug in results:
                    if "submissions" in drug:
                        for submission in drug["submissions"]:
                            if submission.get("submission_type") == "ORIG":
                                class_desc = submission.get(
                                    "submission_class_code_description", ""
                                )
                                status = submission.get(
                                    "submission_status", ""
                                )

                                # Determine if should include
                                should_include = False
                                if include_all_types:
                                    should_include = (
                                        status == "AP"
                                        and (
                                            "Type 1 - New Molecular Entity"
                                            in class_desc
                                            or "Type 2 - New Active Ingredient"
                                            in class_desc
                                            or "Type 3 - New Dosage Form"
                                            in class_desc
                                            or "Type 4 - New Combination"
                                            in class_desc
                                            or "Type 10 - New Indication"
                                            in class_desc
                                        )
                                    )
                                else:
                                    should_include = (
                                        status == "AP"
                                        and "Type 1 - New Molecular Entity"
                                        in class_desc
                                    )

                                if should_include:
                                    submission_date = submission.get(
                                        "submission_status_date", ""
                                    )
                                    if submission_date and len(
                                        submission_date
                                    ) >= 4:
                                        try:
                                            year = int(
                                                submission_date[:4]
                                            )

                                            # Extract drug names
                                            openfda = drug.get(
                                                "openfda", {}
                                            )
                                            brand_names = openfda.get(
                                                "brand_name", []
                                            )
                                            generic_names = openfda.get(
                                                "generic_name", []
                                            )
                                            manufacturers = openfda.get(
                                                "manufacturer_name", []
                                            )

                                            brand_name = (
                                                brand_names[0]
                                                if brand_names
                                                else "N/A"
                                            )
                                            generic_name = (
                                                generic_names[0]
                                                if generic_names
                                                else "N/A"
                                            )
                                            company = (
                                                manufacturers[0]
                                                if manufacturers
                                                else "N/A"
                                            )

                                            drugs_list.append(
                                                {
                                                    "application_number": drug.get(
                                                        "application_number",
                                                        "N/A",
                                                    ),
                                                    "brand_name": brand_name,
                                                    "generic_name": generic_name,
                                                    "company": company,
                                                    "approval_year": year,
                                                    "submission_class": class_desc,
                                                }
                                            )
                                        except (ValueError, IndexError):
                                            logger.debug(
                                                f"Could not parse date: "
                                                f"{submission_date}"
                                            )
                                break

                skip += limit

                if len(results) < limit:
                    break

            logger.info(
                f"Successfully retrieved {len(drugs_list)} "
                f"approved drugs"
            )
            return drugs_list

        except Exception as e:
            logger.error(f"Error retrieving approved drugs: {e}")
            raise

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "FDAClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
