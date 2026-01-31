"""REST API client for fetching financial news."""

import logging
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)


class NewsAPIClient:
    """Client for fetching news articles from the financial API."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize API client.

        Args:
            base_url: Base URL of the API (e.g., http://localhost:8005/api/v3)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def get_news(
        self,
        start_timestamp_ms: int | None = None,
        end_timestamp_ms: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Fetch news articles from the API.

        Args:
            start_timestamp_ms: Start timestamp in milliseconds since epoch
            end_timestamp_ms: End timestamp in milliseconds since epoch
            limit: Maximum number of articles to fetch

        Returns:
            List of news article dictionaries.
        """
        params: dict[str, str | int] = {"limit": limit}

        if start_timestamp_ms is not None:
            params["start"] = start_timestamp_ms
        if end_timestamp_ms is not None:
            params["end"] = end_timestamp_ms

        try:
            url = f"{self.base_url}/news"
            logger.debug(f"Fetching news from {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, dict):
                return data.get("data", data.get("articles", []))
            return data if isinstance(data, list) else []

        except requests.RequestException as e:
            logger.error(f"Failed to fetch news: {e}")
            return []

    def close(self):
        """Close the session."""
        self.session.close()
