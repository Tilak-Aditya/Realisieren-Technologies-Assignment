import re
from typing import Any
from urllib.parse import urlparse

RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def clean_text(value: Any) -> str | None:
    """Normalize whitespace, including non-breaking spaces."""
    if value is None:
        return None

    text = str(value).replace("\xa0", " ")
    text = " ".join(text.split())
    return text or None


def strip_quotes(value: Any) -> str | None:
    """Remove the common curly quotation marks used by Quotes to Scrape."""
    text = clean_text(value)
    if not text:
        return None

    quote_pairs = [
        ("“", "”"),
        ("‘", "’"),
        ('"', '"'),
        ("'", "'"),
    ]

    for opening, closing in quote_pairs:
        if text.startswith(opening) and text.endswith(closing) and len(text) >= 2:
            text = text[1:-1].strip()
            break

    return text or None


def clean_price(raw: Any) -> float | None:
    """Extract a non-negative decimal number from a price string."""
    if raw is None:
        return None

    text = clean_text(raw)
    if not text:
        return None

    match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", text.replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(raw: Any) -> int | None:
    """Convert a word-based star rating such as 'Three' to an integer."""
    if raw is None:
        return None

    for word in str(raw).lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]

    return None


def clean_tags(raw: Any) -> str | None:
    """Lowercase, normalize, sort and join quote tags."""
    if raw is None:
        return None

    if isinstance(raw, str):
        values = [part.strip() for part in raw.split(";")]
    else:
        values = [str(item) for item in raw]

    tags = {
        clean_text(value).lower()
        for value in values
        if clean_text(value)
    }

    return ";".join(sorted(tags)) or None


def normalize_url(value: Any) -> str | None:
    """Return a cleaned absolute HTTP(S) URL, or None."""
    text = clean_text(value)
    if not text:
        return None

    parsed = urlparse(text)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return text

    return None


def clean_record(raw: dict[str, Any]) -> dict[str, Any]:
    """Convert a raw scraper record into the common output schema."""
    return {
        "source": clean_text(raw.get("source")),
        "source_url": normalize_url(raw.get("source_url")),
        "name_or_title": (
            strip_quotes(raw.get("name_or_title_raw"))
            if raw.get("source") == "Quotes to Scrape"
            else clean_text(raw.get("name_or_title_raw"))
        ),
        "category": clean_text(raw.get("category_raw")),
        "price": clean_price(raw.get("price_raw")),
        "rating": clean_rating(raw.get("rating_raw")),
        "author": clean_text(raw.get("author_raw")),
        "tags": clean_tags(raw.get("tags_raw")),
        "description": clean_text(raw.get("description_raw")),
        "scraped_at": raw.get("scraped_at"),
    }
