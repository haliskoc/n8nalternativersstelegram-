#!/bin/bash

# Colors / Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Resolve Project Directory / Proje dizinini bul
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${RED}======================================================${NC}"
echo -e "${RED}   RSS TELEGRAM BOT - UNINSTALL / KALDIRMA SCRIPT   ${NC}"
echo -e "${RED}======================================================${NC}"
echo ""
echo -e "Detected project directory / Tespit edilen proje dizini:"
echo -e "${BLUE}$PROJECT_DIR${NC}"
echo ""
echo -e "${RED}WARNING / DİKKAT:${NC}"
echo "This action will / Bu işlem şunları yapacaktır:"
echo "1. Stop & remove Docker containers (Docker konteynerlerini durdurup silecek)"
echo "2. Remove Docker images (Docker imajlarını silecek)"
echo "3. Delete database & configs (Veritabanı ve ayar dosyalarını silecek)"
echo "4. DELETE THIS ENTIRE DIRECTORY! (BU KLASÖRÜ TAMAMEN SİLECEK!)"
echo ""

read -p "Are you sure you want to proceed? / Devam etmek istiyor musunuz? (y/n): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo -e "${YELLOW}Uninstallation aborted. / İşlem iptal edildi.${NC}"
    exit 0
fi

# Create a temporary cleanup script / Geçici bir temizleme scripti oluştur
TEMP_SCRIPT="/tmp/rss_bot_cleanup.sh"

cat > "$TEMP_SCRIPT" <<EOF
#!/bin/bash

PROJECT_DIR="$PROJECT_DIR"

echo "Cleaning up Docker... / Docker temizliği yapılıyor..."
cd "\$PROJECT_DIR"

# Docker Compose Down
if docker compose version &> /dev/null; then
    docker compose down -v --rmi all
elif command -v docker-compose &> /dev/null; then
    docker-compose down -v --rmi all
else
    echo "Docker Compose not found, trying manual cleanup... / Docker Compose bulunamadı, manuel temizlik deneniyor..."
    docker stop rss-telegram-bot 2>/dev/null
    docker rm rss-telegram-bot 2>/dev/null
    # Try to guess image name / Imaj ismini tahmin etmeye çalış
    DIR_NAME=\$(basename "\$PROJECT_DIR" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')
    docker rmi "\${DIR_NAME}-rss-telegram-bot" 2>/dev/null
    docker rmi "rss-telegram-bot" 2>/dev/null
fi

echo "Removing files... / Dosyalar siliniyor..."
cd ..
rm -rf "\$PROJECT_DIR"

echo -e "\033[0;32m✅ Uninstallation complete. / Kaldırma işlemi tamamlandı.\033[0m"
echo "Directory removed / Klasör silindi: \$PROJECT_DIR"

# Self-destruct / Kendini imha et
rm -- "\$0"
EOF

chmod +x "$TEMP_SCRIPT"

echo -e "${YELLOW}Starting cleanup process... / Temizleme işlemi başlatılıyor...${NC}"
exec "$TEMP_SCRIPT"
