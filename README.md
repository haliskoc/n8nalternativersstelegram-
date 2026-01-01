# 🤖 RSS Telegram Bot

**Your Personal News Assistant / Kişisel Haber Asistanınız**

This bot automatically tracks news from 30+ websites (Technology, Science, Economics) and sends them to your Telegram channel. It can also analyze news using AI!

Bu bot, 30'dan fazla web sitesinden (Teknoloji, Bilim, Ekonomi) haberleri otomatik olarak takip eder ve Telegram kanalınıza gönderir. Ayrıca yapay zeka kullanarak haberleri analiz edebilir!

---

## ✨ Features / Özellikler

- �� **30+ Sources:** TechCrunch, WIRED, NASA, Science, and more.
- ⚡ **Instant Updates:** Checks for news every 5 minutes.
- 🤖 **AI Analysis:** Detailed insights and summaries for each news item (Optional).
- 📊 **Daily Summary:** A neat summary of the day's news at 18:35.
- 🇹🇷 **Turkish & English:** Supports both international and local sources.

---

## 🚀 Super Easy Setup / Çok Kolay Kurulum

You don't need to know any code! Just follow these 3 steps.
Kod bilmenize gerek yok! Sadece bu 3 adımı takip edin.

### 1. Get Your Keys / Anahtarlarınızı Alın
Before starting, you need two things from Telegram:
Başlamadan önce Telegram'dan iki şeye ihtiyacınız var:

1.  **Bot Token:** Talk to [@BotFather](https://t.me/botfather), create a new bot (`/newbot`), and copy the **API Token**.
2.  **Chat ID:** Talk to [@userinfobot](https://t.me/userinfobot) and copy your **ID**.

*(Optional) For AI features, get a free key from [OpenRouter](https://openrouter.ai/).*
*(İsteğe bağlı) AI özellikleri için [OpenRouter](https://openrouter.ai/) adresinden ücretsiz bir anahtar alın.*

### 2. Download & Run / İndir ve Çalıştır

Open your terminal and run these commands:
Terminalinizi açın ve şu komutları çalıştırın:

```bash
# 1. Clone the project / Projeyi indirin
git clone https://github.com/haliskoc/n8nalternativersstelegram-.git
cd n8nalternativersstelegram-

# 2. Run the setup script / Kurulum scriptini çalıştırın
chmod +x setup.sh
sudo ./setup.sh
```

### 3. Follow the Script / Scripti Takip Edin
The script will ask you for your language (English/Turkish) and your keys. Just enter them and press Enter. That's it!
Script size dilinizi (İngilizce/Türkçe) ve anahtarlarınızı soracak. Sadece girin ve Enter'a basın. Bu kadar!

### 🗑️ Uninstall / Kaldırma
If you want to remove everything installed by the bot:
Bot tarafından kurulan her şeyi kaldırmak isterseniz:
```bash
chmod +x cleanup.sh
sudo ./cleanup.sh
```

---

<details>
<summary>🛠️ <b>Advanced / Manual Setup (Click to Expand)</b></summary>

If you prefer to set up everything manually or want to know how it works under the hood.

### Requirements
- Docker & Docker Compose
- Or Python 3.8+

### Manual Docker Setup
1. Create a `.env` file:
   ```bash
   cp env.example .env
   ```
2. Edit `.env` and add your keys:
   ```
   TELEGRAM_TOKEN=your_token
   CHAT_ID=your_id
   OPENROUTER_API_KEY=your_key (optional)
   ```
3. Run with Docker Compose:
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
