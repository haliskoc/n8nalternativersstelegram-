#!/bin/bash

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Proje dizinini bul (Scriptin çalıştığı yer)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${RED}======================================================${NC}"
echo -e "${RED}   RSS TELEGRAM BOT - KALDIRMA / UNINSTALL SCRIPT   ${NC}"
echo -e "${RED}======================================================${NC}"
echo ""
echo -e "Tespit edilen proje dizini / Detected project directory:"
echo -e "${BLUE}$PROJECT_DIR${NC}"
echo ""
echo -e "${RED}DİKKAT / WARNING:${NC}"
echo "Bu işlem şunları yapacaktır / This action will:"
echo "1. Docker konteynerlerini durdurup silecek (Stop & remove Docker containers)"
echo "2. Docker imajlarını silecek (Remove Docker images)"
echo "3. Veritabanı ve ayar dosyalarını silecek (Delete database & configs)"
echo "4. BU KLASÖRÜ TAMAMEN SİLECEK! (DELETE THIS ENTIRE DIRECTORY!)"
echo ""

read -p "Devam etmek istiyor musunuz? / Are you sure? (y/n): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "İşlem iptal edildi. / Aborted."
    exit 0
fi

# Geçici bir temizleme scripti oluştur (Kendi kendini silerken hata vermemesi için)
TEMP_SCRIPT="/tmp/rss_bot_cleanup.sh"

cat > "$TEMP_SCRIPT" <<EOF
#!/bin/bash

PROJECT_DIR="$PROJECT_DIR"

echo "Docker temizliği yapılıyor... / Cleaning up Docker..."
cd "\$PROJECT_DIR"

# Docker Compose Down
if docker compose version &> /dev/null; then
    docker compose down -v --rmi all
elif command -v docker-compose &> /dev/null; then
    docker-compose down -v --rmi all
else
    echo "Docker Compose bulunamadı, manuel temizlik deneniyor..."
    docker stop rss-telegram-bot 2>/dev/null
    docker rm rss-telegram-bot 2>/dev/null
    # Imaj ismini tahmin etmeye çalış (klasör adı_servis adı)
    DIR_NAME=\$(basename "\$PROJECT_DIR" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')
    docker rmi "\${DIR_NAME}-rss-telegram-bot" 2>/dev/null
    docker rmi "rss-telegram-bot" 2>/dev/null
fi

echo "Dosyalar siliniyor... / Removing files..."
cd ..
rm -rf "\$PROJECT_DIR"

echo "✅ Kaldırma işlemi tamamlandı. / Uninstallation complete."
echo "Klasör silindi: \$PROJECT_DIR"

# Kendini imha et
rm -- "\$0"
EOF

chmod +x "$TEMP_SCRIPT"

echo "Temizleme işlemi başlatılıyor..."
exec "$TEMP_SCRIPT"
