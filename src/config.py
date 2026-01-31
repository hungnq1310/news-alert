"""Configuration management for the news alert system."""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager loading from YAML with environment variable overrides."""

    def __init__(self, config_path: str | None = None):
        """Initialize configuration.

        Args:
            config_path: Path to config.yaml file. Defaults to ./config.yaml
        """
        load_dotenv()
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Configuration dictionary with environment variables substituted.
        """
        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        return self._substitute_env_vars(config)

    def _substitute_env_vars(self, value: Any) -> Any:
        """Recursively substitute environment variables in configuration.

        Args:
            value: Configuration value (dict, list, or string)

        Returns:
            Value with ${VAR} patterns replaced by environment variable values.
        """
        if isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        elif isinstance(value, str):
            if value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                if env_value is None:
                    # For optional vars, allow None (will be handled by caller)
                    if env_var.endswith("_ID") or "THREAD" in env_var:
                        return None
                    raise ValueError(f"Environment variable {env_var} not set")
                return env_value
            return value
        return value

    @property
    def api_base_url(self) -> str:
        """Get API base URL."""
        # Check environment variable first (for Docker/production override)
        env_url = os.getenv("API_BASE_URL")
        if env_url:
            return env_url
        return self._config["api"]["base_url"]

    @property
    def api_timeout(self) -> int:
        """Get API timeout in seconds."""
        return self._config["api"].get("timeout", 30)

    @property
    def polling_interval(self) -> int:
        """Get polling interval in seconds."""
        return self._config["polling"]["interval_seconds"]

    @property
    def watched_symbols(self) -> list[str]:
        """Get list of watched ticker symbols."""
        return self._config["watched"]["symbols"]

    @property
    def watched_topics(self) -> list[str]:
        """Get list of watched topics."""
        return self._config["watched"]["topics"]

    @property
    def watched_event_types(self) -> list[str]:
        """Get list of watched event types."""
        return self._config["watched"]["event_types"]

    @property
    def telegram_bot_token(self) -> str:
        """Get Telegram bot token."""
        return self._config["telegram"]["bot_token"]

    @property
    def telegram_chat_ids(self) -> list[str]:
        """Get list of Telegram chat IDs to notify."""
        return self._config["telegram"]["chat_ids"]

    @property
    def telegram_thread_id(self) -> str | None:
        """Get optional Telegram thread ID for forum topics."""
        return self._config["telegram"].get("thread_id")
