#!/usr/bin/env python3
"""
WIRED RSS Feed Telegram Bot
Oracle Cloud Free Tier için optimize edilmiş RSS haber botu
"""

import feedparser
import sqlite3
import logging
import os
import json
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
import openpyxl
from openpyxl import Workbook
from openai import OpenAI

# Telegram Library
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

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
    def __init__(self):
        self.db_path = "news_bot.db"
        self.daily_news_path = "daily_news.xlsx"
        self.rss_urls = []
        self.filters = {"whitelist": [], "blacklist": []}
        self.topics = {}
        
        # AI Setup
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_model = os.getenv('OPENROUTER_MODEL', "google/gemini-2.0-flash-lite-preview-02-05:free")
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

        self.load_config()
        self.init_database()
        self.init_daily_news_storage()

    def load_config(self):
        """Konfigürasyon dosyalarını yükle"""
        # Feeds
        if os.path.exists('feeds.json'):
            try:
                with open('feeds.json', 'r', encoding='utf-8') as f:
                    self.rss_urls = json.load(f)
            except Exception as e:
                logger.error(f"feeds.json okuma hatası: {e}")
        
        # Filters
        if os.path.exists('filters.json'):
            try:
                with open('filters.json', 'r', encoding='utf-8') as f:
                    self.filters = json.load(f)
            except Exception as e:
                logger.error(f"filters.json okuma hatası: {e}")

        # Topics
        if os.path.exists('topics.json'):
            try:
                with open('topics.json', 'r', encoding='utf-8') as f:
                    self.topics = json.load(f)
            except Exception as e:
                logger.error(f"topics.json okuma hatası: {e}")
        
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
        # Basit bir mapping, geliştirilebilir
        source_lower = source.lower()
        if any(x in source_lower for x in ['tech', 'wired', 'code', 'web', 'chip', 'donanım']):
            return 'Technology'
        elif any(x in source_lower for x in ['science', 'nasa', 'space', 'bilim']):
            return 'Science'
        elif any(x in source_lower for x in ['market', 'economy', 'finans', 'borsa']):
            return 'Economics'
        return 'General'

    def check_filters(self, title: str, summary: str) -> bool:
        """Haberin filtrelerden geçip geçmediğini kontrol et"""
        text = (title + " " + summary).lower()
        
        # Blacklist kontrolü (Varsa ve eşleşirse REDDET)
        if self.filters.get('blacklist'):
            for keyword in self.filters['blacklist']:
                if keyword.lower() in text:
                    logger.info(f"Haber filtrelendi (Blacklist: {keyword}): {title}")
                    return False
        
        # Whitelist kontrolü (Varsa ve eşleşmezse REDDET)
        if self.filters.get('whitelist'):
            found = False
            for keyword in self.filters['whitelist']:
                if keyword.lower() in text:
                    found = True
                    break
            if not found:
                # logger.info(f"Haber filtrelendi (Whitelist dışı): {title}")
                return False
                
        return True
    
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
    
    def fetch_feeds(self) -> List[Dict]:
        """RSS feedlerini çek"""
        all_news = []
        for url in self.rss_urls:
            try:
                feed = feedparser.parse(url)
                if feed.bozo: continue
                
                site_name = feed.feed.get('title', url)
                category = self.get_category_from_source(site_name)
                
                for entry in feed.entries:
                    # Tarih kontrolü (Son 24 saat)
                    try:
                        if hasattr(entry, 'published_parsed'):
                            pub_date = datetime(*entry.published_parsed[:6])
                        else:
                            pub_date = datetime.now()
                            
                        if datetime.now() - pub_date > timedelta(hours=24):
                            continue
                    except:
                        pub_date = datetime.now()

                    all_news.append({
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'published': pub_date,
                        'source': site_name,
                        'category': category
                    })
            except Exception as e:
                logger.error(f"Feed hatası ({url}): {e}")
        
        all_news.sort(key=lambda x: x['published'], reverse=True)
        return all_news

    def analyze_news(self, title: str, summary: str, source: str) -> str:
        if not self.ai_client: return None
        try:
            system_prompt = "Sen uzman bir teknoloji analistisin. Haberi Türkçe yorumla: 1. Analiz 2. Neden Önemli? 3. Gelecek Öngörüsü."
            user_content = f"Kaynak: {source}\nBaşlık: {title}\nÖzet: {summary}"
            completion = self.ai_client.chat.completions.create(
                model=self.openrouter_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"AI hatası: {e}")
            return None

# --- Telegram Bot Handlers ---

