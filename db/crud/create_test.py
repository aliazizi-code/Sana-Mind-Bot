import re
from db.session import SessionLocal
from db.models.test import Test
from bot.utils.time_zone import get_iran_time


def extract_quoted_value(text: str, key: str) -> str | None:
    pattern = rf'{key}\s*=\s*(?P<quote>["\']{{1,3}})(.*?)(?P=quote)'
    match = re.search(pattern, text, re.DOTALL)
    return match.group(2).strip() if match else None

def create_test_from_text(raw_text: str) -> str:
    title = extract_quoted_value(raw_text, "title")
    description = extract_quoted_value(raw_text, "description")

    if not title or not description:
        return {
            "result": "❌ فرمت ورودی اشتباه است. لطفاً از title= و description= همراه با کوتیشن استفاده کنید.",
            "err": True
        }

    db = SessionLocal()
    test = Test(
        title=title,
        description=description,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    
    result_text = (
        "🧪 تست با موفقیت ساخته شد:\n\n"
        f"🆔 ID: {test.id}\n\n"
        f"📌 عنوان: {test.title}\n\n"
        f"📄 توضیح: {test.description}\n\n"
        f"🕒 زمان ایجاد: {get_iran_time().strftime('%Y-%m-%d %H:%M')}"
    )

    return {
        "test_id": test.id if test else None,
        "result": result_text,
        "err": False
    }
