# AI_USAGE.md

## AI Tool Used

**Tool:** ChatGPT

AI assistance was used because the assignment explicitly permits AI coding assistants.

## What AI Was Used For

AI assistance was used for:

- Designing the ETL project structure.
- Translating the assignment requirements into Python modules.
- Designing the shared Requests session and retry behavior.
- Drafting BeautifulSoup selectors and pagination logic.
- Designing cleaning functions.
- Designing validation rules and rejection reasons.
- Designing SHA-256 duplicate fingerprints.
- Creating unit tests.
- Drafting README documentation.
- Reviewing edge cases and error handling.

## Representative Prompts

Examples of prompts used during development:

1. "Based on this Python web scraping assignment, create a clean project structure with separate scraper, processing, test, and documentation files."

2. "Implement dynamic pagination for Books to Scrape and Quotes to Scrape using BeautifulSoup and urljoin without hard-coding page counts."

3. "Create reusable cleaning functions for whitespace, currency prices, word-based ratings, tags, and URLs."

4. "Create unit tests for cleaning, validation, and duplicate detection, including case and whitespace differences."

5. "Review the pipeline for missing HTML elements, failed HTTP requests, duplicate records, and summary-count reconciliation."

## AI-Assisted Areas

The following areas were AI-assisted:

- Initial project architecture.
- HTTP retry/session design.
- Source scraper implementation.
- Cleaning and validation implementation.
- Deduplication implementation.
- Unit test generation.
- Documentation drafting.

## Human Review / Important Decisions

The implementation was reviewed against the assignment requirements.

Important design decisions include:

1. **Requests + BeautifulSoup**
   - Chosen because both websites are server-rendered practice sites.
   - A browser automation framework is unnecessary for the required pages.

2. **Dynamic pagination**
   - The implementation follows `li.next > a`.
   - Page numbers are not hard-coded.

3. **Book category/description**
   - The listing page does not provide these fields.
   - Instead of making approximately 1,000 additional detail-page requests or inventing values, the final dataset leaves these fields empty and documents the limitation.

4. **Duplicate removal**
   - Duplicates are removed from the final dataset.
   - The number removed is still reported.

5. **Failure isolation**
   - A failure in one source does not stop the other source.
   - Individual malformed records are skipped and logged.

6. **Quote source URL**
   - The URL of the page where the quote appeared is used as `source_url`.

## Possible AI-Generated Issues Checked

The final implementation was reviewed for common problems such as:

- Hard-coded page counts.
- Missing `None` checks around BeautifulSoup selectors.
- Relative URLs not being converted to absolute URLs.
- Rating classes being treated as plain text incorrectly.
- Duplicate logic failing because of case or whitespace differences.
- Invalid values reaching the final CSV.
- One failed source stopping the entire program.
- Summary counts not matching final output.

## Verification

Run unit tests:

```bash
pytest -q
```

Run the complete pipeline:

```bash
python main.py
```

Then verify:

- `output/final_dataset.csv` exists.
- `output/summary_report.json` exists.
- `logs/scraper.log` exists.
- Both source names appear in the CSV.
- Final CSV row count matches `final_record_count`.
- Ratings are within 1–5 when present.
- Prices are numeric when present.
- Rejected and duplicate records are reflected in the summary.

## Candidate Responsibility

AI-generated code is not treated as automatically correct. The candidate is responsible for reviewing, testing, understanding, and being able to explain the submitted implementation.
