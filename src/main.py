"""Main application loop for the news alert system."""

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .api_client import NewsAPIClient
from .config import Config
from .matcher import KeywordMatcher
from .telegram import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# State file path - support environment variable for Docker
if os.getenv("STATE_FILE"):
    STATE_FILE = Path(os.getenv("STATE_FILE"))
else:
    STATE_FILE = Path(__file__).parent.parent / "state.json"

# Ensure state directory exists
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


class StateManager:
    """Manages persistent state for the application."""

    MAX_PROCESSED_IDS = 1000  # Keep last 1000 processed article IDs

    def __init__(self, state_file: Path = STATE_FILE):
        """Initialize state manager.

        Args:
            state_file: Path to state.json file
        """
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Load state from file.

        Returns:
            State dictionary with last_checked_at timestamp and processed IDs.
        """
        default_state = {
            "last_checked_at": None,
            "processed_article_ids": []
        }

        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    loaded = json.load(f)
                    # Merge with default to handle migration
                    for key, value in default_state.items():
                        if key not in loaded:
                            loaded[key] = value
                    return loaded
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load state file: {e}. Starting fresh.")

        return default_state

    def save_state(self):
        """Save current state to file."""
        # Ensure required fields exist before saving
        if "processed_article_ids" not in self.state:
            self.state["processed_article_ids"] = []

        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save state: {e}")

    @property
    def last_checked_at(self) -> int | None:
        """Get last checked timestamp in milliseconds."""
        return self.state.get("last_checked_at")

    def update_last_checked(self, timestamp_ms: int):
        """Update last checked timestamp.

        Args:
            timestamp_ms: Timestamp in milliseconds since epoch
        """
        self.state["last_checked_at"] = timestamp_ms
        self.save_state()

    def is_article_processed(self, article_id: str) -> bool:
        """Check if an article has already been processed.

        Args:
            article_id: Unique article identifier

        Returns:
            True if article was already processed, False otherwise.
        """
        return article_id in self.state.get("processed_article_ids", [])

    def mark_article_processed(self, article_id: str):
        """Mark an article as processed.

        Args:
            article_id: Unique article identifier
        """
        if "processed_article_ids" not in self.state:
            self.state["processed_article_ids"] = []

        processed_ids = self.state["processed_article_ids"]

        # Only add if not already present
        if article_id not in processed_ids:
            processed_ids.append(article_id)

            # Keep only the most recent IDs to prevent unbounded growth
            if len(processed_ids) > self.MAX_PROCESSED_IDS:
                self.state["processed_article_ids"] = processed_ids[-self.MAX_PROCESSED_IDS:]

            self.save_state()


class NewsAlertApp:
    """Main application for news alert system."""

    def __init__(self, config: Config):
        """Initialize application.

        Args:
            config: Configuration object
        """
        self.config = config
        self.api_client = NewsAPIClient(
            base_url=config.api_base_url,
            timeout=config.api_timeout,
        )
        self.matcher = KeywordMatcher(
            symbols=config.watched_symbols,
            topics=config.watched_topics,
            event_types=config.watched_event_types,
        )
        self.notifier = TelegramNotifier(
            bot_token=config.telegram_bot_token,
            chat_ids=config.telegram_chat_ids,
            thread_id=config.telegram_thread_id,
        )
        self.state = StateManager()
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def run(self):
        """Run the main polling loop."""
        logger.info("Starting News Alert System")
        logger.info(f"Polling interval: {self.config.polling_interval} seconds")
        logger.info(f"Watching {len(self.config.watched_symbols)} symbols, "
                   f"{len(self.config.watched_topics)} topics, "
                   f"{len(self.config.watched_event_types)} event types")

        self.running = True

        while self.running:
            try:
                self._poll_and_process()
            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)

            # Wait for next poll or shutdown
            for _ in range(self.config.polling_interval):
                if not self.running:
                    break
                time.sleep(1)

        self._cleanup()

    def _poll_and_process(self):
        """Poll API for new articles and process matches."""
        now = int(datetime.now(timezone.utc).timestamp() * 1000)
        start_time = self.state.last_checked_at

        logger.info(f"Polling for articles since {start_time or 'beginning'}")

        articles = self.api_client.get_news(
            start_timestamp_ms=start_time,
            end_timestamp_ms=now,
        )

        logger.info(f"Fetched {len(articles)} articles")

        # Process articles
        matched_count = 0
        for article in articles:
            if self._process_article(article):
                matched_count += 1

        # Update state to now
        self.state.update_last_checked(now)

        if matched_count > 0:
            logger.info(f"Sent {matched_count} alerts this cycle")

    def _process_article(self, article: dict) -> bool:
        """Process a single article.

        Args:
            article: Article dictionary

        Returns:
            True if article matched and alert was sent, False otherwise.
        """
        # Get article ID - use _id or article_id
        article_id = article.get("_id") or article.get("article_id")
        if not article_id:
            logger.warning("Article missing ID, skipping")
            return False

        # Skip if already processed
        if self.state.is_article_processed(article_id):
            return False

        match_result = self.matcher.match(article)

        if match_result.has_matches():
            content = article.get("content", {})
            headline = content.get("headline", content.get("subheadline", "Unknown"))
            logger.info(f"Match found: {headline}")

            self.notifier.send_alert(article, match_result)

            # Mark as processed after successful send
            self.state.mark_article_processed(article_id)
            return True

        # Mark as processed even if no match (to avoid re-checking)
        self.state.mark_article_processed(article_id)
        return False

    def _cleanup(self):
        """Cleanup resources before shutdown."""
        logger.info("Cleaning up resources...")
        self.api_client.close()
        self.notifier.close()
        logger.info("Shutdown complete")


def main():
    """Entry point for the application."""
    try:
        config = Config()
        app = NewsAlertApp(config)
        app.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
