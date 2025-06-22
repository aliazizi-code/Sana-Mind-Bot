import re
from db.session import SessionLocal
from db.models.test import Test
from db.models.question import Question
from db.models.option import Option
from sqlalchemy.orm import Session


def add_questions_from_text(raw_text: str, test_id: int) -> str:
    db: Session = SessionLocal()

    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        return "❌ تست مورد نظر پیدا نشد."

    raw_text_lines = raw_text.strip().splitlines()
    raw_text_body = "\n".join(
        line.strip() for line in raw_text_lines if not line.lower().startswith("test_id")
    )

    pattern = r"(?m)^(\d+)\.\s*(.*?)\n((?:\s*-\s*.*\n?)*)"
    matches = re.findall(pattern, raw_text_body)

    if not matches:
        raise "❌ هیچ سوالی پیدا نشد."

    created_questions = 0
    total_options = 0

    try:
        for num, question_text, options_block in matches:
            order = int(num.strip())
            question_text = question_text.strip()
            options = [
                opt.strip("- ").strip()
                for opt in options_block.strip().splitlines()
                if opt.strip()
            ]

            if not question_text or not options:
                continue

            question = Question(test_id=test.id, text=question_text, order=order)
            db.add(question)
            db.flush()

            for opt in options:
                db.add(Option(question_id=question.id, text=opt))

            total_options += len(options)
            created_questions += 1

        db.commit()
        return f"✅ {created_questions} سوال با موفقیت ذخیره شدند.\n📌 مجموع گزینه‌ها: {total_options}"
    except Exception as e:
        db.rollback()
        raise f"❌ خطا در ذخیره‌سازی: {str(e)}"


