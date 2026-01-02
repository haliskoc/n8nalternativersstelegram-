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

## 🌟 Overview

**RSS Telegram Bot** is a sophisticated, multi-language news automation tool designed to keep you updated with the latest from your favorite sources. Optimized for **Oracle Cloud Free Tier**, it fetches news from 30+ global sources, analyzes them using state-of-the-art AI, and delivers them straight to your Telegram channel.

### 🚀 Key Features

- 🌐 **30+ Pre-configured Sources:** TechCrunch, WIRED, NASA, Science, and many more.
- 🤖 **AI-Powered Analysis:** Automatically summarizes and provides insights for each news item using OpenRouter (Gemini, Claude, GPT).
- 📊 **Daily Excel Reports:** Generates a neat summary of the day's news in `.xlsx` format.
- 🌍 **Multi-language Support:** Full support for **English, Türkçe, Español, Русский, and Português**.
- ⚡ **Instant Updates:** Smart polling system checks for new content every 5 minutes.
- 🧹 **Smart Deduplication:** Uses SQLite to ensure you never see the same news twice.
- 🛠️ **Unified CLI Manager:** A powerful command-line tool (`rsstelegram`) to manage everything.
- 🐳 **Docker Ready:** One-command deployment with Docker Compose.

---

## 🛠️ Quick Start

### 1. Prerequisites
You will need:
1.  **Telegram Bot Token:** Get it from [@BotFather](https://t.me/botfather).
2.  **Chat ID:** Get it from [@userinfobot](https://t.me/userinfobot).
3.  *(Optional)* **OpenRouter API Key:** For AI features, get one at [OpenRouter.ai](https://openrouter.ai/).

### 2. Installation

Run the following command in your terminal:

```bash
# Clone the repository
git clone https://github.com/haliskoc/n8nalternativersstelegram-.git
cd n8nalternativersstelegram-

# Run the interactive setup wizard
chmod +x setup.sh
sudo ./setup.sh
```

The setup wizard will guide you through language selection, API key configuration, and RSS source selection.

---

## 🎮 Management (The CLI Tool)

Once installed, you can manage your bot using the `rsstelegram` command:

```bash
sudo rsstelegram
```

This interactive menu allows you to:
- 📰 **Manage Feeds:** Add, remove, or search for RSS feeds.
- 🔄 **OPML Support:** Import your existing feed lists or export your current ones.
- 🤖 **Bot Control:** Start, stop, restart, and view live logs.
- ⚙️ **Settings:** Update your API keys and configuration on the fly.
- ⬆️ **Auto-Update:** Keep your bot up to date with a single click.

---

## 📂 Project Structure

- `rss_telegram_bot.py`: The core engine of the bot.
- `rsstelegram.sh`: The unified CLI management tool.
- `setup.sh`: Interactive multi-language installation script.
- `locales.json`: Translation files for the UI and messages.
- `feeds.json`: Your personalized list of RSS sources.
- `aweomsrss/`: A curated collection of hundreds of OPML files categorized by country and topic.

---

## 🗑️ Uninstallation

If you wish to remove the bot and all its data:

```bash
chmod +x uninstall.sh
sudo ./uninstall.sh
```
*This will safely stop containers, remove images, and clean up the project directory.*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for the community.
</p>
   ```bash
   docker-compose up -d
   ```

### Manual Python Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   ```bash
   export TELEGRAM_TOKEN="your_token"
   export CHAT_ID="your_id"
   ```
3. Run the bot:
   ```bash
   python3 rss_telegram_bot.py
   ```

</details>
