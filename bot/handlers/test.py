import logging
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


logger = logging.getLogger(__name__)


async def show_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        logger.info(f"Showing test info for callback query: {query.data}")
        
        db = SessionLocal()
        test_id = int(query.data.split(":")[1])
        logger.debug(f"Extracted test_id: {test_id}")
        
        test = db.query(Test).filter_by(id=test_id).first()
        if not test:
            logger.error(f"Test with id {test_id} not found")
            await query.edit_message_text(text="آزمون مورد نظر یافت نشد!")
            return
            
        description = test.description
        logger.debug(f"Test description retrieved: {description[:50]}...")
        
        keyboard = [
            [InlineKeyboardButton('شروع آزمون 🚀', callback_data=f"start_test:{test_id}")],
            [InlineKeyboardButton('مشاهده نتیجه 📄', callback_data=f"show_result:{test_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"Sending test description and options to user")
        await query.edit_message_text(
            text=description,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    except ValueError as e:
        logger.error(f"Error parsing test_id from callback data: {query.data}. Error: {str(e)}")
        await query.edit_message_text(text="خطا در پردازش درخواست!")
    except Exception as e:
        logger.error(f"Unexpected error in show_test: {str(e)}", exc_info=True)
        await query.edit_message_text(text="خطای غیرمنتظره رخ داد!")
    finally:
        db.close()


async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        logger.info(f"Starting test for user {query.from_user.id} with callback data: {query.data}")
        
        test_id = int(query.data.split(":")[1])
        logger.debug(f"Extracted test_id: {test_id}")
        
        db = SessionLocal()
        
        # Get user from database
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            logger.error(f"User with telegram_id {query.from_user.id} not found")
            await query.answer(text="کاربر یافت نشد!", show_alert=True)
            return
            
        user_id = user.id
        logger.debug(f"User ID resolved: {user_id}")
        
        now = get_iran_time()
        today = now.date()
        logger.debug(f"Current time in Iran: {now}, today: {today}")
        
        # Check existing progress
        existing = db.query(UserProgress).filter_by(
            user_id=user_id, test_id=test_id
        ).first()
        
        if existing:
            logger.debug(f"Existing progress found: {existing}")
            
            if existing.last_taken_date and existing.last_taken_date.date() == today:
                next_time = existing.last_taken_date + timedelta(days=1)
                remaining = next_time - now
                logger.info(f"User {user_id} already took test {test_id} today. Next available: {next_time}")
                
                await query.answer(
                    text=get_already_done_msg(remaining),
                    show_alert=True
                )
                return
            
            elif existing.last_taken_date and existing.last_taken_date.date() != today:
                logger.info(f"User {user_id} has old progress for test {test_id}, offering options")
                
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
        
        # If no existing progress or can start new attempt
        logger.info(f"Creating new progress for user {user_id} on test {test_id}")
        await query.answer()
        
        progress = UserProgress(user_id=user_id, test_id=test_id, current_order=1)
        db.add(progress)
        db.commit()
        logger.debug(f"New progress created: {progress}")
        
        await send_question(update, context, progress)
        logger.info(f"First question sent to user {user_id} for test {test_id}")
        
    except ValueError as e:
        logger.error(f"Error parsing test_id from callback data: {query.data}. Error: {str(e)}")
        await query.answer(text="خطا در پردازش درخواست!", show_alert=True)
    except Exception as e:
        logger.error(f"Unexpected error in start_test: {str(e)}", exc_info=True)
        await query.answer(text="خطای غیرمنتظره رخ داد!", show_alert=True)
    finally:
        db.close()
        logger.debug("Database session closed")


async def delete_test_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        logger.info(f"User {query.from_user.id} requested to delete test progress, callback data: {query.data}")
        
        db = SessionLocal()
        
        # Extract test_id from callback data
        test_id = int(query.data.split(":")[1])
        logger.debug(f"Extracted test_id: {test_id}")
        
        # Get user from database
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            logger.error(f"User with telegram_id {query.from_user.id} not found in database")
            await query.edit_message_text(text="کاربر یافت نشد!")
            return
            
        user_id = user.id
        logger.debug(f"Resolved user_id: {user_id}")
        
        # Find existing progress
        progress = db.query(UserProgress).filter_by(
            user_id=user_id, test_id=test_id
        ).first()
        
        if not progress:
            logger.error(f"No progress found for user_id {user_id} and test_id {test_id}")
            await query.edit_message_text(text="پیشرفتی برای حذف یافت نشد!")
            return
            
        logger.info(f"Found progress to delete - ID: {progress.id}, Last taken: {progress.last_taken_date}")
        
        # Delete all user answers
        answers = db.query(UserAnswer).filter_by(
            progress_id=progress.id, user_id=user_id
        ).all()
        
        logger.debug(f"Found {len(answers)} answers to delete for progress {progress.id}")
        
        for record in answers:
            db.delete(record)
            logger.debug(f"Deleted answer ID: {record.id}")
        
        db.commit()
        logger.info(f"Deleted all {len(answers)} user answers successfully")
        
        # Delete the progress record
        db.delete(progress)
        db.commit()
        logger.info(f"Deleted progress record ID: {progress.id}")
        
        # Create new progress
        new_progress = UserProgress(user_id=user_id, test_id=test_id, current_order=1)
        db.add(new_progress)
        db.commit()
        logger.info(f"Created new progress ID: {new_progress.id} for fresh start")
        
        await send_question(update, context, new_progress)
        logger.info(f"Sent first question to user after resetting progress")
        
    except ValueError as e:
        logger.error(f"Error parsing test_id from callback data: {query.data}. Error: {str(e)}")
        await query.edit_message_text(text="خطا در پردازش درخواست!")
    except Exception as e:
        logger.error(f"Unexpected error in delete_test_progress: {str(e)}", exc_info=True)
        await query.edit_message_text(text="خطای غیرمنتظره در حذف پیشرفت آزمون رخ داد!")
    finally:
        db.close()
        logger.debug("Database session closed")


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, progress: UserProgress):
    try:
        logger.info(f"Starting to send question for progress ID: {progress.id}, test ID: {progress.test_id}, current order: {progress.current_order}")
        
        db = SessionLocal()
        test_id = progress.test_id
        logger.debug(f"Database session opened for test ID: {test_id}")

        # Get test details
        test = db.query(Test).filter_by(id=test_id).first()
        if not test:
            logger.error(f"Test not found with ID: {test_id}")
            await update.callback_query.edit_message_text(text="آزمون مورد نظر یافت نشد!")
            return
        logger.debug(f"Test found: {test.title}")

        # Get current question
        question = db.query(Question).filter_by(
            test_id=test_id, 
            order=progress.current_order
        ).first()

        if not question:
            logger.info(f"No more questions found for test ID: {test_id}. Marking as complete.")
            await update.callback_query.edit_message_text(test_completion_msg, parse_mode="Markdown")
            
            telegram_id = update.effective_user.id
            logger.debug(f"Test completed by user ID: {telegram_id}, getting QA pairs")
            
            qa_pairs = get_user_exam_qa(telegram_id, progress)
            
            if qa_pairs in ["کاربر پیدا نشد ❌", "پیشرفت کاربر پیدا نشد ❌"]:
                logger.error(f"Error getting QA pairs: {qa_pairs}")
                await update.callback_query.edit_message_text(qa_pairs)
            else:
                logger.info(f"Sending QA pairs for AI analysis. Test: {test.title}, User: {telegram_id}")
                get_ai_analysis.delay(test.title, qa_pairs, telegram_id, test.id)
            return

        logger.debug(f"Question found - ID: {question.id}, Text: {question.text[:50]}...")

        # Get question options
        options = db.query(Option).filter_by(question_id=question.id).all()
        logger.debug(f"Found {len(options)} options for question ID: {question.id}")

        # Prepare keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    f"- {i+1}",
                    callback_data=f"answer:{progress.id}:{question.id}:{option.id}"
                )
            ]
            for i, option in enumerate(options)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.debug("Keyboard markup prepared")

        # Prepare question text
        text = f"سوال {progress.current_order}: {question.text}\n\n"
        for i, option in enumerate(options):
            text += f"{i+1}- {option.text}\n"
        logger.debug(f"Question text prepared. Length: {len(text)} characters")

        # Send question to user
        await update.callback_query.edit_message_text(
            text=text, 
            reply_markup=reply_markup
        )
        logger.info(f"Question {progress.current_order} successfully sent to user")

    except Exception as e:
        logger.error(f"Error in send_question: {str(e)}", exc_info=True)
        await update.callback_query.edit_message_text(
            text="خطایی در ارسال سوال رخ داد. لطفا مجددا تلاش کنید."
        )
    finally:
        db.close()
        logger.debug("Database session closed")


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Start logging
        logger.info(f"Handling answer from user {update.effective_user.id}")
        query = update.callback_query
        await query.answer()

        # Parse callback data
        logger.debug(f"Raw callback data: {query.data}")
        _, progress_id, question_id, option_id = query.data.split(":")
        logger.info(f"Parsed data - ProgressID: {progress_id}, QuestionID: {question_id}, OptionID: {option_id}")

        db = SessionLocal()
        logger.debug("Database session opened")

        # Get progress
        progress = db.query(UserProgress).get(int(progress_id))
        if not progress:
            logger.error(f"Progress not found with ID: {progress_id}")
            await query.edit_message_text(text="پیشرفت آزمون یافت نشد!")
            return
        logger.debug(f"Found progress - TestID: {progress.test_id}, CurrentOrder: {progress.current_order}")

        # Get user
        user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
        if not user:
            logger.error(f"User not found with Telegram ID: {update.effective_user.id}")
            await query.edit_message_text(text="کاربر یافت نشد!")
            return
        user_id = user.id
        logger.debug(f"User ID resolved: {user_id}")

        # Record answer
        answer = UserAnswer(
            progress_id=progress.id,
            user_id=user_id,
            question_id=int(question_id),
            selected_option_id=int(option_id)
        )
        db.add(answer)
        logger.info(f"New answer recorded - Question: {question_id}, Option: {option_id}")

        # Update progress
        progress.current_order += 1
        progress.last_taken_date = get_iran_time()
        db.commit()
        logger.info(f"Progress updated - New order: {progress.current_order}, Timestamp: {progress.last_taken_date}")

        # Send next question
        await send_question(update, context, progress)
        logger.debug("Next question requested")

    except ValueError as e:
        logger.error(f"Error parsing callback data: {str(e)} - Data: {query.data}")
        await query.edit_message_text(text="خطا در پردازش پاسخ!")
    except Exception as e:
        logger.error(f"Unexpected error in handle_answer: {str(e)}", exc_info=True)
        await query.edit_message_text(text="خطای غیرمنتظره در ثبت پاسخ رخ داد!")
    finally:
        db.close()
        logger.debug("Database session closed")


async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"Showing result request from user {update.effective_user.id}")
        query = update.callback_query
        
        # Parse test_id from callback data
        logger.debug(f"Raw callback data: {query.data}")
        test_id = int(query.data.split(":")[1])
        logger.info(f"Requested result for test ID: {test_id}")

        db = SessionLocal()
        logger.debug("Database session opened")

        # Get user from database
        user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
        if not user:
            logger.error(f"User not found with Telegram ID: {query.from_user.id}")
            await query.answer(text="کاربر یافت نشد!", show_alert=True)
            return
        
        user_id = user.id
        logger.debug(f"User ID resolved: {user_id}")

        # Query for result
        result = db.query(UserResult).filter_by(
            user_id=user_id, 
            test_id=test_id
        ).first()

        if result:
            logger.info(f"Result found - Result ID: {result.id}")
            await query.answer()
            await query.edit_message_text(result.result_text)
            logger.debug("Result displayed to user")
        else:
            logger.info(f"No result yet for user {user_id} on test {test_id}")
            await query.answer(
                text=waiting_for_result_msg,
                show_alert=True
            )
            logger.debug("Waiting message shown to user")

    except ValueError as e:
        logger.error(f"Error parsing test_id from callback data: {query.data}. Error: {str(e)}")
        await query.answer(text="خطا در پردازش درخواست!", show_alert=True)
    except Exception as e:
        logger.error(f"Unexpected error in show_result: {str(e)}", exc_info=True)
        await query.answer(text="خطای غیرمنتظره در نمایش نتیجه رخ داد!", show_alert=True)
    finally:
        db.close()
        logger.debug("Database session closed")
