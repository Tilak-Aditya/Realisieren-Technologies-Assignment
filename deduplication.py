import hashlib
import re
from typing import Any


def _normalize_key_part(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def make_fingerprint(record: dict[str, Any]) -> str:
    """
    Books: source + title.
    Quotes: source + author + first 50 chars of quote.
    """
    source = _normalize_key_part(record.get("source"))

    if record.get("source") == "Books to Scrape":
        key = f"{source} {_normalize_key_part(record.get('name_or_title'))}"
    else:
        author = _normalize_key_part(record.get("author"))
        quote = _normalize_key_part(record.get("name_or_title"))[:50]
        key = f"{source} {author} {quote}"

    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (unique_records, duplicate_records)."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []

    for record in records:
        fingerprint = make_fingerprint(record)

        if fingerprint in seen:
            duplicates.append(record)
        else:
            unique.append(record)
            seen.add(fingerprint)

    return unique, duplicates
