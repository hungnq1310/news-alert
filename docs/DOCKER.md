# Docker Deployment

## Quick Start

### 1. Build and Run

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### 2. Environment Variables

Create `.env` file (use `.env.example` as template):

```bash
cp .env.example .env
# Edit .env with your values
```

Required variables:
```bash
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="-1002391447760"
TELEGRAM_THREAD_ID="9"  # Optional
```

### 3. Configuration

Edit `config.yaml` to set watched symbols, topics, and events:

```yaml
watched:
  symbols: ["VNM", "VIC", "HPG", "MSN"]
  topics: ["financial_performance", "market_expansion"]
  event_types: ["shareholder_reduction", "equity_pledge"]
```

## Persistence

- State file is stored in `./data/state.json`
- Mount this directory to preserve state across container restarts

## Health Check

Container includes health check. View status:

```bash
docker ps
docker inspect news-alert | grep -A 5 Health
```

## Logs

```bash
# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker logs -f news-alert
```

## Restart Policies

- `restart: unless-stopped` - Always restart unless explicitly stopped
- Container survives host reboots

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### State file missing
```bash
mkdir -p data
touch data/state.json
echo '{"last_checked_at": null, "processed_article_ids": []}' > data/state.json
docker-compose restart
```

### Check environment variables
```bash
docker-compose config
```

### Shell into container
```bash
docker-compose exec news-alert bash
```
