"""Telegram bot integration for sending notifications."""

import asyncio
import logging
from typing import Any

from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends formatted news alerts to Telegram."""

    def __init__(self, bot_token: str, chat_ids: list[str], thread_id: str | None = None):
        """Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token
            chat_ids: List of chat IDs to send notifications to
            thread_id: Optional thread ID for forum topics
        """
        self.bot = Bot(token=bot_token)
        self.chat_ids = chat_ids
        self.thread_id = int(thread_id) if thread_id else None

    def send_alert(self, article: dict[str, Any], match_result: Any) -> bool:
        """Send a formatted alert for a matching article.

        Args:
            article: News article dictionary
            match_result: MatchResult with matched keywords

        Returns:
            True if all messages sent successfully, False otherwise.
        """
        message = self._format_message(article, match_result)
        success = True

        async def _send_messages():
            nonlocal success
            async with self.bot:
                for chat_id in self.chat_ids:
                    try:
                        await self.bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode="HTML",
                            message_thread_id=self.thread_id
                        )
                        thread_info = f" (thread {self.thread_id})" if self.thread_id else ""
                        logger.info(f"Sent alert to chat {chat_id}{thread_info}")
                    except TelegramError as e:
                        logger.error(f"Failed to send to chat {chat_id}: {e}")
                        success = False

        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(_send_messages())
        except RuntimeError:
            # No event loop exists, create new one
            asyncio.run(_send_messages())

        return success

    def _format_message(self, article: dict[str, Any], match_result: Any) -> str:
        """Format article into a Telegram message.

        Args:
            article: News article dictionary
            match_result: MatchResult with matched keywords

        Returns:
            Formatted HTML message string.
        """
        # Access nested content fields
        content = article.get("content", {})
        headline = content.get("headline", content.get("subheadline", "No Headline"))
        summary = content.get("summary", content.get("body", ""))[:300]
        url = article.get("source", {}).get("url", "#")

        # Get sentiment if available
        sentiment_data = article.get("sentiment", {})
        if sentiment_data:
            score = sentiment_data.get("overall_sentiment", 0)
            if score > 0.2:
                sentiment = "Positive"
            elif score < -0.2:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
        else:
            sentiment = "N/A"

        # Build match highlights
        highlights = []
        if match_result.symbols:
            highlights.append(f"<b>Symbols:</b> {', '.join(match_result.symbols)}")
        if match_result.topics:
            highlights.append(f"<b>Topics:</b> {', '.join(match_result.topics)}")
        if match_result.event_types:
            highlights.append(f"<b>Events:</b> {', '.join(match_result.event_types)}")

        highlights_text = "\n".join(highlights) if highlights else "No specific matches"

        message = f"""📰 <b>{headline}</b>

{summary if summary else 'No summary available'}

{highlights_text}

<b>Sentiment:</b> {sentiment}

🔗 <a href="{url}">Read more</a>"""

        return message

    def close(self):
        """Close the bot session."""
        # Note: python-telegram-bot v20+ uses async, but we're using sync wrapper
        # The bot will be cleaned up automatically
        pass
