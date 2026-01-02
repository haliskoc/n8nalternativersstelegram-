# 🤖 RSS Telegram Bot - AI Powered News Assistant

<p align="center">
  <img src="image.png" alt="RSS Telegram Bot Banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Docker-Supported-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-OpenRouter-orange.svg" alt="AI Powered">
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Quick Start](#️-quick-start)
- [Configuration](#-configuration)
- [Management (CLI Tool)](#-management-the-cli-tool)
- [Project Structure](#-project-structure)
- [Advanced Usage](#-advanced-usage)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Uninstallation](#️-uninstallation)
- [License](#-license)

---

## 🌟 Overview

**RSS Telegram Bot** is an open-source, transparent, and community-driven news automation tool designed to keep you updated with the latest from your favorite sources. Optimized for **Oracle Cloud Free Tier**, it fetches news from 30+ global sources, analyzes them using state-of-the-art AI, and delivers them straight to your Telegram channel.

This project emphasizes **transparency and documentation** to ensure users understand exactly how their news is processed, filtered, and delivered—preventing any "black box" behavior.

### 🚀 Key Features

- 🌐 **30+ Pre-configured Sources:** TechCrunch, WIRED, NASA, Science, and many more.
- 🤖 **AI-Powered Analysis:** Automatically summarizes and provides insights for each news item using OpenRouter (Gemini, Claude, GPT).
- 📊 **Daily Excel Reports:** Generates a neat summary of the day's news in `.xlsx` format.
- 🌍 **Multi-language Support:** Full support for **English, Türkçe, Español, Русский, and Português**.
- ⚡ **Instant Updates:** Smart polling system checks for new content every 5 minutes.
- 🧹 **Smart Deduplication:** Uses SQLite to ensure you never see the same news twice.
- 🛠️ **Unified CLI Manager:** A powerful command-line tool (`rsstelegram`) to manage everything.
- 🐳 **Docker Ready:** One-command deployment with Docker Compose.
- 📖 **Fully Transparent:** Open-source code with comprehensive documentation to prevent "black box" behavior.

---

## 🔍 How It Works

Understanding how your news bot operates is crucial for trust and customization. Here's a transparent breakdown of the entire process:

### Data Flow Pipeline

```
RSS Sources (30+) 
    ↓
[1. Fetch] - Every 5 minutes, fetch RSS feeds
    ↓
[2. Parse] - Extract title, link, description, publish date
    ↓
[3. Hash] - Generate unique hash (SHA-256) for deduplication
    ↓
[4. Check Database] - Query SQLite to see if already sent
    ↓
[5. Filter] - Apply whitelist/blacklist keyword filters (optional)
    ↓
[6. Clean HTML] - Remove tags and format text using BeautifulSoup
    ↓
[7. AI Analysis] - Generate insights using OpenRouter API (optional)
    ↓
[8. Format] - Create Telegram-compatible HTML message
    ↓
[9. Send] - Post to Telegram using Bot API
    ↓
[10. Store] - Save to SQLite archive for history
    ↓
[11. Excel Export] - Add to daily report (news_daily.xlsx)
```

### Core Components

1. **RSS Feed Parser** (`feedparser` library)
   - Fetches and parses RSS/Atom feeds
   - Handles various feed formats automatically
   - Timeout protection: 30 seconds per feed

2. **SQLite Database** (`news_bot.db`)
   - **`sent_news` table**: Tracks sent items (prevents duplicates)
   - **`news_archive` table**: Full searchable history of all news
   - Hash-based deduplication using SHA-256

3. **AI Analysis Engine** (Optional)
   - Uses OpenRouter API (supports 200+ models)
   - Default: `google/gemini-2.0-flash-lite-preview-02-05:free`
   - Generates summaries and insights
   - Only runs if `OPENROUTER_API_KEY` is set

4. **Telegram Bot API** (`python-telegram-bot` v20.8)
   - Sends formatted messages using HTML mode
   - Rate limiting: 2-second delay between messages
   - Supports rich formatting (bold, italic, links, code blocks)

5. **Job Scheduler**
   - Checks feeds every 5 minutes
   - Daily report generation at midnight
   - Automatic database cleanup for old entries

### Security & Privacy

- **No external analytics**: Zero tracking or telemetry
- **Local-first**: All data stored locally in SQLite
- **API keys**: Stored in environment variables (never in code)
- **Open source**: Every line of code is auditable
- **No third-party services**: Except Telegram and OpenRouter (optional)

For detailed technical architecture, see [docs/architecture.md](docs/architecture.md).

---

## 🛠️ Quick Start

### Prerequisites

Before installation, gather these credentials:

1. **Telegram Bot Token:** 
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the prompts
   - Copy the token (format: `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`)

2. **Chat ID:** 
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - Copy your Chat ID (format: `123456789` or `-1001234567890` for groups)

3. **OpenRouter API Key (Optional - for AI features):**
   - Visit [OpenRouter.ai](https://openrouter.ai/)
   - Sign up and generate an API key
   - Get free credits or use free models

### Installation

**Automated Setup (Recommended):**

```bash
# Clone the repository
git clone https://github.com/haliskoc/n8nalternativersstelegram-.git
cd n8nalternativersstelegram-

# Run the interactive setup wizard
chmod +x setup.sh
sudo ./setup.sh
```

The setup wizard will:
1. Detect your OS (Linux/macOS/Windows)
2. Install Docker and Docker Compose (if needed)
3. Guide you through language selection
4. Configure API keys and credentials
5. Let you choose from 30+ RSS sources
6. Start the bot automatically

**Docker Deployment:**

If you already have Docker installed:

```bash
# Create .env file
cp env.example .env
nano .env  # Edit with your credentials

# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f
```

**Manual Python Setup:**

For development or custom deployments:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_TOKEN="your_bot_token"
export CHAT_ID="your_chat_id"
export OPENROUTER_API_KEY="your_openrouter_key"  # Optional

# Run the bot
python3 rss_telegram_bot.py
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: Telegram Bot Configuration
TELEGRAM_TOKEN=110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
CHAT_ID=123456789

# Optional: AI Analysis Configuration
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_MODEL=google/gemini-2.0-flash-lite-preview-02-05:free
```

### Configuration Files

All configuration is stored in JSON files for easy editing:

#### `feeds.json` - RSS Feed List

```json
[
  {
    "name": "TechCrunch",
    "url": "https://techcrunch.com/feed/",
    "category": "Technology"
  },
  {
    "name": "WIRED",
    "url": "https://www.wired.com/feed/rss",
    "category": "Technology"
  }
]
```

#### `filters.json` - Keyword Filters (Optional)

```json
{
  "whitelist": ["AI", "machine learning", "cybersecurity"],
  "blacklist": ["cryptocurrency", "NFT"]
}
```

- **Whitelist**: Only send news containing these keywords
- **Blacklist**: Never send news containing these keywords
- Empty arrays = no filtering

#### `topics.json` - Topic Categories (Optional)

```json
{
  "Technology": "🖥️",
  "Science": "🔬",
  "Business": "💼",
  "Sports": "⚽"
}
```

Maps categories to emoji prefixes for visual organization.

### Available OpenRouter Models

The bot supports 200+ AI models. Popular free options:

- `google/gemini-2.0-flash-lite-preview-02-05:free` (Default, Fast)
- `meta-llama/llama-3.2-3b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

See [OpenRouter Models](https://openrouter.ai/models) for the full list.

---

## 🎮 Management (The CLI Tool)

Once installed, manage your bot using the `rsstelegram` command:

```bash
sudo rsstelegram
```

This interactive menu provides:

### Feed Management
- **Add Feed**: Enter RSS/Atom URL, name, and category
- **Remove Feed**: Delete feeds by name or URL
- **List Feeds**: View all configured sources
- **Search Feeds**: Find feeds by keyword or category
- **Import OPML**: Bulk import from Feedly, Inoreader, etc.
- **Export OPML**: Backup your feed list

### Bot Control
- **Start Bot**: Launch the RSS monitoring service
- **Stop Bot**: Gracefully shut down the bot
- **Restart Bot**: Apply configuration changes
- **View Logs**: Real-time log streaming
- **Status Check**: See if bot is running and stats

### Settings
- **Update API Keys**: Change Telegram or OpenRouter credentials
- **Configure Filters**: Set whitelist/blacklist keywords
- **Change Language**: Switch between EN, TR, ES, RU, PT
- **Set Check Interval**: Adjust RSS polling frequency (default: 5 min)

### Maintenance
- **Update Bot**: Pull latest code and rebuild containers
- **Database Backup**: Export SQLite database
- **Clear History**: Clean old news from database
- **View Statistics**: News count, sources, AI usage

---

## 📂 Project Structure

```
n8nalternativersstelegram-/
├── rss_telegram_bot.py      # Core bot engine (600+ lines)
│   ├── RSSNewsBot class     # Main bot logic
│   ├── fetch_rss_feed()     # RSS fetching and parsing
│   ├── analyze_news()       # AI analysis integration
│   ├── format_news_message()# Telegram HTML formatting
│   └── process_news()       # Main processing loop
│
├── rsstelegram.sh           # Unified CLI management tool (217 lines)
│   └── Interactive menu for all bot operations
│
├── setup.sh                 # Multi-language installer (560 lines)
│   ├── OS detection (Linux/macOS/Windows)
│   ├── Docker installation
│   ├── API key configuration
│   └── Feed selection wizard
│
├── update.sh                # One-command update script
├── update_feeds.sh          # Feed database updater (253 lines)
├── uninstall.sh             # Clean removal script
│
├── opml_manager.py          # OPML import/export utility (133 lines)
├── generate_feeds_db.py     # Feed database generator (104 lines)
│
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # Bot container definition
├── requirements.txt         # Python dependencies
│
├── feeds.json               # Your RSS feed list (user-editable)
├── feeds_db.txt             # 30+ pre-configured feeds
├── filters.json             # Keyword filters (optional)
├── topics.json              # Category emoji mappings
├── locales.json             # Multi-language translations (600+ strings)
│
├── docs/
│   └── architecture.md      # Detailed technical documentation
│
└── Database (auto-generated):
    ├── news_bot.db          # SQLite database
    │   ├── sent_news        # Deduplication tracking
    │   └── news_archive     # Full news history
    └── daily_news.xlsx      # Daily Excel reports
```

### Key Files Explained

**`rss_telegram_bot.py`** - The heart of the system
- Fetches RSS feeds using `feedparser`
- Deduplicates using SHA-256 hashing
- Cleans HTML with `BeautifulSoup`
- Sends to Telegram using `python-telegram-bot`
- Stores in SQLite for history

**`rsstelegram.sh`** - Your control center
- Bash script providing interactive menu
- Manages Docker containers
- Edits configuration files
- Views logs and statistics

**`locales.json`** - Full i18n support
- All UI strings in 5 languages
- Easy to add new languages
- Community contributions welcome

**Database Schema:**
```sql
-- Prevents sending duplicate news
CREATE TABLE sent_news (
    id INTEGER PRIMARY KEY,
    news_hash TEXT UNIQUE,
    title TEXT,
    link TEXT,
    sent_at TIMESTAMP
);

-- Full searchable archive
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
);
```

---

## 🚀 Advanced Usage

### Adding Custom RSS Feeds

**Method 1: Using CLI (Recommended)**
```bash
sudo rsstelegram
# Select "Add Feed" from menu
# Enter URL, name, and category
```

**Method 2: Edit `feeds.json` Directly**
```json
[
  {
    "name": "Your Blog",
    "url": "https://yourblog.com/feed.xml",
    "category": "Personal"
  }
]
```

### Custom AI Prompts

Edit `rss_telegram_bot.py` to customize AI analysis:

```python
def analyze_news(self, title, summary):
    prompt = f"""
    Analyze this news and provide:
    1. A one-sentence summary
    2. Key impact points
    3. Related topics
    
    Title: {title}
    Summary: {summary}
    """
```

### Filtering Examples

**Whitelist: Only tech and AI news**
```json
{
  "whitelist": ["AI", "artificial intelligence", "machine learning", "neural network", "GPT"],
  "blacklist": []
}
```

**Blacklist: Avoid political content**
```json
{
  "whitelist": [],
  "blacklist": ["election", "politics", "parliament", "senate"]
}
```

### Schedule Customization

Edit `rss_telegram_bot.py` to change check frequency:

```python
# Change from 5 minutes to 10 minutes
job_queue.run_repeating(
    self.check_feeds_job, 
    interval=600,  # seconds (600 = 10 minutes)
    first=10
)
```

### Multiple Telegram Destinations

To send to multiple channels, modify the `.env`:

```env
CHAT_ID=123456789,-1001234567890  # Comma-separated
```

Or use multiple bot instances with different configurations.

---

## 🔧 Troubleshooting

### Bot Not Starting

**Problem**: `docker-compose up -d` fails  
**Solution**:
```bash
# Check Docker is running
docker --version
sudo systemctl start docker

# Check logs for errors
docker-compose logs
```

**Problem**: "Invalid token" error  
**Solution**: Verify your Telegram token format:
- Must start with numbers, contain `:`, and have 35+ characters
- Get a new token from [@BotFather](https://t.me/botfather)

### No News Received

**Problem**: Bot running but no messages  
**Solution**:
```bash
# Check bot logs
docker-compose logs -f

# Verify feeds are valid
python3 -c "import feedparser; print(feedparser.parse('YOUR_FEED_URL').entries[0])"

# Test Telegram connection
curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage \
  -d chat_id=<YOUR_CHAT_ID> \
  -d text="Test message"
```

### AI Analysis Not Working

**Problem**: News sent but no AI insights  
**Solution**:
- Verify `OPENROUTER_API_KEY` is set in `.env`
- Check API key is valid at [OpenRouter Dashboard](https://openrouter.ai/keys)
- Ensure you have credits or are using a free model
- Check logs: `docker-compose logs | grep -i "ai"`

### Database Issues

**Problem**: "Database locked" errors  
**Solution**:
```bash
# Stop bot
docker-compose down

# Check database integrity
sqlite3 news_bot.db "PRAGMA integrity_check;"

# Restart bot
docker-compose up -d
```

### Memory/CPU Issues

**Problem**: High resource usage on Oracle Cloud  
**Solution**:
```bash
# Reduce check frequency (edit rss_telegram_bot.py)
interval=900  # 15 minutes instead of 5

# Disable AI analysis
# Remove OPENROUTER_API_KEY from .env

# Limit number of feeds
# Keep only essential feeds in feeds.json
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'telegram'` | Missing dependencies | `pip install -r requirements.txt` |
| `sqlite3.OperationalError: database is locked` | Multiple bot instances | Stop duplicate processes |
| `telegram.error.Unauthorized: Forbidden` | Wrong bot token | Regenerate token from @BotFather |
| `openai.APIError: Invalid API key` | Wrong OpenRouter key | Verify at openrouter.ai/keys |
| `feedparser.exceptions: URLError` | Network/firewall issues | Check internet, RSS URL |

---

## 🤝 Contributing

We welcome community contributions! This project thrives on transparency and collaboration.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-idea`
3. **Make your changes**: Follow existing code style
4. **Test thoroughly**: Ensure bot starts and works
5. **Document changes**: Update README if needed
6. **Submit a Pull Request**: Clear description of changes

### Contribution Ideas

- 🌐 Add new language translations to `locales.json`
- 📰 Contribute more RSS feeds to `feeds_db.txt`
- 🐛 Fix bugs or improve error handling
- 📚 Improve documentation
- ✨ Add new features (filters, formatters, AI prompts)
- 🧪 Add unit tests
- 🎨 Improve CLI interface

### Code Style

- Follow PEP 8 for Python code
- Add comments for complex logic
- Use descriptive variable names
- Keep functions focused and small
- Document all configuration options

### Reporting Issues

Found a bug? Have a suggestion?

1. Check existing [Issues](https://github.com/haliskoc/n8nalternativersstelegram-/issues)
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs (if applicable)
   - Your environment (OS, Python version, Docker version)

---

## 🗑️ Uninstallation

To completely remove the bot and all its data:

```bash
chmod +x uninstall.sh
sudo ./uninstall.sh
```

This will:
- Stop all running containers
- Remove Docker images
- Delete the project directory
- Clean up the `rsstelegram` command
- Preserve your configuration (optional backup prompt)

**Manual Cleanup (if needed):**
```bash
# Stop and remove containers
docker-compose down -v

# Remove Docker images
docker rmi n8nalternativersstelegram-_rss-bot

# Remove project directory
cd ..
rm -rf n8nalternativersstelegram-

# Remove CLI command
sudo rm /usr/local/bin/rsstelegram
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What This Means

✅ **You can:**
- Use this commercially
- Modify the code
- Distribute copies
- Use privately
- Sublicense

❌ **You must:**
- Include the original license
- Include copyright notice

❌ **No warranty:**
- Provided "as-is" without warranty
- Authors not liable for damages

---

## 🙏 Acknowledgments

- **Telegram Bot API**: For the excellent bot platform
- **OpenRouter**: For democratizing AI access
- **FeedParser**: For robust RSS/Atom parsing
- **Community Contributors**: For translations, feeds, and improvements

---

## 📞 Support & Community

- **Issues**: [GitHub Issues](https://github.com/haliskoc/n8nalternativersstelegram-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/haliskoc/n8nalternativersstelegram-/discussions)
- **Email**: Create an issue for support

---

## 🔐 Security & Privacy

This project takes security and privacy seriously:

- **No tracking**: Zero analytics or telemetry
- **Local-first**: All data stored on your machine
- **No backdoors**: Every line of code is open source
- **API keys**: Stored in environment variables only
- **Minimal permissions**: Bot only needs message sending
- **Regular updates**: Security patches applied promptly

**Found a security vulnerability?** Please email the maintainer directly or create a private security advisory.

---

## 📊 Project Statistics

- **Lines of Code**: ~2,400
- **Languages**: Python, Bash
- **Dependencies**: 7 Python packages
- **Pre-configured Feeds**: 30+
- **Supported Languages**: 5 (EN, TR, ES, RU, PT)
- **License**: MIT
- **Docker Support**: ✅
- **Free Tier Compatible**: Oracle Cloud, AWS, GCP

---

<p align="center">
  Made with ❤️ for the community | Open Source | Community Driven
</p>

<p align="center">
  <strong>Transparent. Documented. No Black Boxes.</strong>
</p>
