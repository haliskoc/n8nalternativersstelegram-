#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== RSS Telegram Bot Update Utility ===${NC}"

# 1. Pull latest changes
echo -e "\n${BLUE}[1/3] Pulling latest code from git...${NC}"
if git pull; then
    echo -e "${GREEN}Code updated successfully.${NC}"
else
    echo -e "${RED}Git pull failed. Please check your internet connection or git status.${NC}"
    exit 1
fi

# 2. Update Feeds Database
echo -e "\n${BLUE}[2/3] Updating feeds database...${NC}"
if [ -f generate_feeds_db.py ]; then
    python3 generate_feeds_db.py
    echo -e "${GREEN}Feeds database updated.${NC}"
fi

# 3. Rebuild and Restart Containers
echo -e "\n${BLUE}[3/3] Rebuilding and restarting bot...${NC}"

# Determine Docker Compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

$DOCKER_COMPOSE_CMD down 2>/dev/null
$DOCKER_COMPOSE_CMD up -d --build

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Update Completed Successfully!${NC}"
    echo "Your bot is running with the latest version."
else
    echo -e "\n${RED}Update failed during container rebuild.${NC}"
    exit 1
fi
