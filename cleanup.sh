#!/bin/bash

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo -e "\033[0;31mBu script sudo (root) yetkisi ile çalıştırılmalıdır.\033[0m"
   echo -e "\033[0;31mThis script must be run with sudo (root) privileges.\033[0m"
   echo "Örn: sudo ./cleanup.sh"
   exit 1
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Language Selection
echo -e "${BLUE}Select Language / Dil Seçiniz:${NC}"
echo "1) English"
echo "2) Türkçe"
read -p "Choice/Seçim (1/2): " lang_choice

if [[ "$lang_choice" == "2" ]]; then
    MSG_HEADER="   RSS Telegram Bot - Temizlik Scripti   "
    MSG_STOPPING="Bot durduruluyor ve konteynerler kaldırılıyor..."
    MSG_REMOVING_IMAGES="Docker imajları temizleniyor..."
    MSG_REMOVING_FILES="Yapılandırma dosyaları ve veritabanı siliniyor mu?"
    MSG_CONFIRM="Emin misiniz? Bu işlem veritabanını ve .env dosyasını SİLECEKTİR. (e/h): "
    MSG_CLEANED="Temizlik tamamlandı!"
else
    MSG_HEADER="   RSS Telegram Bot - Cleanup Script   "
    MSG_STOPPING="Stopping bot and removing containers..."
    MSG_REMOVING_IMAGES="Cleaning up Docker images..."
    MSG_REMOVING_FILES="Deleting configuration files and database?"
    MSG_CONFIRM="Are you sure? This will DELETE the database and .env file. (y/n): "
    MSG_CLEANED="Cleanup completed!"
fi

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}${MSG_HEADER}${NC}"
echo -e "${BLUE}================================================${NC}"

# Determine Docker Compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# 1. Stop and remove containers
echo -e "\n${BLUE}${MSG_STOPPING}${NC}"
$DOCKER_COMPOSE_CMD down --volumes --remove-orphans

# 2. Remove images
echo -e "\n${BLUE}${MSG_REMOVING_IMAGES}${NC}"
docker rmi -f rss-telegram-bot 2>/dev/null

# 3. Optional file removal
echo -e "\n${BLUE}${MSG_REMOVING_FILES}${NC}"
read -p "$MSG_CONFIRM" confirm
if [[ $confirm == "e" || $confirm == "y" ]]; then
    rm -f .env
    rm -f news_bot.db
    rm -f rss_bot.log
    rm -f feeds.json
    rm -f daily_news_*.xlsx
    echo -e "${GREEN}Dosyalar silindi.${NC}"
fi

echo -e "\n${GREEN}${MSG_CLEANED}${NC}"
