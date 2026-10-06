import csv
import json
import logging
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

CSV_FIELDS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
]

logger = logging.getLogger("scraping_assignment")


def configure_logging() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_PATH,
        mode="w",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def write_csv(records: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=CSV_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(records)

    logger.info("Wrote %d records to %s", len(records), CSV_PATH)


def write_summary(summary: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=4, ensure_ascii=False)

    logger.info("Wrote summary report to %s", SUMMARY_PATH)


def process_source(
    source_name: str,
    raw_records: list[dict[str, Any]],
    rejected_by_reason: Counter,
) -> list[dict[str, Any]]:
    """Clean and validate records from one source."""
    valid_records: list[dict[str, Any]] = []

    for raw in raw_records:
        # Store one consistent UTC timestamp for each record.
        raw["scraped_at"] = raw.get(
            "scraped_at",
            utc_now().isoformat(),
        )

        cleaned = clean_record(raw)
        problems = validate_record(cleaned)

        if problems:
            for reason in problems:
                rejected_by_reason[reason] += 1

            logger.warning(
                "Rejected %s record: reasons=%s name=%r",
                source_name,
                ",".join(problems),
                cleaned.get("name_or_title"),
            )
            continue

        valid_records.append(cleaned)

    logger.info(
        "%s: raw=%d, valid_after_cleaning_and_validation=%d",
        source_name,
        len(raw_records),
        len(valid_records),
    )
    return valid_records


def run() -> int:
    configure_logging()

    started_at = utc_now()
    start_monotonic = time.monotonic()

    logger.info("Starting multi-source scraping pipeline.")

    raw_by_source: dict[str, list[dict[str, Any]]] = {
        "Books to Scrape": [],
        "Quotes to Scrape": [],
    }

    scrapers = [
        ("Books to Scrape", BooksScraper(delay=0.5)),
        ("Quotes to Scrape", QuotesScraper(delay=0.5)),
    ]

    try:
        for source_name, scraper in scrapers:
            try:
                raw_by_source[source_name] = scraper.scrape()
            except Exception:
                # One source must not prevent the other source from running.
                logger.exception("Unexpected failure in %s scraper.", source_name)
            finally:
                scraper.close()
    finally:
        pass

    rejected_by_reason: Counter = Counter()
    cleaned_by_source: dict[str, list[dict[str, Any]]] = {}

    for source_name, raw_records in raw_by_source.items():
        cleaned_by_source[source_name] = process_source(
            source_name,
            raw_records,
            rejected_by_reason,
        )

    all_valid_records = [
        record
        for records in cleaned_by_source.values()
        for record in records
    ]

    unique_records, duplicate_records = find_duplicates(all_valid_records)

    for duplicate in duplicate_records:
        logger.warning(
            "Duplicate removed: source=%s name=%r",
            duplicate.get("source"),
            duplicate.get("name_or_title"),
        )

    finished_at = utc_now()
    duration = round(time.monotonic() - start_monotonic, 3)

    write_csv(unique_records)

    final_counts = {
        source: sum(1 for record in unique_records if record["source"] == source)
        for source in raw_by_source
    }

    cleaned_counts = {
        source: len(records)
        for source, records in cleaned_by_source.items()
    }

    summary = {
        "project": "Multi-Source Web Scraping & Data Consolidation",
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": duration,
        "sources": {
            source: {
                "raw_records_collected": len(raw_by_source[source]),
                "records_after_cleaning_and_validation": cleaned_counts[source],
                "duplicates_removed": sum(
                    1
                    for record in duplicate_records
                    if record.get("source") == source
                ),
                "final_records": final_counts[source],
            }
            for source in raw_by_source
        },
        "rejected_records_total": sum(rejected_by_reason.values()),
        "rejected_by_reason": dict(sorted(rejected_by_reason.items())),
        "duplicates_detected": len(duplicate_records),
        "final_record_count": len(unique_records),
        "outputs": {
            "csv": str(CSV_PATH.relative_to(BASE_DIR)),
            "summary": str(SUMMARY_PATH.relative_to(BASE_DIR)),
            "log": str(LOG_PATH.relative_to(BASE_DIR)),
        },
    }

    write_summary(summary)

    logger.info(
        "Pipeline complete: final_records=%d duplicates=%d rejected=%d duration=%ss",
        len(unique_records),
        len(duplicate_records),
        sum(rejected_by_reason.values()),
        duration,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
