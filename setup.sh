#!/bin/bash

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
    LANG="TR"
    MSG_HEADER="   RSS Telegram Bot - Otomatik Kurulum Scripti   "
    MSG_DOCKER_CHECK="[1/4] Docker kontrol ediliyor..."
    MSG_DOCKER_MISSING="Docker bulunamadı! Lütfen önce Docker'ı kurun."
    MSG_DOCKER_INSTALL="Ubuntu için: curl -fsSL https://get.docker.com | sh"
    MSG_DOCKER_OK="Docker yüklü."
    MSG_COMPOSE_MISSING="Docker Compose bulunamadı!"
    MSG_COMPOSE_OK="Docker Compose yüklü."
    MSG_CONFIG="[2/4] Konfigürasyon ayarlanıyor..."
    MSG_ENV_EXISTS=".env dosyası zaten mevcut."
    MSG_RECREATE="Yeniden oluşturmak ister misiniz? (e/h): "
    MSG_USING_EXISTING="Mevcut konfigürasyon kullanılıyor."
    MSG_ENTER_INFO="Lütfen Telegram Bot bilgilerinizi girin:"
    MSG_TOKEN_EMPTY="Token boş olamaz!"
    MSG_CHATID_EMPTY="Chat ID boş olamaz!"
    MSG_AI_HEADER="--- AI Ayarları (İsteğe Bağlı) ---"
    MSG_AI_INFO="OpenRouter API Key (Ücretsiz modeller için: https://openrouter.ai/)"
    MSG_AI_KEY_PROMPT="OpenRouter API Key (Boş bırakırsanız AI özelliği kapalı olur): "
    MSG_AI_MODEL_PROMPT="Model (Varsayılan: google/gemini-2.0-flash-lite-preview-02-05:free): "
    MSG_ENV_CREATED=".env dosyası oluşturuldu."
    MSG_STARTING="[3/4] Konteynerler hazırlanıyor ve başlatılıyor..."
    MSG_DONE_HEADER="[4/4] Kurulum Tamamlandı!"
    MSG_DONE_SUCCESS="Bot başarıyla başlatıldı!"
    MSG_LOGS="Logları görmek için: "
    MSG_ERROR="Kurulum sırasında bir hata oluştu!"
else
    LANG="EN"
    MSG_HEADER="   RSS Telegram Bot - Auto Setup Script   "
    MSG_DOCKER_CHECK="[1/4] Checking Docker..."
    MSG_DOCKER_MISSING="Docker not found! Please install Docker first."
    MSG_DOCKER_INSTALL="For Ubuntu: curl -fsSL https://get.docker.com | sh"
    MSG_DOCKER_OK="Docker is installed."
    MSG_COMPOSE_MISSING="Docker Compose not found!"
    MSG_COMPOSE_OK="Docker Compose is installed."
    MSG_CONFIG="[2/4] Configuring..."
    MSG_ENV_EXISTS=".env file already exists."
    MSG_RECREATE="Do you want to recreate it? (y/n): "
    MSG_USING_EXISTING="Using existing configuration."
    MSG_ENTER_INFO="Please enter your Telegram Bot details:"
    MSG_TOKEN_EMPTY="Token cannot be empty!"
    MSG_CHATID_EMPTY="Chat ID cannot be empty!"
    MSG_AI_HEADER="--- AI Settings (Optional) ---"
    MSG_AI_INFO="OpenRouter API Key (For free models: https://openrouter.ai/)"
    MSG_AI_KEY_PROMPT="OpenRouter API Key (Leave empty to disable AI): "
    MSG_AI_MODEL_PROMPT="Model (Default: google/gemini-2.0-flash-lite-preview-02-05:free): "
    MSG_ENV_CREATED=".env file created."
    MSG_STARTING="[3/4] Preparing and starting containers..."
    MSG_DONE_HEADER="[4/4] Setup Completed!"
    MSG_DONE_SUCCESS="Bot started successfully!"
    MSG_LOGS="To see logs: "
    MSG_ERROR="An error occurred during setup!"
fi

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}${MSG_HEADER}${NC}"
echo -e "${BLUE}================================================${NC}"

# 1. Docker Check
echo -e "\n${BLUE}${MSG_DOCKER_CHECK}${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}${MSG_DOCKER_MISSING}${NC}"
    echo "$MSG_DOCKER_INSTALL"
    exit 1
fi
echo -e "${GREEN}${MSG_DOCKER_OK}${NC}"

# 2. Docker Compose Check
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}${MSG_COMPOSE_MISSING}${NC}"
    exit 1
fi
echo -e "${GREEN}${MSG_COMPOSE_OK}${NC}"

# 3. Configuration
echo -e "\n${BLUE}${MSG_CONFIG}${NC}"

if [ -f .env ]; then
    echo -e "${GREEN}${MSG_ENV_EXISTS}${NC}"
    read -p "$MSG_RECREATE" recreate
    if [[ $recreate != "e" && $recreate != "y" ]]; then
        echo "$MSG_USING_EXISTING"
    else
        rm .env
    fi
fi

if [ ! -f .env ]; then
    echo "$MSG_ENTER_INFO"
    
    read -p "Telegram Bot Token: " token
    while [[ -z "$token" ]]; do
        echo -e "${RED}${MSG_TOKEN_EMPTY}${NC}"
        read -p "Telegram Bot Token: " token
    done

    read -p "Chat ID: " chat_id
    while [[ -z "$chat_id" ]]; do
        echo -e "${RED}${MSG_CHATID_EMPTY}${NC}"
        read -p "Chat ID: " chat_id
    done

    echo -e "\n${BLUE}${MSG_AI_HEADER}${NC}"
    echo "$MSG_AI_INFO"
    read -p "$MSG_AI_KEY_PROMPT" openrouter_key
    
    if [[ -n "$openrouter_key" ]]; then
        read -p "$MSG_AI_MODEL_PROMPT" openrouter_model
        if [[ -z "$openrouter_model" ]]; then
            openrouter_model="google/gemini-2.0-flash-lite-preview-02-05:free"
        fi
    else
        openrouter_model=""
    fi

    # Create .env file
    echo "TELEGRAM_TOKEN=\"$token\"" > .env
    echo "CHAT_ID=\"$chat_id\"" >> .env
    echo "OPENROUTER_API_KEY=\"$openrouter_key\"" >> .env
    echo "OPENROUTER_MODEL=\"$openrouter_model\"" >> .env
    
    echo -e "${GREEN}${MSG_ENV_CREATED}${NC}"
fi

# 4. Setup and Start
echo -e "\n${BLUE}${MSG_STARTING}${NC}"

# Determine Docker Compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

$DOCKER_COMPOSE_CMD down 2>/dev/null
$DOCKER_COMPOSE_CMD up -d --build

if [ $? -eq 0 ]; then
    echo -e "\n${BLUE}${MSG_DONE_HEADER}${NC}"
    echo -e "${GREEN}${MSG_DONE_SUCCESS}${NC}"
    echo -e "${MSG_LOGS} ${DOCKER_COMPOSE_CMD} logs -f"
else
    echo -e "\n${RED}${MSG_ERROR}${NC}"
    exit 1
fi
