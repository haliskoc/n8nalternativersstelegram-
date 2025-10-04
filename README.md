# 🤖 Multi-Source RSS Telegram Bot

A Telegram bot that automatically tracks RSS feeds from 30+ websites including technology, science, and economics news.

## ✨ Features

- **30+ Websites**: Technology, science, economics, and research news
- **5-Minute Check Interval**: Always up-to-date news
- **Duplicate Prevention**: Won't send the same news twice
- **Source Display**: Shows which site each news comes from
- **Low Resource Usage**: Only 30 MB RAM, 3% CPU

## 📰 Tracked Websites

### 💻 Technology
- TechCrunch, WIRED, TechRepublic
- Computer Weekly, Ars Technica
- The Verge, Engadget
- Webtekno, Technopat, ShiftDelete

### 🔬 Science & Research
- Scientific American, Science (AAAS)
- ScienceDaily, MIT News
- NASA, The Conversation
- Futurism

### 💰 Economics & Finance
- Trading Economics, MarketWatch
- Federal Reserve, CEPR
- BNP Paribas Economic Research

### 🇹🇷 Turkish Technology
- Donanım Günlüğü, PC Hocası
- Teknoblog, Megabayt, Sözcü

## 🚀 Quick Setup

### 1. Create Telegram Bot
1. Talk to [@BotFather](https://t.me/botfather) on Telegram
2. Type `/newbot`
3. Choose a bot name (e.g., "Tech News Bot")
4. Choose a bot username (e.g., "tech_news_bot")
5. **Copy and save the token**

### 2. Get Chat ID
1. Talk to [@userinfobot](https://t.me/userinfobot)
2. **Copy and save your Chat ID**

### 3. Download Project
```bash
git clone https://github.com/username/rss-telegram-bot.git
cd rss-telegram-bot
```

### 4. Run with Python
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_TOKEN="your_bot_token_here"
export CHAT_ID="your_chat_id_here"

# Start the bot
python3 rss_telegram_bot.py
```

### 5. Run with Docker
```bash
# Set environment variables
export TELEGRAM_TOKEN="your_bot_token_here"
export CHAT_ID="your_chat_id_here"

# Run with Docker
docker-compose up -d
```

## 🔧 Detailed Setup

### Requirements
- Python 3.8+ or Docker
- Telegram account

### Manual Installation
```bash
# 1. Clone the project
git clone https://github.com/username/rss-telegram-bot.git
cd rss-telegram-bot

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export TELEGRAM_TOKEN="your_bot_token_here"
export CHAT_ID="your_chat_id_here"

# 5. Start the bot
python3 rss_telegram_bot.py
```

### Running on Server
```bash
# Run in background
nohup python3 rss_telegram_bot.py > bot.log 2>&1 &

# Check status
ps aux | grep python

# View logs
tail -f bot.log
```

## 📊 Resource Usage
- **RAM**: ~30 MB
- **CPU**: ~3%
- **Storage**: ~50 MB
- **Network**: Minimal

## 🛠️ Configuration

### Environment Variables
- `TELEGRAM_TOKEN`: Telegram bot token
- `CHAT_ID`: Target chat ID

### Bot Settings
- Check interval: 5 minutes
- News age: 24 hours
- Maximum summary: 300 characters

## 📁 Project Structure

```
rss-telegram-bot/
├── rss_telegram_bot.py    # Main bot code
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image
├── docker-compose.yml    # Docker Compose
├── env.example          # Environment variables example
├── .gitignore           # Git ignore
├── LICENSE              # MIT License
└── README.md            # This file
```

## 🛠️ Development

### Adding New RSS Feed
Add new URL to the `rss_urls` list in `rss_telegram_bot.py`.

### Adding Site Name
Add new site to the `site_names` dictionary in the `get_site_name()` function.

## 📄 License

MIT License - Feel free to use and modify.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## 📞 Support

Use GitHub Issues for problems and questions.

## 🔧 Troubleshooting

### Bot Not Sending Messages
1. Check if bot token is correct
2. Verify chat ID is correct
3. Make sure bot is started in the chat
4. Check logs for errors

### RSS Feed Not Working
1. Verify RSS URL is correct
2. Check firewall settings
3. Review logs for errors

### Container Not Starting
1. Make sure Docker is running
2. Check if port 8080 is available
3. Review logs: `docker-compose logs`