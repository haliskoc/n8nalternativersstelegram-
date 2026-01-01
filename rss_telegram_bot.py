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
from openai import OpenAI
import openpyxl
from openpyxl import Workbook
import schedule
import threading
from bs4 import BeautifulSoup

import json

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
    def __init__(self, telegram_token: str, chat_id: str, rss_urls: list = None, openrouter_api_key: str = None, openrouter_model: str = None):
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_model = openrouter_model or "google/gemini-2.0-flash-lite-preview-02-05:free"
        
        self.ai_client = None
        if self.openrouter_api_key:
            try:
                self.ai_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.openrouter_api_key,
                )
                logger.info(f"AI Client başlatıldı. Model: {self.openrouter_model}")
            except Exception as e:
                logger.error(f"AI Client başlatılamadı: {e}")
        
        # RSS feed listesini belirle
        self.rss_urls = []
        
        # 1. Öncelik: Parametre olarak gelen liste
        if rss_urls:
            self.rss_urls = rss_urls
        # 2. Öncelik: feeds.json dosyası
        elif os.path.exists('feeds.json'):
            try:
                with open('feeds.json', 'r', encoding='utf-8') as f:
                    self.rss_urls = json.load(f)
                logger.info(f"feeds.json dosyasından {len(self.rss_urls)} adet kaynak yüklendi.")
            except Exception as e:
                logger.error(f"feeds.json okuma hatası: {e}")
        
        # 3. Öncelik: Varsayılan liste (Eğer yukarıdakiler boşsa)
        if not self.rss_urls:
            logger.info("Varsayılan RSS listesi kullanılıyor.")
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
                "https://www.sozcu.com.tr/feeds-rss-category-bilim-teknoloji",
                
                # Bilim & Araştırma
                "https://rss.sciam.com/ScientificAmerican-Global",
                "https://www.science.org/rss/news_current.xml",
                "https://www.sciencedaily.com/rss/all.xml",
                "https://news.mit.edu/rss",
                "https://www.wired.com/category/science/feed",
                "https://www.nasa.gov/rss/dyn/breaking_news.rss",
                
                # Ekonomi & Finans
                "https://tradingeconomics.com/rss",
                "https://www.marketwatch.com/rss/topstories",
                "https://www.federalreserve.gov/feeds/press_all.xml",
                "https://cepr.org/rss-feeds",
                "https://economic-research.bnpparibas.com/RSS/en-US",
                
                # Genel Haber & Analiz
                "https://theconversation.com/global/topics/science-technology.rss",
                "https://futurism.com/feed"
            ]
            
        self.telegram_api_url = f"https://api.telegram.org/bot{telegram_token}"
        self.db_path = "news_bot.db"
        self.daily_news_path = "daily_news.xlsx"
        self.init_database()
        self.init_daily_news_storage()
        
    def init_database(self):
        """SQLite veritabanını başlat ve tabloları oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gönderilen haberlerin takibi için (Deduplication)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_hash TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tüm haberlerin detaylı arşivi için (Full History)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    news_hash TEXT UNIQUE NOT NULL,
                    source TEXT,
                    category TEXT,
                    title TEXT,
                    summary TEXT,
                    link TEXT,
                    published_date TIMESTAMP,
                    analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Veritabanı başarıyla başlatıldı (sent_news ve news_archive tabloları)")
        except Exception as e:
            logger.error(f"Veritabanı başlatma hatası: {e}")
    
    def init_daily_news_storage(self):
        """Günlük haber depolama Excel dosyasını başlat"""
        try:
            # Günlük dosya adı oluştur
            today = datetime.now().strftime('%Y-%m-%d')
            self.daily_news_path = f"daily_news_{today}.xlsx"
            
            if not os.path.exists(self.daily_news_path):
                wb = Workbook()
                ws = wb.active
                ws.title = f"Daily News {today}"
                ws.append(['Date', 'Time', 'Source', 'Category', 'Title', 'Content', 'Link'])
                wb.save(self.daily_news_path)
                logger.info(f"Günlük haber depolama dosyası oluşturuldu: {self.daily_news_path}")
        except Exception as e:
            logger.error(f"Günlük haber depolama başlatma hatası: {e}")
    
    def save_news_to_db(self, news_item: Dict, news_hash: str):
        """Haberi detaylı olarak veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            category = self.get_category_from_source(news_item.get('source', ''))
            published_date = news_item.get('published')
            if isinstance(published_date, datetime):
                published_date = published_date.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT OR IGNORE INTO news_archive 
                (news_hash, source, category, title, summary, link, published_date, analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                news_hash,
                news_item.get('source', 'Unknown'),
                category,
                news_item.get('title', ''),
                news_item.get('summary', ''),
                news_item.get('link', ''),
                published_date,
                news_item.get('analysis', '')
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Haber veritabanına arşivlendi: {news_item.get('title', '')[:30]}...")
        except Exception as e:
            logger.error(f"Veritabanı arşivleme hatası: {e}")

    def save_news_to_excel(self, news_item: Dict):
        """Haberi Excel dosyasına kaydet"""
        try:
            wb = openpyxl.load_workbook(self.daily_news_path)
            ws = wb.active
            
            # Kategori belirleme
            category = self.get_category_from_source(news_item.get('source', ''))
            
            # Bugünün tarihi
            today = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            
            ws.append([
                today,
                current_time,
                news_item.get('source', 'Unknown'),
                category,
                news_item.get('title', ''),
                news_item.get('summary', ''),
                news_item.get('link', '')
            ])
            
            wb.save(self.daily_news_path)
            logger.info(f"Haber Excel'e kaydedildi: {news_item.get('title', '')[:50]}...")
            
        except Exception as e:
            logger.error(f"Excel kaydetme hatası: {e}")
    
    def get_category_from_source(self, source: str) -> str:
        """Kaynağa göre kategori belirle"""
        tech_sources = ['TechCrunch', 'WIRED', 'TechRepublic', 'Computer Weekly', 'Ars Technica', 
                       'The Verge', 'Engadget', 'Webtekno', 'Technopat', 'ShiftDelete', 
                       'Donanım Günlüğü', 'PC Hocası', 'Teknoblog', 'Megabayt', 'Sözcü']
        
        science_sources = ['Scientific American', 'Science (AAAS)', 'ScienceDaily', 'MIT News', 
                          'NASA', 'The Conversation', 'Futurism']
        
        economics_sources = ['Trading Economics', 'MarketWatch', 'Federal Reserve', 'CEPR', 
                           'BNP Paribas']
        
        if source in tech_sources:
            return 'Technology'
        elif source in science_sources:
            return 'Science'
        elif source in economics_sources:
            return 'Economics'
        else:
            return 'General'
    
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
            # Teknoloji
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
            "sozcu.com.tr": "Sözcü",
            
            # Bilim & Araştırma
            "sciam.com": "Scientific American",
            "science.org": "Science (AAAS)",
            "sciencedaily.com": "ScienceDaily",
            "mit.edu": "MIT News",
            "nasa.gov": "NASA",
            
            # Ekonomi & Finans
            "tradingeconomics.com": "Trading Economics",
            "marketwatch.com": "MarketWatch",
            "federalreserve.gov": "Federal Reserve",
            "cepr.org": "CEPR",
            "bnpparibas.com": "BNP Paribas",
            
            # Genel
            "theconversation.com": "The Conversation",
            "futurism.com": "Futurism"
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
            
            # Hata durumunda detaylı log bas
            if response.status_code != 200:
                logger.error(f"Telegram API Hatası: {response.status_code} - {response.text}")
                
            response.raise_for_status()
            
            logger.info("Telegram mesajı başarıyla gönderildi")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram mesaj gönderme hatası: {e}")
            return False
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return False
    
    def analyze_news(self, title: str, summary: str, source: str) -> str:
        """Haberi AI ile analiz et"""
        if not self.ai_client:
            return None

        try:
            system_prompt = """Sen uzman bir teknoloji, bilim ve ekonomi analistisin. 
            Görevin sana verilen haber başlığını ve özetini analiz ederek Türkçe, detaylı ve içgörü dolu bir yorum yazmak.
            
            Lütfen şu yapıyı kullan:
            1. 🧐 **Analiz:** Haberin ne anlama geldiğini ve önemini kısaca açıkla.
            2. 💡 **Neden Önemli?:** Bu gelişmenin sektöre veya geleceğe etkileri neler olabilir?
            3. 🔮 **Gelecek Öngörüsü:** Bu haberin devamında neler beklenebilir?
            
            Yanıtın bilgilendirici, profesyonel ama anlaşılır olsun. Emojileri yerinde kullan."""

            user_content = f"Haber Kaynağı: {source}\nBaşlık: {title}\nÖzet: {summary}"

            completion = self.ai_client.chat.completions.create(
                model=self.openrouter_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ]
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"AI Analiz hatası: {e}")
            return None

    def format_news_message(self, news: Dict) -> str:
        """Haber mesajını formatla"""
        title = news.get('title', 'Başlık Yok')
        summary_raw = news.get('summary', '')
        source = news.get('source', 'Bilinmeyen Kaynak')
        link = news.get('link', '#')
        
        # HTML temizliği (BeautifulSoup ile)
        try:
            soup = BeautifulSoup(summary_raw, "html.parser")
            summary = soup.get_text(separator=" ", strip=True)
        except Exception as e:
            logger.warning(f"HTML temizleme hatası: {e}")
            summary = summary_raw

        # HTML karakterlerini escape et (Telegram HTML parse mode için)
        def escape_html(text):
            return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        title = escape_html(title)
        summary = escape_html(summary)
        source = escape_html(source)

        # Özeti kısalt
        if len(summary) > 350:
            summary = summary[:350] + "..."
        
        # Yeni Tasarım
        message = (
            f"📰 <b>{title}</b>\n\n"
            f"ℹ️ <i>{source}</i>\n"
            f"─────────────────────\n"
            f"{summary}\n\n"
            f"🔗 <a href='{link}'>Haberi Kaynağında Oku</a>"
        )
        
        # AI Analizi varsa ekle
        if news.get('analysis'):
            message += f"\n\n🧠 <b>AI Analizi</b>\n"
            message += f"{news['analysis']}"
        
        return message
    
    def process_news(self):
        """Ana haber işleme fonksiyonu"""
        logger.info("Haber işleme başlatılıyor...")
        
        news_items = self.fetch_rss_feed()
        new_news_count = 0
        
        for news in news_items:
            news_hash = self.get_news_hash(news['title'], news['link'])
            
            if not self.is_news_sent(news_hash):
                # AI Analizi yap (varsa)
                if self.ai_client:
                    logger.info(f"Haber analiz ediliyor: {news['title'][:30]}...")
                    analysis = self.analyze_news(news['title'], news['summary'], news['source'])
                    if analysis:
                        news['analysis'] = analysis

                message = self.format_news_message(news)
                
                if self.send_telegram_message(message):
                    self.mark_news_sent(news_hash, news['title'], news['link'])
                    # Haberi Veritabanına ve Excel'e kaydet
                    self.save_news_to_db(news, news_hash)
                    self.save_news_to_excel(news)
                    
                    new_news_count += 1
                    logger.info(f"Yeni haber gönderildi: {news['title'][:50]}...")
                    
                    # Rate limiting için kısa bekleme
                    time.sleep(2)
                else:
                    logger.error(f"Haber gönderilemedi: {news['title'][:50]}...")
        
        logger.info(f"İşlem tamamlandı. {new_news_count} yeni haber gönderildi.")
        return new_news_count
    
    def get_todays_news_from_excel(self) -> Dict[str, List[Dict]]:
        """Excel'den bugünün haberlerini kategorilere göre al"""
        try:
            wb = openpyxl.load_workbook(self.daily_news_path)
            ws = wb.active
            
            today = datetime.now().strftime('%Y-%m-%d')
            categories = {'Technology': [], 'Science': [], 'Economics': [], 'General': []}
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] == today:  # Bugünün tarihi
                    news_item = {
                        'source': row[2],
                        'category': row[3],
                        'title': row[4],
                        'content': row[5],
                        'link': row[6]
                    }
                    category = row[3]
                    if category in categories:
                        categories[category].append(news_item)
            
            return categories
            
        except Exception as e:
            logger.error(f"Excel'den haber okuma hatası: {e}")
            return {'Technology': [], 'Science': [], 'Economics': [], 'General': []}
    
    def generate_daily_summary_with_gemini(self) -> str:
        """Günlük özet oluştur (AI devre dışı - Telegram HTML formatı)"""
        try:
            todays_news = self.get_todays_news_from_excel()
            
            if not any(todays_news.values()):
                return "📭 <b>Bugün henüz haber bulunamadı.</b>"
            
            # Category emojis and Turkish names
            category_info = {
                'Technology': {'emoji': '💻', 'name': 'TEKNOLOJİ'},
                'Science': {'emoji': '🔬', 'name': 'BİLİM'},
                'Economics': {'emoji': '💰', 'name': 'EKONOMİ'},
                'General': {'emoji': '📰', 'name': 'GENEL'}
            }
            
            total_news = sum(len(news_list) for news_list in todays_news.values())
            
            # HTML formatted summary for Telegram
            summary = f"<b>� GÜNLÜK HABER ÖZETİ</b>\n"
            summary += f"<i>{datetime.now().strftime('%d.%m.%Y')} • Toplam {total_news} haber</i>\n"
            summary += f"━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for category, news_list in todays_news.items():
                if news_list:
                    info = category_info.get(category, {'emoji': '📌', 'name': category.upper()})
                    
                    # Category header with HTML
                    summary += f"{info['emoji']} <b>{info['name']}</b>\n"
                    summary += f"────────────────────\n"
                    
                    # Show top news items with HTML formatting
                    for i, news in enumerate(news_list[:5], 1):
                        # Escape HTML characters in title
                        title = news['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        source = news['source'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        
                        summary += f"🔹 <b>{title}</b>\n"
                        summary += f"   └ <i>{source}</i> • <a href=\"{news['link']}\">Oku →</a>\n\n"
                    
                    summary += "\n"
            
            # Footer
            summary += f"━━━━━━━━━━━━━━━━━━━━\n"
            summary += f"✨ <i>Günü yakaladınız!</i>\n"
            summary += f"🤖 <b>RSS News Bot</b>"
            
            return summary
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return f"Özet oluşturulurken hata: {e}"
    
    def format_news_for_ai(self, news_list: List[Dict]) -> str:
        """Haberleri AI için formatla"""
        if not news_list:
            return "Bu kategoride haber bulunamadı."
        
        formatted = ""
        for news in news_list[:10]:  # Maksimum 10 haber
            formatted += f"• {news['title']} ({news['source']})\n"
            formatted += f"  {news['content'][:200]}...\n\n"
        
        return formatted
    
    def send_daily_summary(self):
        """Günlük özeti gönder"""
        try:
            logger.info("Günlük özet hazırlanıyor...")
            summary = self.generate_daily_summary_with_gemini()
            
            if summary and len(summary) > 100:
                # Telegram mesaj limiti için böl
                if len(summary) > 4000:
                    chunks = [summary[i:i+4000] for i in range(0, len(summary), 4000)]
                    for i, chunk in enumerate(chunks):
                        message = f"📊 **GÜNLÜK ÖZET - BÖLÜM {i+1}/{len(chunks)}**\n\n{chunk}"
                        self.send_telegram_message(message)
                        time.sleep(2)
                else:
                    message = f"📊 **GÜNLÜK ÖZET - {datetime.now().strftime('%d.%m.%Y')}**\n\n{summary}"
                    self.send_telegram_message(message)
                
                logger.info("Günlük özet başarıyla gönderildi")
                
                # Özet gönderildikten sonra günlük dosyayı sil
                self.cleanup_daily_files()
                
            else:
                logger.warning("Özet oluşturulamadı veya çok kısa")
                
        except Exception as e:
            logger.error(f"Günlük özet gönderme hatası: {e}")
    
    def cleanup_daily_files(self):
        """Günlük dosyaları temizle"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            daily_file = f"daily_news_{today}.xlsx"
            
            if os.path.exists(daily_file):
                os.remove(daily_file)
                logger.info(f"Günlük dosya temizlendi: {daily_file}")
            
            # Eski günlük dosyalarını da temizle (7 günden eski)
            for i in range(1, 8):
                old_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                old_file = f"daily_news_{old_date}.xlsx"
                if os.path.exists(old_file):
                    os.remove(old_file)
                    logger.info(f"Eski günlük dosya temizlendi: {old_file}")
                    
        except Exception as e:
            logger.error(f"Günlük dosya temizleme hatası: {e}")
    
    def schedule_daily_summary(self):
        """Günlük özet zamanlaması (Devre Dışı)"""
        # schedule.every().day.at("18:35").do(self.send_daily_summary)
        logger.info("Günlük özet zamanlaması devre dışı bırakıldı.")
    
    def check_and_renew_daily_file(self):
        """Günlük dosya kontrolü ve yenileme"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_file = f"daily_news_{today}.xlsx"
            
            # Eğer bugünün dosyası yoksa yeni oluştur
            if not os.path.exists(current_file):
                self.daily_news_path = current_file
                wb = Workbook()
                ws = wb.active
                ws.title = f"Daily News {today}"
                ws.append(['Date', 'Time', 'Source', 'Category', 'Title', 'Content', 'Link'])
                wb.save(self.daily_news_path)
                logger.info(f"Yeni günlük dosya oluşturuldu: {self.daily_news_path}")
                
        except Exception as e:
            logger.error(f"Günlük dosya kontrol hatası: {e}")
    
    def run_continuous(self, interval_minutes: int = 5):
        """Sürekli çalışma modu"""
        logger.info(f"Bot başlatıldı. {interval_minutes} dakikada bir kontrol edilecek.")
        
        # Günlük özet zamanlamasını başlat
        self.schedule_daily_summary()
        
        # Schedule'ı ayrı thread'de çalıştır
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Her dakika kontrol et
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        while True:
            try:
                # Her çalışmada günlük dosya kontrolü yap
                self.check_and_renew_daily_file()
                
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
    openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
    openrouter_model = os.getenv('OPENROUTER_MODEL', '')
    
    if not telegram_token or telegram_token == 'your_telegram_bot_token_here':
        logger.error("TELEGRAM_TOKEN environment variable gerekli!")
        logger.info("Test modu için geçici token kullanılıyor...")
        telegram_token = "test_token_for_local_testing"
    
    # Bot'u başlat (artık tüm RSS feed'leri otomatik yüklenir)
    bot = RSSNewsBot(telegram_token, chat_id, openrouter_api_key=openrouter_api_key, openrouter_model=openrouter_model)
    
    # Test mesajı gönder
    test_message = "🤖 RSS News Bot başlatıldı! 30+ site (teknoloji, bilim, ekonomi) haberleri takip ediliyor...\n\n📊 Günlük özet 18:35'te gönderilecek!"
    if openrouter_api_key:
        test_message += "\n\n✨ AI Analiz Modülü: AKTİF"
    
    if bot.send_telegram_message(test_message):
        logger.info("Test mesajı gönderildi")
    else:
        logger.error("Test mesajı gönderilemedi")
    
    # Sürekli çalışma modunu başlat
    bot.run_continuous(interval_minutes=5)

if __name__ == "__main__":
    main()
