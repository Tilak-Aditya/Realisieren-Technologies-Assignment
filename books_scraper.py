import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BooksScraper(BaseScraper):
    START_URL = "https://books.toscrape.com/"
    SOURCE = "Books to Scrape"

    def scrape(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        url = self.START_URL
        page_number = 1

        while url:
            logger.info("Books page %d: %s", page_number, url)
            response = self.get(url)

            if response is None:
                logger.error(
                    "Stopping Books to Scrape after page %d because the page failed.",
                    page_number,
                )
                break

            soup = BeautifulSoup(response.text, "lxml")
            articles = soup.select("article.product_pod")

            if not articles:
                logger.warning("No book records found on %s", url)

            for index, article in enumerate(articles, start=1):
                try:
                    record = self._parse_book(article, url)
                    records.append(record)
                except Exception:
                    logger.exception(
                        "Could not parse book %d on page %d (%s). Skipping record.",
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

        logger.info("Books scraper collected %d raw records.", len(records))
        return records

    def _parse_book(self, article, page_url: str) -> dict[str, Any]:
        link = article.select_one("h3 > a")
        price = article.select_one("p.price_color")
        rating = article.select_one("p.star-rating")
        availability = article.select_one("p.instock.availability")

        if link is None:
            raise ValueError("Book title/link element is missing.")

        href = link.get("href")
        if not href:
            raise ValueError("Book URL is missing.")

        rating_classes = rating.get("class", []) if rating else []
        rating_raw = " ".join(rating_classes)

        return {
            "source": self.SOURCE,
            "source_url": urljoin(page_url, href),
            "name_or_title_raw": link.get("title") or link.get_text(" ", strip=True),
            "category_raw": None,
            "price_raw": price.get_text(" ", strip=True) if price else None,
            "rating_raw": rating_raw,
            "author_raw": None,
            "tags_raw": None,
            "description_raw": None,
            "availability_raw": availability.get_text(" ", strip=True)
            if availability
            else None,
        }
