import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    START_URL = "https://quotes.toscrape.com/"
    SOURCE = "Quotes to Scrape"

    def scrape(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        url = self.START_URL
        page_number = 1

        while url:
            logger.info("Quotes page %d: %s", page_number, url)
            response = self.get(url)

            if response is None:
                logger.error(
                    "Stopping Quotes to Scrape after page %d because the page failed.",
                    page_number,
                )
                break

            soup = BeautifulSoup(response.text, "lxml")
            quote_blocks = soup.select("div.quote")

            if not quote_blocks:
                logger.warning("No quote records found on %s", url)

            for index, block in enumerate(quote_blocks, start=1):
                try:
                    record = self._parse_quote(block, url)
                    records.append(record)
                except Exception:
                    logger.exception(
                        "Could not parse quote %d on page %d (%s). Skipping record.",
                        index,
                        page_number,
                        url,
                    )

            next_link = soup.select_one("li.next > a")
            if next_link and next_link.get("href"):
                url = urljoin(url, next_link["href"])
                page_number += 1
            else:
                url = None

        logger.info("Quotes scraper collected %d raw records.", len(records))
        return records

    def _parse_quote(self, block, page_url: str) -> dict[str, Any]:
        text = block.select_one("span.text")
        author = block.select_one("small.author")
        author_link = block.select_one('a[href^="/author/"]')
        tags = block.select("a.tag")

        if text is None:
            raise ValueError("Quote text element is missing.")
        if author is None:
            raise ValueError("Quote author element is missing.")

        author_url = (
            urljoin(page_url, author_link["href"])
            if author_link and author_link.get("href")
            else page_url
        )

        return {
            "source": self.SOURCE,
            # Documented choice: use the page where the quote appeared.
            "source_url": page_url,
            "name_or_title_raw": text.get_text(" ", strip=True),
            "category_raw": None,
            "price_raw": None,
            "rating_raw": None,
            "author_raw": author.get_text(" ", strip=True),
            "tags_raw": [tag.get_text(" ", strip=True) for tag in tags],
            "description_raw": None,
            "author_url_raw": author_url,
        }
