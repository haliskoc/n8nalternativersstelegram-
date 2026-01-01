# Architecture / Mimari

## How it Works / Nasıl Çalışır?

This document explains the architecture and data flow of the RSS Telegram Bot.

---

## System Overview / Sistem Genel Bakış

The bot follows this flow:

1. **RSS Feed Fetching:** Fetches news from 30+ sources every 5 minutes
2. **News Processing:** Deduplicates, filters, and formats news items
3. **AI Analysis (Optional):** Analyzes news using OpenRouter AI
4. **Telegram Sending:** Sends formatted messages to your Telegram
5. **Database Storage:** Stores everything in SQLite for history and search

---

## Components / Bileşenler

### `rss_telegram_bot.py`
Main bot logic handling all RSS fetching, processing, and Telegram messaging.

**Key Functions:**
- `fetch_rss_feed()` - Fetches news from all configured RSS sources
- `format_news_message()` - Formats news with HTML for Telegram
- `analyze_news()` - Uses AI to generate insights (optional)
- `send_telegram_message()` - Sends message to Telegram API
- `process_news()` - Main loop that orchestrates everything

### `setup.sh`
One-command installation that:
- Detects your OS (Linux/Mac/Windows)
- Installs Docker automatically (on Linux)
- Configures environment variables
- Sets up RSS feed preferences
- Launches the bot via Docker

### `docker-compose.yml`
Containerizes the bot for easy deployment on any system.

### `locales.json`
Multi-language support (English, Turkish, Spanish, Russian, Portuguese).

### `opml_manager.py`
Import/Export RSS feeds from OPML format (Feedly, Inoreader, etc.).

### `update.sh`
One-command update script that pulls latest code and rebuilds containers.

---

## Database Schema / Veritabanı Şeması

### `sent_news` Table
Tracks which news have been sent (prevents duplicates).

```sql
CREATE TABLE sent_news (
    id INTEGER PRIMARY KEY,
    news_hash TEXT UNIQUE,
    title TEXT,
    link TEXT,
    sent_at TIMESTAMP
)
```

### `news_archive` Table
Full history of all processed news for searching and analysis.

```sql
CREATE TABLE news_archive (
    id INTEGER PRIMARY KEY,
    news_hash TEXT UNIQUE,
    source TEXT,
    category TEXT,
    title TEXT,
    summary TEXT,
    link TEXT,
    published_date TIMESTAMP,
    analysis TEXT,
    created_at TIMESTAMP
)
```

---

## Data Flow / Veri Akışı

```
RSS Sources (30+) 
    ↓
fetch_rss_feed() 
    ↓
Deduplication (SQLite) 
    ↓
HTML Cleanup (BeautifulSoup) 
    ↓
AI Analysis (Optional) 
    ↓
format_news_message() 
    ↓
Telegram Bot API 
    ↓
Your Telegram Channel/Chat
    ↓
Database (News Archive)
```

---

## Configuration / Konfigürasyon

All settings are in `.env`:

```env
TELEGRAM_TOKEN=your_bot_token
CHAT_ID=your_chat_id
OPENROUTER_API_KEY=your_ai_api_key (optional)
OPENROUTER_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
```

---

## Performance / Performans

- **Check Interval:** 5 minutes (configurable)
- **HTML Cleanup:** Uses BeautifulSoup for safe parsing
- **Deduplication:** O(1) lookup via SQLite UNIQUE constraint
- **AI Analysis:** Only runs if API key is provided
- **Message Format:** HTML mode for rich formatting
- **Rate Limiting:** 2-second delay between messages to respect Telegram API limits

---

## Extensibility / Genişletilebilirlik

To add new features:

1. **New RSS Sources:** Edit `rss_urls` in `rss_telegram_bot.py`
2. **New Languages:** Add to `locales.json`
3. **Custom Filtering:** Modify `process_news()` method
4. **Custom Formatting:** Modify `format_news_message()` method
5. **Additional AI Prompts:** Modify `analyze_news()` system prompt

