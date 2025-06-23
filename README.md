<div dir="ltr" align=center>
    
[**English**](README_ru.md) / [**فارسی 🇮🇷**](README_fa.md)

</div>
<br>

# 🤖 SANA Bot (Self Analysis via Neural AI)

<p align="center">
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?logo=telegram&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/OpenRouter-1E90FF">
  <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white">
  <img src="https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white">
</p>

**SANA** is an AI-powered Telegram bot for psychological self-assessment. Create custom personality tests and receive AI-generated analysis reports.

## 🚀 Quick Setup

### Prerequisites
- Ubuntu/Debian OS
- Python 3.10+
- [OpenRouter](https://openrouter.ai) account (free API key)

### 🔧 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/aliazizi-code/Sana-Mind-Bot.git
cd Sana-Mind-Bot

# 2. Create config file
echo '# Redis
REDIS_HOST="localhost"
REDIS_BROKER='redis://localhost:6379/0'
REDIS_BACKEND='redis://localhost:6379/1'

# Bot
BOT_TOKEN="YOUR_BOT_TOKEN"

# OpenRouter
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxx"
OPENROUTER_MODEL="deepseek/deepseek-chat:free"' > .env

# 3. Update server & install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y sqlite3 python3-venv

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install libraries
pip install -r requirements.txt

# 6. Run bot and Celery (in separate terminals)
celery -A tasks.celery_config.celery_app worker --loglevel=info
python main.py
```

### ⚙️ Set Admin User
After starting the bot, execute:
```bash
sqlite3 telegram_bot.db "UPDATE users SET is_admin = 1 WHERE telegram_id = YOUR_TELEGRAM_ID;"
```

## 🧠 Creating New Tests
1. As admin, send command in Telegram:
```
/create_test
```
2. Follow interactive setup  
3. Tests become immediately available to users

## ⚠️ Important Notes
- **Test Limits:** Max 50 tests/day (OpenRouter free tier)
- **Queueing:** Tests processed with time intervals via Celery
- **Customization:** Modify `prompts.py` to adjust AI responses

## 📌 Key Features
- ✅ Create multi-choice psychological tests
- ✅ AI-powered response analysis
- ✅ Admin test management panel
- ✅ Advanced queueing system
- ✅ SQLite data storage

---

**Professional Design with** ✨  
`SANA - Self Analysis via Neural AI`  
*Version 1.0 | June 2025*
