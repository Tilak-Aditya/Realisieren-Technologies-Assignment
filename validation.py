from math import isfinite
from typing import Any

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record: dict[str, Any]) -> list[str]:
    """Return validation problem codes. Empty list means valid."""
    problems: list[str] = []

    if record.get("source") not in VALID_SOURCES:
        problems.append("unknown_source")

    if not record.get("name_or_title"):
        problems.append("missing_name")

    source_url = str(record.get("source_url") or "")
    if not source_url.startswith(("http://", "https://")):
        problems.append("invalid_url")

    price = record.get("price")
    if price is not None:
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            problems.append("invalid_price")
        elif not isfinite(float(price)) or float(price) < 0:
            problems.append("invalid_price")

    rating = record.get("rating")
    if rating is not None and (
        isinstance(rating, bool)
        or not isinstance(rating, int)
        or rating not in {1, 2, 3, 4, 5}
    ):
        problems.append("invalid_rating")

    # Source-specific checks.
    if record.get("source") == "Quotes to Scrape" and not record.get("author"):
        problems.append("missing_author")

    return problems
