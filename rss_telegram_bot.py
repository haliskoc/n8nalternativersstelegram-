#!/usr/bin/env python3
"""
WIRED RSS Feed Telegram Bot
Oracle Cloud Free Tier için optimize edilmiş RSS haber botu
"""

import feedparser
import requests
import sqlite3
import time
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rss_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RSSNewsBot:
    def __init__(self, telegram_token: str, chat_id: str, rss_urls: list = None):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        
        # Varsayılan RSS feed listesi
        if rss_urls is None:
            self.rss_urls = [
                # Uluslararası Teknoloji Siteleri
                "https://techcrunch.com/feed",
                "https://www.wired.com/feed/rss",
                "https://www.techrepublic.com/index.rss",
                "https://www.computerweekly.com/rss/All-Computer-Weekly-content.xml",
                "http://feeds.arstechnica.com/arstechnica/index",
                "https://www.theverge.com/rss/index.xml",
                "https://www.engadget.com/rss.xml",
                
                # Türkçe Teknoloji Siteleri
                "https://www.webtekno.com/rss.xml",
                "https://www.technopat.net/feed",
                "https://shiftdelete.net/feed",
                "https://donanimgunlugu.com/feed",
                "https://pchocasi.com.tr/feed",
                "https://www.teknoblog.com/feed",
                "https://www.megabayt.com/rss/categorynews/teknoloji",
                "https://www.sozcu.com.tr/feeds-rss-category-bilim-teknoloji"
            ]
        else:
            self.rss_urls = rss_urls
            
        self.telegram_api_url = f"https://api.telegram.org/bot{telegram_token}"
        self.db_path = "news_bot.db"
        self.init_database()
        
    def init_database(self):
        """SQLite veritabanını başlat ve tabloyu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_hash TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Veritabanı başarıyla başlatıldı")
        except Exception as e:
            logger.error(f"Veritabanı başlatma hatası: {e}")
    
    def get_news_hash(self, title: str, link: str) -> str:
        """Haber için benzersiz hash oluştur"""
        content = f"{title}_{link}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_news_sent(self, news_hash: str) -> bool:
        """Haberin daha önce gönderilip gönderilmediğini kontrol et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM sent_news WHERE news_hash = ?", (news_hash,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"Veritabanı kontrol hatası: {e}")
            return False
    
    def mark_news_sent(self, news_hash: str, title: str, link: str):
        """Haberi gönderildi olarak işaretle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO sent_news (news_hash, title, link) VALUES (?, ?, ?)",
                (news_hash, title, link)
            )
            conn.commit()
            conn.close()
            logger.info(f"Haber işaretlendi: {title[:50]}...")
        except Exception as e:
            logger.error(f"Haber işaretleme hatası: {e}")
    
    def fetch_rss_feed(self) -> List[Dict]:
        """Tüm RSS feed'lerini çek ve parse et"""
        all_news_items = []
        
        for rss_url in self.rss_urls:
            try:
                logger.info(f"RSS feed çekiliyor: {rss_url}")
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parse hatası var: {rss_url}")
                    continue
                
                site_name = self.get_site_name(rss_url)
                
                for entry in feed.entries:
                    # Son 24 saat içindeki haberleri al
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if datetime.now() - pub_date <= timedelta(hours=24):
                            all_news_items.append({
                                'title': entry.get('title', 'Başlık yok'),
                                'link': entry.get('link', ''),
                                'summary': entry.get('summary', entry.get('description', 'Özet yok')),
                                'published': pub_date,
                                'source': site_name
                            })
                    except Exception as e:
                        logger.warning(f"Tarih parse hatası: {e}")
                        # Tarih parse edilemezse de haberi ekle
                        all_news_items.append({
                            'title': entry.get('title', 'Başlık yok'),
                            'link': entry.get('link', ''),
                            'summary': entry.get('summary', entry.get('description', 'Özet yok')),
                            'published': datetime.now(),
                            'source': site_name
                        })
                
                logger.info(f"{site_name}: {len([item for item in all_news_items if item.get('source') == site_name])} haber bulundu")
                
            except Exception as e:
                logger.error(f"RSS feed çekme hatası ({rss_url}): {e}")
                continue
        
        # Haberleri tarihe göre sırala (en yeni önce)
        all_news_items.sort(key=lambda x: x['published'], reverse=True)
        
        logger.info(f"Toplam {len(all_news_items)} yeni haber bulundu")
        return all_news_items
    
    def get_site_name(self, url: str) -> str:
        """URL'den site adını çıkar"""
        site_names = {
            "techcrunch.com": "TechCrunch",
            "wired.com": "WIRED",
            "techrepublic.com": "TechRepublic",
            "computerweekly.com": "Computer Weekly",
            "arstechnica.com": "Ars Technica",
            "theverge.com": "The Verge",
            "engadget.com": "Engadget",
            "webtekno.com": "Webtekno",
            "technopat.net": "Technopat",
            "shiftdelete.net": "ShiftDelete",
            "donanimgunlugu.com": "Donanım Günlüğü",
            "pchocasi.com.tr": "PC Hocası",
            "teknoblog.com": "Teknoblog",
            "megabayt.com": "Megabayt",
            "sozcu.com.tr": "Sözcü"
        }
        
        for domain, name in site_names.items():
            if domain in url:
                return name
        
        return url.split('/')[2] if '/' in url else url
    
    def send_telegram_message(self, message: str) -> bool:
        """Telegram'a mesaj gönder"""
        try:
            # Test modu kontrolü
            if self.telegram_token == "test_token_for_local_testing":
                logger.info("TEST MODU: Mesaj gönderilmedi (test token)")
                logger.info(f"TEST MESAJI: {message[:100]}...")
                return True  # Test modunda başarılı say
            
            url = f"{self.telegram_api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            logger.info("Telegram mesajı başarıyla gönderildi")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram mesaj gönderme hatası: {e}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return False
    
    def format_news_message(self, news: Dict) -> str:
        """Haber mesajını formatla"""
        # HTML karakterlerini temizle
        title = news['title'].replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        summary = news['summary'].replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        source = news.get('source', 'Bilinmeyen Kaynak')
        
        # Özeti kısalt (Telegram limiti için)
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        message = f"""<b>YENİ HABER BİLDİRİMİ</b>

📰 <b>Kaynak:</b> {source}
📝 <b>Başlık:</b> {title}

---

📄 <b>Özet:</b> {summary}

---

🔗 <a href="{news['link']}">Habere Git (Tıkla)</a>"""
        
        return message
    
    def process_news(self):
        """Ana haber işleme fonksiyonu"""
        logger.info("Haber işleme başlatılıyor...")
        
        news_items = self.fetch_rss_feed()
        new_news_count = 0
        
        for news in news_items:
            news_hash = self.get_news_hash(news['title'], news['link'])
            
            if not self.is_news_sent(news_hash):
                message = self.format_news_message(news)
                
                if self.send_telegram_message(message):
                    self.mark_news_sent(news_hash, news['title'], news['link'])
                    new_news_count += 1
                    logger.info(f"Yeni haber gönderildi: {news['title'][:50]}...")
                    
                    # Rate limiting için kısa bekleme
                    time.sleep(2)
                else:
                    logger.error(f"Haber gönderilemedi: {news['title'][:50]}...")
        
        logger.info(f"İşlem tamamlandı. {new_news_count} yeni haber gönderildi.")
        return new_news_count
    
    def run_continuous(self, interval_minutes: int = 5):
        """Sürekli çalışma modu"""
        logger.info(f"Bot başlatıldı. {interval_minutes} dakikada bir kontrol edilecek.")
        
        while True:
            try:
                self.process_news()
                logger.info(f"{interval_minutes} dakika bekleniyor...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Bot durduruldu.")
                break
            except Exception as e:
                logger.error(f"Beklenmeyen hata: {e}")
                logger.info("5 dakika bekleniyor...")
                time.sleep(300)  # Hata durumunda 5 dakika bekle

def main():
    # Environment variables'dan konfigürasyon al
    telegram_token = os.getenv('TELEGRAM_TOKEN', 'your_telegram_bot_token_here')
    chat_id = os.getenv('CHAT_ID', 'your_telegram_chat_id_here')
    
    if not telegram_token or telegram_token == 'your_telegram_bot_token_here':
        logger.error("TELEGRAM_TOKEN environment variable gerekli!")
        logger.info("Test modu için geçici token kullanılıyor...")
        telegram_token = "test_token_for_local_testing"
    
    # Bot'u başlat (artık tüm RSS feed'leri otomatik yüklenir)
    bot = RSSNewsBot(telegram_token, chat_id)
    
    # Test mesajı gönder
    test_message = "🤖 RSS News Bot başlatıldı! 15 teknoloji sitesinden haberler takip ediliyor..."
    if bot.send_telegram_message(test_message):
        logger.info("Test mesajı gönderildi")
    else:
        logger.error("Test mesajı gönderilemedi")
    
    # Sürekli çalışma modunu başlat
    bot.run_continuous(interval_minutes=5)

if __name__ == "__main__":
    main()
