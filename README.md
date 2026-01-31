# Finance News Alert System

A Python-based monitoring system that fetches financial news from a REST API and sends Telegram notifications when watched keywords appear in new articles.

## Features

- Polls financial news API at configurable intervals
- Matches articles against watched symbols, topics, and event types
- Sends formatted Telegram alerts for matching articles
- Persists state between runs to avoid duplicate alerts
- Graceful shutdown handling

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd news-alert
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
```bash
cp .env.example .env
# Edit .env with your Telegram bot token and chat ID
```

4. Edit `config.yaml` to customize watched keywords and settings.

## Configuration

### Environment Variables (.env)

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Chat ID to send notifications to |

### Config File (config.yaml)

```yaml
api:
  base_url: http://localhost:8005/api/v3  # API base URL
  timeout: 30                              # Request timeout

polling:
  interval_seconds: 60                      # How often to poll

watched:
  symbols: ["AAPL", "GOOGL", "TSLA"]      # Ticker symbols to watch
  topics: ["earnings", "merger"]           # Topics to watch
  event_types: ["earnings_beat"]           # Event types to watch

telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}
  chat_ids:
    - ${TELEGRAM_CHAT_ID}
```

## Usage

Run the application:

```bash
python -m src.main
```

The application will:
1. Start polling the API at the configured interval
2. Check each new article against your watched keywords
3. Send Telegram notifications for matches
4. Persist the last checked timestamp to `state.json`

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Copy the bot token
3. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. Add both to your `.env` file

## State Persistence

The application stores its state in `state.json`:

```json
{
  "last_checked_at": 1737350400000
}
```

This prevents duplicate alerts for the same articles.

## Stopping the Application

Press `Ctrl+C` to gracefully shutdown. The application will:
- Stop polling
- Save current state
- Close connections cleanly

## Project Structure

```
news-alert/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── api_client.py      # REST API client
│   ├── matcher.py         # Keyword matching logic
│   ├── telegram.py        # Telegram notifications
│   └── main.py            # Main application loop
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── state.json             # Persistent state (auto-generated)
└── README.md
```

## License

MIT License
