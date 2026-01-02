# Multi-Language Greeting Feature

## Overview

The RSS Telegram Bot now supports multi-language greetings and commands in 5 languages:
- 🇬🇧 English (en)
- 🇹🇷 Türkçe (tr)
- 🇪🇸 Español (es)
- 🇷🇺 Русский (ru)
- 🇧🇷 Português (pt)

## Features

### 1. Auto-Detection
When a user first starts the bot with `/start`, their language is automatically detected from their Telegram language settings and saved for future interactions.

### 2. Personalized Greeting
The bot greets each user in their preferred language:

**English:**
```
👋 Hello! I'm the RSS News Bot.

Commands:
/latest - Get the last 5 news items
/search <keyword> - Search in news
/subscribe <url> - Add a new RSS feed
/topicid - Get current topic ID
/setlang - Change language
```

**Türkçe:**
```
👋 Merhaba! Ben RSS Haber Botu.

Komutlar:
/sonhaberler - Son 5 haberi getir
/ara <kelime> - Haberlerde arama yap
/abone <url> - Yeni RSS kaynağı ekle
/topicid - Bulunduğun konunun ID'sini öğren
/dil - Dil değiştir
```

**Español:**
```
👋 ¡Hola! Soy el Bot de Noticias RSS.

Comandos:
/ultimas - Obtener las últimas 5 noticias
/buscar <palabra> - Buscar en noticias
/suscribir <url> - Agregar nueva fuente RSS
/topicid - Obtener ID del tema actual
/idioma - Cambiar idioma
```

**Русский:**
```
👋 Здравствуйте! Я RSS Новостной Бот.

Команды:
/последние - Получить последние 5 новостей
/поиск <слово> - Поиск в новостях
/подписаться <url> - Добавить новый RSS канал
/topicid - Получить ID текущей темы
/язык - Изменить язык
```

**Português:**
```
👋 Olá! Eu sou o Bot de Notícias RSS.

Comandos:
/ultimas - Obter as últimas 5 notícias
/buscar <palavra> - Buscar nas notícias
/assinar <url> - Adicionar nova fonte RSS
/topicid - Obter ID do tópico atual
/lingua - Mudar idioma
```

### 3. Language Switching

Users can change their language preference at any time using the `/setlang` command (or its aliases in other languages).

**Usage:**
```
/setlang          - Show current language and available options
/setlang en       - Switch to English
/setlang tr       - Switch to Turkish
/setlang es       - Switch to Spanish
/setlang ru       - Switch to Russian
/setlang pt       - Switch to Portuguese
```

**Aliases:**
- English: `/setlang`
- Türkçe: `/dil`
- Español: `/idioma`
- Русский: `/язык`
- Português: `/lingua`

### 4. Multi-Language Commands

All major commands have aliases in each supported language:

| Feature | English | Türkçe | Español | Русский | Português |
|---------|---------|---------|---------|---------|-----------|
| Latest News | `/latest` | `/sonhaberler` | `/ultimas` | `/последние` | `/ultimas` |
| Search | `/search` | `/ara` | `/buscar` | `/поиск` | `/buscar` |
| Subscribe | `/subscribe` | `/abone` | `/suscribir` | `/подписаться` | `/assinar` |
| Set Language | `/setlang` | `/dil` | `/idioma` | `/язык` | `/lingua` |

## Technical Implementation

### Database Schema

User language preferences are stored in a new SQLite table:

```sql
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'tr',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Language Detection Flow

1. User sends `/start` command
2. Bot checks if user has a saved language preference
3. If not, detects language from Telegram user settings (`update.effective_user.language_code`)
4. Maps Telegram language code to bot's supported languages
5. Saves the preference in the database
6. Returns greeting and commands in the user's language

### Localization Files

All translations are stored in `locales.json`:

```json
{
  "en": {
    "name": "English",
    "messages": {
      "BOT_GREETING": "👋 Hello! I'm the RSS News Bot.",
      "BOT_COMMANDS": "Commands:\n/latest - ...",
      "CMD_LANGUAGE_SET": "Language set to English!"
    }
  },
  ...
}
```

## Testing

The implementation includes comprehensive tests that validate:
- ✅ Locale loading for all 5 languages
- ✅ User language preference storage and retrieval
- ✅ Message retrieval in all languages
- ✅ Default language (Turkish) for new users
- ✅ Database schema correctness

All tests pass successfully.

## Future Enhancements

Potential improvements for future versions:
- Add more languages (French, German, Italian, etc.)
- Localize news content and AI analysis
- Add language-specific RSS feeds
- Implement inline keyboard for language selection
- Add translation for error messages and system notifications