bot_logic = RSSNewsBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu"""
    await update.message.reply_text(
        "👋 Merhaba! Ben RSS Haber Botu.\n\n"
        "Komutlar:\n"
        "/sonhaberler - Son 5 haberi getir\n"
        "/ara <kelime> - Haberlerde arama yap\n"
        "/abone <url> - Yeni RSS kaynağı ekle\n"
        "/topicid - Bulunduğun konunun ID'sini öğren"
    )

async def get_topic_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/topicid komutu"""
    tid = update.message.message_thread_id
    title = update.message.chat.title or "Bu Sohbet"
    if tid:
        await update.message.reply_text(f"📍 Bu konunun ID'si: `{tid}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("Bu bir konu (topic) değil veya Genel sohbet.")

async def latest_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/sonhaberler komutu"""
    try:
        conn = sqlite3.connect(bot_logic.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, link, source FROM news_archive ORDER BY published_date DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            await update.message.reply_text("Henüz haber yok.")
            return

        msg = "📰 **Son Haberler:**\n\n"
        for title, link, source in rows:
            msg += f"🔹 [{title}]({link}) - _{source}_\n"
        
        await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"Hata: {e}")

async def search_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ara komutu"""
    if not context.args:
        await update.message.reply_text("Lütfen aranacak kelimeyi girin. Örn: /ara yapay zeka")
        return
    
    query = " ".join(context.args)
    try:
        conn = sqlite3.connect(bot_logic.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, link FROM news_archive WHERE title LIKE ? OR summary LIKE ? ORDER BY published_date DESC LIMIT 5", 
            (f'%{query}%', f'%{query}%')
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            await update.message.reply_text(f"'{query}' ile ilgili haber bulunamadı.")
            return

        msg = f"🔍 **'{query}' Sonuçları:**\n\n"
        for title, link in rows:
            msg += f"🔹 [{title}]({link})\n"
            
        await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        await update.message.reply_text(f"Hata: {e}")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/abone komutu"""
    if not context.args:
        await update.message.reply_text("Lütfen RSS URL'si girin. Örn: /abone https://site.com/feed")
        return
        
    url = context.args[0]
    # Basit validasyon
    if not url.startswith('http'):
        await update.message.reply_text("Geçersiz URL.")
        return
        
    if url in bot_logic.rss_urls:
        await update.message.reply_text("Bu kaynak zaten ekli.")
        return
        
    bot_logic.rss_urls.append(url)
    
    # Dosyaya kaydet
    try:
        with open('feeds.json', 'w', encoding='utf-8') as f:
            json.dump(bot_logic.rss_urls, f, indent=4)
        await update.message.reply_text(f"✅ Başarıyla eklendi: {url}")
    except Exception as e:
        await update.message.reply_text(f"Kaydetme hatası: {e}")

async def check_feeds_job(context: ContextTypes.DEFAULT_TYPE):
    """Periyodik haber kontrol işi"""
    chat_id = context.job.chat_id
    
    # Config'i yenile (dosya değişikliklerini al)
    bot_logic.load_config()
    
    news_items = bot_logic.fetch_feeds()
    
    for news in news_items:
        news_hash = bot_logic.get_news_hash(news['title'], news['link'])
        
        if not bot_logic.is_news_sent(news_hash):
            # 1. Filtre Kontrolü
            if not bot_logic.check_filters(news['title'], news['summary']):
                continue
                
            # 2. AI Analizi
            if bot_logic.ai_client:
                analysis = bot_logic.analyze_news(news['title'], news['summary'], news['source'])
                if analysis:
                    news['analysis'] = analysis
            
            # 3. Mesaj Formatı
            # HTML temizliği
            soup = BeautifulSoup(news['summary'], "html.parser")
            clean_summary = soup.get_text(separator=" ", strip=True)[:350] + "..."
            
            msg = (
                f"📰 <b>{news['title']}</b>\n"
                f"ℹ️ <i>{news['source']}</i>\n"
                f"─────────────────────\n"
                f"{clean_summary}\n\n"
                f"🔗 <a href='{news['link']}'>Haberi Oku</a>"
            )
            
            if news.get('analysis'):
                msg += f"\n\n🧠 <b>AI Analizi</b>\n{news['analysis']}"

            # 4. Topic (Konu) Belirleme
            topic_id = None
            category = news.get('category', 'General')
            if category in bot_logic.topics and bot_logic.topics[category]:
                topic_id = bot_logic.topics[category]

            # 5. Gönder
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode='HTML',
                    message_thread_id=topic_id
                )
                
                bot_logic.mark_news_sent(news_hash, news['title'], news['link'])
                bot_logic.save_news_to_db(news, news_hash)
                
                # Rate limit
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Gönderim hatası: {e}")

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    if not token:
        logger.error("Token bulunamadı!")
        return

    # Application oluştur
    application = Application.builder().token(token).build()

    # Komutları ekle
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sonhaberler", latest_news))
    application.add_handler(CommandHandler("ara", search_news))
    application.add_handler(CommandHandler("abone", subscribe))
    application.add_handler(CommandHandler("topicid", get_topic_id))

    # Job Queue (Periyodik kontrol)
    if chat_id:
        job_queue = application.job_queue
        # İlk çalışmada hemen, sonra her 300 saniyede bir (5 dk)
        job_queue.run_repeating(check_feeds_job, interval=300, first=10, chat_id=chat_id)
        logger.info(f"Bot başlatıldı. Hedef Chat ID: {chat_id}")
    else:
        logger.warning("CHAT_ID bulunamadı! Otomatik haber gönderimi çalışmayacak.")

    # Botu çalıştır
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()