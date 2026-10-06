import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """Shared HTTP behavior for the source-specific scrapers."""

    def __init__(
        self,
        delay: float = 0.5,
        timeout: float = 10.0,
        user_agent: str = "RealisierenScrapingAssignment/1.0 (learning project)",
    ):
        self.delay = delay
        self.timeout = timeout
        self.session = self._create_session(user_agent)

    @staticmethod
    def _create_session(user_agent: str) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml",
        })

        retries = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get(self, url: str) -> Optional[requests.Response]:
        """Fetch a page with retries. Returns None after a final failure."""
        try:
            logger.info("Requesting: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            logger.error("Request failed for %s: %s", url, exc)
            return None
        finally:
            # Keep a polite delay between requests, including failed requests.
            time.sleep(self.delay)

    def close(self) -> None:
        self.session.close()
