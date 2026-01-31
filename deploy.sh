#!/bin/bash
# News Alert Docker Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ACTION=${1:-help}

case "$ACTION" in
  build)
    echo -e "${GREEN}Building Docker image...${NC}"
    docker compose build
    ;;

  start|up)
    echo -e "${GREEN}Starting News Alert service...${NC}"
    mkdir -p data
    docker compose up -d
    echo -e "${GREEN}Service started!${NC}"
    echo "View logs: docker compose logs -f"
    ;;

  stop|down)
    echo -e "${YELLOW}Stopping News Alert service...${NC}"
    docker compose down
    echo -e "${GREEN}Service stopped.${NC}"
    ;;

  restart)
    echo -e "${YELLOW}Restarting News Alert service...${NC}"
    docker compose restart
    echo -e "${GREEN}Service restarted!${NC}"
    ;;

  logs)
    echo -e "${GREEN}Showing logs (Ctrl+C to exit):${NC}"
    docker compose logs -f
    ;;

  status)
    echo -e "${GREEN}Container status:${NC}"
    docker ps --filter "name=news-alert"
    ;;

  rebuild)
    echo -e "${YELLOW}Rebuilding and restarting...${NC}"
    docker compose build --no-cache
    docker compose up -d
    echo -e "${GREEN}Done!${NC}"
    ;;

  shell|sh)
    echo -e "${GREEN}Opening shell in container...${NC}"
    docker compose exec news-alert bash
    ;;

  clean)
    echo -e "${RED}Removing container, images, and volumes...${NC}"
    read -p "Are you sure? This will delete all data! [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      docker compose down -v --rmi all
      rm -rf data
      echo -e "${GREEN}Cleaned.${NC}"
    else
      echo "Cancelled."
    fi
    ;;

  help|*)
    echo "News Alert Docker Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build     Build Docker image"
    echo "  start     Start service (up)"
    echo "  stop      Stop service (down)"
    echo "  restart   Restart service"
    echo "  logs      Show logs (follow mode)"
    echo "  status    Show container status"
    echo "  rebuild   Rebuild and restart"
    echo "  shell     Open shell in container"
    echo "  clean     Remove everything (including data)"
    echo "  help      Show this help"
    ;;
esac
