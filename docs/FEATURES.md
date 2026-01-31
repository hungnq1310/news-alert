# News Alert System - Features

## Overview
News Alert System polls news API and sends matching articles to Telegram forum topics with built-in deduplication and Docker deployment support.

---

## Features

### 1. Keyword Matching
- **Symbols**: Match stocks by ticker (e.g., `VNM`, `VIC`, `HPG`)
- **Topics**: Match by article topics (financial_performance, market_expansion, strategic_partnership, mergers_acquisitions)
- **Event Types**: Match by extracted events (shareholder_reduction, equity_pledge, bankruptcy_liquidation, etc.)

### 2. Telegram Integration
- **Forum Topics Support**: Send messages to specific topics using `TELEGRAM_THREAD_ID`
- **HTML Formatting**: Rich formatted messages with headline, summary, matched keywords, sentiment
- **Multiple Chats**: Support for multiple chat IDs

### 3. Deduplication System
- **Article ID Tracking**: Tracks processed article IDs to prevent duplicate alerts
- **Persistent State**: Saves up to 1000 recent article IDs in `state.json`
- **Auto-Migration**: Automatically migrates old state files to new format
- **Smart Skipping**: Skips already-processed articles before matching

### 4. State Management
- **Persistent State**: Tracks last checked timestamp AND processed article IDs
- **Auto-recovery**: Continues from last checkpoint on restart
- **State File**: `state.json` (or `./data/state.json` for Docker)

### 5. Docker Deployment
- **Always-On**: Container auto-restarts with `restart: unless-stopped`
- **Health Check**: Built-in container health monitoring
- **Persistent Volume**: State preserved in `./data/` directory
- **Easy Management**: Use `./deploy.sh` script for common operations

### 6. CI/CD Pipeline
- **GitHub Actions**: Automatic Docker builds on code changes
- **Docker Hub Push**: Images automatically pushed to Docker Hub
- **Multi-Tags**: Generates `latest`, branch, and SHA tags
- **Manual Trigger**: On-demand builds via workflow_dispatch
- **PR Builds**: Test builds for pull requests

### 7. Configuration
- **YAML + ENV**: Centralized config in `config.yaml` with environment variable overrides
- **API URL Override**: Set `API_BASE_URL` in `.env` for Docker deployment
- **Watched Items**: Configure symbols, topics, and event types to watch
- **Polling Interval**: Adjustable polling frequency

### 8. Claude Code Hooks
- **Implementation Logging**: Tracks every tool execution to `.claude/logs/implementation-steps.jsonl`
- **Auto-Commit**: Suggests conventional commit messages on session end
- **Project-Specific**: Hooks stored in `.claude/` directory
- **Auto-Trigger**: Runs on PostToolUse and Stop events

---

## API Schema

### Article Structure
```json
{
  "_id": "unique-article-id",
  "content": {
    "headline": "Apple Announces Record Quarterly Revenue",
    "summary": "Apple Inc. reported record-breaking quarterly revenue...",
    "body": "Full article text...",
    "author": "Jane Smith"
  },
  "source": {
    "url": "https://example.com/article",
    "domain": "bloomberg.com",
    "name": "Bloomberg"
  },
  "companies_mentioned": [
    {
      "symbol_code": "VNM",
      "company_name": "Vinamilk"
    }
  ],
  "classification": {
    "topics": ["financial_performance", "market_expansion"]
  },
  "events_extracted": [
    {
      "event_type": "shareholder_reduction"
    }
  ],
  "sentiment": {
    "overall_sentiment": 0.5
  }
}
```

---

## Setup

### 1. Environment Variables (.env)
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="-1002391447760"
TELEGRAM_THREAD_ID="9"  # Optional: for forum topics

# API Configuration (for Docker deployment)
API_BASE_URL="http://192.168.2.138:8005/api/v3"
```

### 2. Configuration (config.yaml)
```yaml
watched:
  symbols: ["VNM", "VIC", "HPG", "MSN"]
  topics: ["financial_performance", "market_expansion"]
  event_types: ["shareholder_reduction", "equity_pledge"]

telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}
  chat_ids:
    - ${TELEGRAM_CHAT_ID}
  thread_id: ${TELEGRAM_THREAD_ID}
```

### 3. Get Forum Topic ID
1. Open the topic in Telegram
2. Copy URL: `t.me/c/2391447760/9`
3. Thread ID is the last number: `9`

---

## Usage

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m src.main

# Or in background
nohup python -m src.main > logs/app.log 2>&1 &
```

### Docker Deployment
```bash
# Using deploy script (recommended)
./deploy.sh start      # Start service
./deploy.sh logs       # View logs
./deploy.sh status     # Check status
./deploy.sh stop       # Stop service
./deploy.sh rebuild    # Rebuild after code changes

# Or using docker-compose directly
docker compose up -d           # Start
docker compose logs -f         # View logs
docker compose down            # Stop
```

---

## State File Format

### Current State Structure
```json
{
  "last_checked_at": 1769874980000,
  "processed_article_ids": [
    "697e1edcda5e76709f3a7b83",
    "697e1eb3da5e76709f3a7b82",
    "697e1e92da5e76709f3a7b81"
  ]
}
```

- `last_checked_at`: Timestamp of last API poll (milliseconds since epoch)
- `processed_article_ids`: List of processed article IDs (max 1000)

---

## Troubleshooting

### "Chat not found"
- Ensure bot is admin in the group
- Use numeric chat ID (e.g., `-1002391447760`), not URL format

### "Event loop is closed"
- Fixed: Bot now reuses event loop properly

### Empty messages
- Fixed: Now correctly accesses nested `content.headline`, `content.summary`

### Duplicate alerts
- Check `state.json` - should have `processed_article_ids` array
- If missing, system will auto-migrate on next run

### Docker container can't connect to API
- Set `API_BASE_URL` in `.env` to host IP (not localhost)
- Example: `API_BASE_URL=http://192.168.2.138:8005/api/v3`

### Container not starting
- Check logs: `docker compose logs`
- Verify `.env` file exists with correct values
- Ensure `./data/` directory exists

---

## Project Structure
```
news-alert/
├── src/
│   ├── main.py           # Main application loop with deduplication
│   ├── config.py         # Config with API_BASE_URL env override
│   ├── telegram.py       # Telegram bot integration
│   ├── matcher.py        # Keyword matching logic
│   └── api_client.py     # News API client
├── .claude/
│   ├── hooks/
│   │   └── log-implementation.py  # Claude Code hook
│   ├── logs/                        # Implementation logs
│   └── settings.local.json         # Hook configuration
├── data/
│   └── state.json         # Persistent state (Docker)
├── docs/
│   ├── FEATURES.md        # This file
│   └── DOCKER.md          # Docker deployment guide
├── config.yaml            # Main configuration
├── .env                   # Environment variables
├── state.json             # Persistent state (local)
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container image
├── deploy.sh              # Deployment script
└── requirements.txt       # Dependencies
```

---

## Quick Reference

| Feature | Status |
|---------|--------|
| Keyword Matching | ✅ |
| Telegram Forum Topics | ✅ |
| Deduplication | ✅ |
| Docker Deployment | ✅ |
| CI/CD Pipeline | ✅ |
| Claude Code Hooks | ✅ |
| Auto-Commit Suggestion | ✅ |
| Auto-Restart | ✅ |
| Health Check | ✅ |
| State Persistence | ✅ |
| API URL Override | ✅ |
