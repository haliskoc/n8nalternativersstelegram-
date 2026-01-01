#!/bin/bash

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo -e "\033[0;31mBu script sudo (root) yetkisi ile çalıştırılmalıdır.\033[0m"
   echo -e "\033[0;31mThis script must be run with sudo (root) privileges.\033[0m"
   echo "Örn: sudo ./setup.sh"
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
    MSG_ENTER_INFO="Lütfen aşağıdaki adımları takip ederek bilgileri girin:"
    
    MSG_STEP_TOKEN="--- ADIM 1: TELEGRAM BOT TOKEN ALMA ---
1. Telegram uygulamasını açın.
2. Arama kısmına @BotFather yazın ve botu başlatın.
3. /newbot komutunu gönderin.
4. Botunuza bir isim verin (Örn: Haber Botu).
5. Botunuza bir kullanıcı adı verin (Örn: haber_rss_bot - sonu 'bot' ile bitmeli).
6. BotFather size bir 'HTTP API Token' verecektir.
7. O uzun kodu kopyalayın ve aşağıya yapıştırın.
(Sadece kodu yapıştırın, tüm mesajı değil!)"
    
    MSG_STEP_CHATID="--- ADIM 2: CHAT ID (KULLANICI ID) ALMA ---
1. Telegram arama kısmına @userinfobot yazın ve botu başlatın.
2. Bot size otomatik olarak 'Id' numaranızı gönderecektir.
3. Bu numarayı kopyalayın ve aşağıya yapıştırın."

    MSG_STEP_AI="--- ADIM 3: AI ANALİZ AYARLARI (İSTEĞE BAĞLI) ---
Haberlerin AI tarafından yorumlanmasını istiyorsanız:
1. https://openrouter.ai/ adresine gidin ve kayıt olun.
2. 'Keys' bölümünden yeni bir API Key oluşturun.
3. Oluşturduğunuz key'i kopyalayın ve aşağıya yapıştırın.
(İstemiyorsanız boş bırakıp Enter'a basabilirsiniz)"

    MSG_TOKEN_EMPTY="Hata: Token boş olamaz!"
    MSG_CHATID_EMPTY="Hata: Chat ID boş olamaz!"
    MSG_AI_KEY_PROMPT="OpenRouter API Key: "
    MSG_AI_MODEL_PROMPT="Kullanılacak Model (Varsayılan için Enter'a basın): "
    MSG_ENV_CREATED=".env dosyası başarıyla oluşturuldu."
    MSG_STARTING="[3/4] Docker konteynerleri hazırlanıyor ve başlatılıyor..."
    MSG_CLEANING="Eski konteynerler temizleniyor..."
    MSG_DONE_HEADER="[4/4] Kurulum Başarıyla Tamamlandı!"
    MSG_DONE_SUCCESS="Botunuz şu an arka planda çalışıyor."
    MSG_LOGS="Çalışmayı canlı izlemek için: "
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
    MSG_ENTER_INFO="Please follow the steps below to enter your details:"
    
    MSG_STEP_TOKEN="--- STEP 1: GETTING TELEGRAM BOT TOKEN ---
1. Open Telegram app.
2. Search for @BotFather and start the bot.
3. Send /newbot command.
4. Give your bot a name (e.g., News Bot).
5. Give your bot a username (e.g., news_rss_bot - must end with 'bot').
6. BotFather will give you an 'HTTP API Token'.
7. Copy that long code and paste it below.
(Paste ONLY the code, not the whole message!)"
    
    MSG_STEP_CHATID="--- STEP 2: GETTING YOUR CHAT ID ---
1. Search for @userinfobot on Telegram and start it.
2. The bot will automatically send you your 'Id' number.
3. Copy this number and paste it below."

    MSG_STEP_AI="--- STEP 3: AI ANALYSIS SETTINGS (OPTIONAL) ---
If you want AI to comment on the news:
1. Go to https://openrouter.ai/ and sign up.
2. Create a new API Key in the 'Keys' section.
3. Copy the key and paste it below.
(If you don't want this, just press Enter to skip)"

    MSG_TOKEN_EMPTY="Error: Token cannot be empty!"
    MSG_CHATID_EMPTY="Error: Chat ID cannot be empty!"
    MSG_AI_KEY_PROMPT="OpenRouter API Key: "
    MSG_AI_MODEL_PROMPT="Model to use (Press Enter for default): "
    MSG_ENV_CREATED=".env file created successfully."
    MSG_STARTING="[3/4] Preparing and starting Docker containers..."
    MSG_CLEANING="Cleaning up old containers..."
    MSG_DONE_HEADER="[4/4] Setup Completed Successfully!"
    MSG_DONE_SUCCESS="Your bot is now running in the background."
    MSG_LOGS="To watch the bot live: "
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
    echo -e "${GREEN}${MSG_ENTER_INFO}${NC}"
    
    echo -e "\n${BLUE}${MSG_STEP_TOKEN}${NC}"
    read -p "Telegram Bot Token: " raw_token
    while [[ -z "$raw_token" ]]; do
        echo -e "${RED}${MSG_TOKEN_EMPTY}${NC}"
        read -p "Telegram Bot Token: " raw_token
    done

    # Extract token if user pasted the whole message
    token=$(echo "$raw_token" | grep -oE "[0-9]+:[a-zA-Z0-9_-]+")
    if [[ -z "$token" ]]; then
        token="$raw_token"
    fi

    echo -e "\n${BLUE}${MSG_STEP_CHATID}${NC}"
    read -p "Chat ID: " chat_id
    while [[ -z "$chat_id" ]]; do
        echo -e "${RED}${MSG_CHATID_EMPTY}${NC}"
        read -p "Chat ID: " chat_id
    done

    echo -e "\n${BLUE}${MSG_STEP_AI}${NC}"
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

echo -e "${BLUE}${MSG_CLEANING}${NC}"
# Force remove any container with the same name to avoid conflicts
docker rm -f rss-telegram-bot 2>/dev/null

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
