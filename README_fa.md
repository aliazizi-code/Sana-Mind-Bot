<div dir="ltr" align=center>
    
[**English**](README_ru.md) / [**فارسی 🇮🇷**](README_fa.md)

</div>
<br>

### README فارسی (فارسی)

<div dir="rtl">

# 🤖 ربات خودشناسی SANA (تحلیل شخصیت با هوش مصنوعی)

<p align="center">
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?logo=telegram&logoColor=white">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/OpenRouter-1E90FF">
  <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white">
  <img src="https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white">
</p>

**SANA** یک ربات تلگرامی هوشمند برای خودشناسی و تحلیل شخصیت با استفاده از تست‌های روانشناسی مبتنی بر هوش مصنوعی. کاربران می‌توانند تست‌های سفارشی ایجاد کرده و نتایج تحلیلی دریافت کنند.

## 🚀 راه‌اندازی سریع

### پیش‌نیازها
- سیستم‌عامل Ubuntu/Debian
- Python 3.10+
- حساب [OpenRouter](https://openrouter.ai) (دریافت API Key رایگان)

### 🔧 مراحل نصب

```bash
# 1. کلون پروژه
git clone https://github.com/aliazizi-code/Sana-Mind-Bot.git
cd Sana-Mind-Bot

# 2. ایجاد فایل تنظیمات
echo '# Redis
REDIS_HOST="localhost"
REDIS_BROKER='redis://localhost:6379/0'
REDIS_BACKEND='redis://localhost:6379/1'

# Bot
BOT_TOKEN="YOUR_BOT_TOKEN"

# OpenRouter
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxx"
OPENROUTER_MODEL="deepseek/deepseek-chat:free"' > .env

# 3. به‌روزرسانی سرور و نصب پیش‌نیازها
sudo apt update && sudo apt upgrade -y
sudo apt install -y sqlite3 python3-venv

# 4. راه‌اندازی محیط مجازی
python3 -m venv venv
source venv/bin/activate

# 5. نصب کتابخانه‌ها
pip install -r requirements.txt

# 6. اجرای ربات و سلری (در دو ترمینال مجزا)
celery -A tasks.celery_config.celery_app worker --loglevel=info
python main.py
```

### ⚙ تنظیم کاربر ادمین
پس از اجرا و استارت ربات در تلگرام، دستور زیر را اجرا کنید:
```bash
sqlite3 telegram_bot.db "UPDATE users SET is_admin = 1 WHERE telegram_id = YOUR_TELEGRAM_ID;"
```

## 🧠 ساخت تست جدید
1. در ربات به عنوان ادمین دستور زیر را وارد کنید:
```
/create_test
```
2. مراحل ساخت تست را دنبال کنید  
3. تست ساخته شده برای کاربران قابل استفاده خواهد بود

## ⚠️ نکات مهم
- **محدودیت تست‌ها:** حداکثر ۵۰ تست در روز (به دلیل محدودیت نسخه رایگان OpenRouter)
- **صف‌بندی:** تست‌ها با فاصله زمانی توسط Celery پردازش می‌شوند
- **شخصی‌سازی:** فایل `prompts.py` را برای تنظیم پاسخ‌های هوش مصنوعی ویرایش کنید

## 📌 امکانات کلیدی
- ✅ ساخت تست‌های روانشناسی چندگزینه‌ای
- ✅ تحلیل پاسخ‌ها با هوش مصنوعی
- ✅ پنل مدیریت برای تست‌ها
- ✅ پشتیبانی از صف‌بندی پیشرفته
- ✅ سیستم ذخیره‌سازی داده‌ها در SQLite

</div>

---




**طراحی حرفه‌ای با** ✨  
`SANA - Self Analysis via Neural AI`  
*نسخه ۱.۰ | ژوئن ۲۰۲۵*