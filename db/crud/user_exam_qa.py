from db.session import SessionLocal
from sqlalchemy.orm import joinedload
from  db.models import User, UserProgress, UserAnswer, Question, Option


def get_user_exam_qa(telegram_id: int, progress: UserProgress) -> str:
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        return "کاربر پیدا نشد ❌"
    
    if not progress:
        return "پیشرفت کاربر پیدا نشد ❌"
    
    answers = (
        db.query(UserAnswer)
        .options(
            joinedload(UserAnswer.question),
            joinedload(UserAnswer.option)
        )
        .filter(
            UserAnswer.user_id == user.id,
            UserAnswer.progress_id == progress.id
        )
        .join(Question)
        .order_by(Question.order)
        .all()
    )
    
    qa_pairs = ''
    for answer in answers:
        question = db.query(Question).filter_by(id=answer.question_id).first()
        option = db.query(Option).filter_by(id=answer.selected_option_id).first().text
        
        qa_pairs += f"سوال{question.order}: {question.text}\nپاسخ: {option}\n\n"
    
    return qa_pairs.strip()
