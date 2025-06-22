import os
import requests
import asyncio
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from AI.prompt import prompt
from tasks.celery_config import celery_app, redis_conn
from db.models import UserResult, User
from db.session import SessionLocal
from datetime import datetime, timedelta
from bot.bot_messages import analysis_ready_msg


logger = logging.getLogger(__name__)

load_dotenv()
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")


@celery_app.task(bind=True, rate_limit="10/s", max_retries=10, default_retry_delay=300)
def get_ai_analysis(self, test_name: str, qa_pairs: str, telegram_id: int, test_id: int):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    count_key = f"daily_count:{today}"
    
    if redis_conn.get(count_key) is None:
        now = datetime.utcnow()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        ttl = int((midnight - now).total_seconds())
        redis_conn.setex(count_key, ttl, 0)
        
    current_count = redis_conn.incr(count_key)
    if current_count > 50:
        now = datetime.utcnow()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delay_seconds = (midnight - now).total_seconds()
        logger.info(f"[{today}] حداکثر تعداد درخواست روزانه رسیده. تسک برای {delay_seconds} ثانیه دیگر زمان‌بندی می‌شود.")
        
        raise self.retry(countdown=delay_seconds, max_retries=10)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt(qa_pairs, test_name)}],
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        user_result = UserResult(user_id=user.id , test_id=test_id, result_text=result)
        db.add(user_result)
        db.commit()
        db.close()
        
        bot = Bot(token=os.getenv("BOT_TOKEN"))
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('مشاهده نتیجه 📄', callback_data=f"show_result:{test_id}")]
        ])
        asyncio.run(
            bot.send_message(
            chat_id=telegram_id,
            reply_markup=keyboard,
            text=analysis_ready_msg
        )
        )
    
    except requests.Timeout as e:
        logger.warning(f"Timeout: {e}")
        raise self.retry(exc=e, countdown=300)
    
    except requests.HTTPError as e:
        status_code = e.response.status_code
        logger.error(f"[HTTPError {status_code}] {e}")
        
        if status_code == 429:
            retry_after = int(e.response.headers.get("Retry-After", 360))
            raise self.retry(exc=e, countdown=retry_after)
        
        elif 500 <= status_code < 600:
            retry_num = self.request.retries
            base_delay = 300
            delay = base_delay * (2 ** retry_num)
            delay = min(delay, 3600)
            raise self.retry(exc=e, countdown=delay)
        
        else:
            return ""
    
    except requests.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise self.retry(exc=e, countdown=300)
    
    except Exception as e:
        logger.exception(f"[unhandled Exception] {e}")
        raise self.retry(exc=e, countdown=360)
