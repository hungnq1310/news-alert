"""Keyword matching logic for news articles."""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of keyword matching."""

    matched: bool
    symbols: list[str]
    topics: list[str]
    event_types: list[str]

    def has_matches(self) -> bool:
        """Check if any keywords were matched."""
        return bool(self.symbols or self.topics or self.event_types)


class KeywordMatcher:
    """Matches news articles against watched keywords."""

    def __init__(
        self,
        symbols: list[str],
        topics: list[str],
        event_types: list[str],
    ):
        """Initialize matcher with watched keywords.

        Args:
            symbols: List of ticker symbols to watch
            topics: List of topics to watch
            event_types: List of event types to watch
        """
        self.symbols = set(s.lower() for s in symbols)
        self.topics = set(t.lower() for t in topics)
        self.event_types = set(e.lower() for e in event_types)

    def match(self, article: dict[str, Any]) -> MatchResult:
        """Check if article matches any watched keywords.

        Args:
            article: News article dictionary

        Returns:
            MatchResult containing all matched keywords.
        """
        matched_symbols = self._match_symbols(article)
        matched_topics = self._match_topics(article)
        matched_event_types = self._match_event_types(article)

        result = MatchResult(
            matched=bool(matched_symbols or matched_topics or matched_event_types),
            symbols=matched_symbols,
            topics=matched_topics,
            event_types=matched_event_types,
        )

        if result.has_matches():
            logger.debug(
                f"Article matched: symbols={matched_symbols}, "
                f"topics={matched_topics}, events={matched_event_types}"
            )

        return result

    def _match_symbols(self, article: dict[str, Any]) -> list[str]:
        """Match against ticker symbols.

        Checks companies_mentioned[].ticker and symbol_code fields.
        """
        matched = []

        # Check companies_mentioned array
        for company in article.get("companies_mentioned", []):
            ticker = company.get("ticker", "")
            if ticker and ticker.lower() in self.symbols:
                matched.append(ticker)

        # Check symbol_code field
        symbol_code = article.get("symbol_code", "")
        if symbol_code and symbol_code.lower() in self.symbols:
            if symbol_code not in matched:
                matched.append(symbol_code)

        return matched

    def _match_topics(self, article: dict[str, Any]) -> list[str]:
        """Match against classification topics."""
        matched = []

        classification = article.get("classification", {})
        for topic in classification.get("topics", []):
            if isinstance(topic, str) and topic.lower() in self.topics:
                matched.append(topic)

        return matched

    def _match_event_types(self, article: dict[str, Any]) -> list[str]:
        """Match against extracted event types."""
        matched = []

        for event in article.get("events_extracted", []):
            event_type = event.get("event_type", "")
            if event_type and event_type.lower() in self.event_types:
                matched.append(event_type)

        return matched
