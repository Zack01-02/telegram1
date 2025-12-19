from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random
import os
TOKEN = os.getenv("BOT_TOKEN")


QUESTIONS = [
    {"event": "اندلاع الثورة الجزائرية ضد الاستعمار الفرنسي", "year": "1954", "choices": ["1952", "1954", "1956", "1960"]},
    {"event": "استقلال الجزائر عن فرنسا", "year": "1962", "choices": ["1960", "1961", "1962", "1963"]},
    {"event": "أزمة الصواريخ الكوبية", "year": "1962", "choices": ["1960", "1961", "1962", "1963"]},
    {"event": "انتهاء الحرب العالمية الثانية", "year": "1945", "choices": ["1944", "1945", "1946", "1947"]},
    {"event": "تقسيم ألمانيا بعد الحرب العالمية الثانية", "year": "1949", "choices": ["1947", "1948", "1949", "1950"]},
    {"event": "بداية الحرب الباردة بين الولايات المتحدة والاتحاد السوفيتي", "year": "1947", "choices": ["1945", "1946", "1947", "1948"]},
    {"event": "إطلاق الاتحاد السوفيتي لقمر صناعي سبوتنيك", "year": "1957", "choices": ["1955", "1957", "1958", "1960"]},
    {"event": "أزمة برلين", "year": "1961", "choices": ["1960", "1961", "1962", "1963"]},
    {"event": "اغتيال الرئيس الأمريكي جون كيندي", "year": "1963", "choices": ["1962", "1963", "1964", "1965"]},
    {"event": "اتفاقيات إيفيان لإنهاء الحرب الجزائرية", "year": "1962", "choices": ["1961", "1962", "1963", "1964"]},
    {"event": "قيام الثورة المجريّة ضد الاتحاد السوفيتي", "year": "1956", "choices": ["1955", "1956", "1957", "1958"]},
    {"event": "أزمة السويس", "year": "1956", "choices": ["1955", "1956", "1957", "1958"]},
    {"event": "تأسيس حلف شمال الأطلسي (الناتو)", "year": "1949", "choices": ["1948", "1949", "1950", "1951"]},
    {"event": "تأسيس حلف وارسو", "year": "1955", "choices": ["1954", "1955", "1956", "1957"]},
    {"event": "الحرب الكورية", "year": "1950", "choices": ["1949", "1950", "1951", "1952"]},
    {"event": "إعلان الرئيس الأمريكي ترومان للسياسة الخارجية لمواجهة الشيوعية", "year": "1947", "choices": ["1945", "1946", "1947", "1948"]},
    {"event": "حادثة خليج الخنازير في كوبا", "year": "1961", "choices": ["1960", "1961", "1962", "1963"]},
    {"event": "إطلاق أول إنسان للفضاء يوري غاغارين", "year": "1961", "choices": ["1960", "1961", "1962", "1963"]},
    {"event": "تشييد جدار برلين", "year": "1961", "choices": ["1960", "1961", "1962", "1963"]},
    {"event": "أزمة فيتنام الكبرى", "year": "1965", "choices": ["1964", "1965", "1966", "1967"]}
]


user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 جولة كاملة", callback_data="full_quiz")],
        [InlineKeyboardButton("🔹 سؤال واحد", callback_data="single_question")],
        [InlineKeyboardButton("✏️ إدخال يدوي", callback_data="manual_input")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلاً بك في لعبة التاريخ! 📜\nاختر نوع التجربة التي تريدها:", reply_markup=reply_markup
    )

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data
    await query.answer()

    if choice == "full_quiz":
        keyboard = [
            [InlineKeyboardButton(f"{min(3, len(QUESTIONS))} أسئلة", callback_data="3")],
            [InlineKeyboardButton(f"{min(5, len(QUESTIONS))} أسئلة", callback_data="5")],
            [InlineKeyboardButton(f"{min(7, len(QUESTIONS))} أسئلة", callback_data="7")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("اختر عدد الأسئلة للجولة:", reply_markup=reply_markup)
    elif choice == "single_question":
        await send_single_question(query, context)
    elif choice == "manual_input":
        q = random.choice(QUESTIONS)
        user_data[user_id] = {"mode": "manual_input", "current": q}
        await query.message.reply_text(f"📜 حدث تاريخي:\n\n{q['event']}\nأدخل السنة الصحيحة:")

async def handle_number_of_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    num_questions = min(int(query.data), len(QUESTIONS))
    await query.answer()

    
    user_data[user_id] = {
        "mode": "full_quiz",
        "score": 0,
        "remaining_questions": random.sample(QUESTIONS, num_questions),
        "total_questions": num_questions
    }
    await send_next_question(user_id, query, context)

async def send_next_question(user_id, query, context):
    if user_data[user_id]["remaining_questions"]:
        q = user_data[user_id]["remaining_questions"].pop()
        user_data[user_id]["current"] = q
        keyboard = [[InlineKeyboardButton(year, callback_data=year)] for year in q["choices"]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=f"📜 حدث تاريخي:\n\n{q['event']}\n\nاختر السنة الصحيحة:",
                                       reply_markup=reply_markup)
    else:
        score = user_data[user_id]["score"]
        total = user_data[user_id]["total_questions"]
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=f"🏁 انتهت الجولة! مجموع نقاطك: {score}/{total}")
        del user_data[user_id]

async def send_single_question(query, context):
    user_id = query.from_user.id
    q = random.choice(QUESTIONS)
    user_data[user_id] = {"mode": "single_question", "current": q}
    keyboard = [[InlineKeyboardButton(year, callback_data=year)] for year in q["choices"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=query.message.chat_id,
                                   text=f"📜 حدث تاريخي:\n\n{q['event']}\n\nاختر السنة الصحيحة:",
                                   reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    choice = query.data
    await query.answer()

    if user_id not in user_data:
        await query.message.reply_text("ابدأ أولاً بإرسال /start")
        return

    mode = user_data[user_id]["mode"]
    current_q = user_data[user_id]["current"]

    if mode in ["full_quiz", "single_question"]:
        if choice == current_q["year"]:
            if mode == "full_quiz":
                user_data[user_id]["score"] += 1
            message = f"🎉 اختيار صحيح!\n✔️ السنة الصحيحة هي {current_q['year']}"
        else:
            message = f"❌ اختيار خاطئ\n✔️ السنة الصحيحة هي {current_q['year']}"
        await query.edit_message_text(text=message)

        if mode == "full_quiz":
            await send_next_question(user_id, query, context)

async def handle_manual_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data or user_data[user_id]["mode"] != "manual_input":
        return

    text = update.message.text.strip()
    current_q = user_data[user_id]["current"]
    correct = current_q["year"]

    if text == correct:
        await update.message.reply_text(f"🎉 صحيح! السنة الصحيحة هي {correct}")
    else:
        await update.message.reply_text(f"❌ خاطئ. السنة الصحيحة هي {correct}")

    del user_data[user_id]

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_choice, pattern="^(full_quiz|single_question|manual_input)$"))
    app.add_handler(CallbackQueryHandler(handle_number_of_questions, pattern="^(3|5|7)$"))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_input))
    print("البوت يعمل الآن...")
    app.run_polling()


