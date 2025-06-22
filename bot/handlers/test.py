from datetime import timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.crud.user_exam_qa import get_user_exam_qa
from db.models import Test, UserProgress, Question, Option, UserAnswer, User, UserResult
from db.session import SessionLocal
from bot.utils.time_zone import get_iran_time
from tasks.ai_analysis import get_ai_analysis
from bot.bot_messages import (
    test_completion_msg,
    get_already_done_msg,
    waiting_for_result_msg,
    already_taken_no_limit_msg,
)


async def show_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    db = SessionLocal()
    test_id = int(query.data.split(":")[1])
    description = db.query(Test).filter_by(id=test_id).first().description
    
    keyboard = [
        [InlineKeyboardButton('شروع آزمون 🚀', callback_data=f"start_test:{test_id}")],
        [InlineKeyboardButton('مشاهده نتیجه 📄', callback_data=f"show_result:{test_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=description,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    test_id = int(query.data.split(":")[1])
    db = SessionLocal()
    user_id = db.query(User).filter_by(telegram_id=query.from_user.id).first().id
    
    now = get_iran_time()
    today = now.date()
    
    existing = db.query(UserProgress).filter_by(
        user_id=user_id, test_id=test_id
    ).first()
    
    if existing and existing.last_taken_date and existing.last_taken_date.date() == today:
        next_time = existing.last_taken_date + timedelta(days=1)
        remaining = next_time - now
        await query.answer(
            text=get_already_done_msg(remaining),
            show_alert=True
        )
        return
    
    elif existing and existing.last_taken_date and existing.last_taken_date.date() != today:
        keyboard = [
            [InlineKeyboardButton("شروع دوباره 🔁", callback_data=f"delete_test:{test_id}")],
            [InlineKeyboardButton("مشاهده نتیجه 📝", callback_data=f"result_test{test_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=already_taken_no_limit_msg,
            reply_markup=reply_markup
        )
        return
    
    await query.answer()
    progress = UserProgress(user_id=user_id, test_id=test_id, current_order=1)
    db.add(progress)
    db.commit()
    
    await send_question(update, context, progress)


async def delete_test_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    db = SessionLocal()
    test_id = int(query.data.split(":")[1])
    user_id = db.query(User).filter_by(telegram_id=query.from_user.id).first().id
    progress = db.query(UserProgress).filter_by(
        user_id=user_id, test_id=test_id
    ).first()
    answers = db.query(UserAnswer).filter_by(
        progress_id=progress.id, user_id=user_id
    ).all()
    
    for record in answers:
        db.delete(record)
    
    db.commit()
    
    db.delete(progress)
    db.commit()
    
    progress = UserProgress(user_id=user_id, test_id=test_id, current_order=1)
    db.add(progress)
    db.commit()
    
    await send_question(update, context, progress)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, progress: UserProgress):
    db = SessionLocal()
    test_id = progress.test_id
    
    test = db.query(Test).filter_by(id=test_id).first()
    
    question = db.query(Question).filter_by(
        test_id=test_id, order=progress.current_order
    ).first()
    
    if not question:
        await update.callback_query.edit_message_text(test_completion_msg, parse_mode="Markdown")
        
        telegram_id = update.effective_user.id
        qa_pairs = get_user_exam_qa(telegram_id, progress)
        if qa_pairs in ["کاربر پیدا نشد ❌", "پیشرفت کاربر پیدا نشد ❌"]:
            await update.callback_query.edit_message_text(qa_pairs)
        else:
            get_ai_analysis.delay(test.title, qa_pairs, telegram_id, test.id)
        return
    
    option = db.query(Option).filter_by(question_id=question.id).all()
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"- {i+1}",
                callback_data=f"answer:{progress.id}:{question.id}:{option.id}"
            )
        ]
        for i, option in enumerate(option)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"سوال{progress.current_order}:{question.text}\n\n"
    for i, option in enumerate(option):
        text += f"{i+1}- {option.text}\n"
    

        
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, progress_id, question_id, option_id = query.data.split(":")
    db = SessionLocal()

    progress = db.query(UserProgress).get(int(progress_id))
    
    user_id = db.query(User).filter_by(telegram_id=update.effective_user.id).first().id

    answer = UserAnswer(
        progress_id=progress.id,
        user_id=user_id,
        question_id=int(question_id),
        selected_option_id=int(option_id)
    )
    db.add(answer)

    progress.current_order += 1
    progress.last_taken_date = get_iran_time()
    db.commit()

    await send_question(update, context, progress)


async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    db = SessionLocal()
    test_id = int(query.data.split(":")[1])
    user_id = db.query(User).filter_by(telegram_id=query.from_user.id).first().id
    
    result = db.query(UserResult).filter_by(
        user_id=user_id, test_id=test_id
    ).first()
    
    if result:
        await query.answer()
        await query.edit_message_text(result.result_text)
    else:
        await query.answer(
            text=waiting_for_result_msg,
            show_alert=True
        )
