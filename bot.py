import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен и ID группы
BOT_TOKEN = "7834055152:AAHbGBpdWlS3KiycHh39-e1X-Vn98BFyzn4"
GROUP_CHAT_ID = "-1003138276027"

logging.basicConfig(level=logging.INFO)

# Кнопки по языкам
uz_buttons = [
    ["💳 Kontrakt to'lovi bo‘yicha", "🧾 Imtihon bo‘yicha savol"],
    ["📚 Dars jarayonlari", "💻 LMS bo‘yicha"],
    ["🏫 Dars jarayonlari va xonalari"]
]

ru_buttons = [
    ["💳 Вопрос по оплате контракта", "🧾 Вопрос по экзамену"],
    ["📚 Учебный процесс", "💻 По LMS"],
    ["🏫 Процесс занятий и аудитории"]
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🇺🇿 O‘zbek tili", "🇷🇺 Русский язык"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Tilni tanlang / Выберите язык:", reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    # Выбор языка
    if text == "🇺🇿 O‘zbek tili":
        context.user_data["lang"] = "uz"
        await update.message.reply_text(
            "Bo‘limni tanlang:", reply_markup=ReplyKeyboardMarkup(uz_buttons, resize_keyboard=True)
        )
        return
    elif text == "🇷🇺 Русский язык":
        context.user_data["lang"] = "ru"
        await update.message.reply_text(
            "Выберите раздел:", reply_markup=ReplyKeyboardMarkup(ru_buttons, resize_keyboard=True)
        )
        return

    lang = context.user_data.get("lang")

    # Обработка нажатий
    topics_uz = {
        "💳 Kontrakt to'lovi bo‘yicha": "Kontrakt to'lovi bo‘yicha murojaat",
        "🧾 Imtihon bo‘yicha savol": "Imtihon bo‘yicha savol",
        "📚 Dars jarayonlari": "Dars jarayonlari haqida murojaat",
        "💻 LMS bo‘yicha": "LMS bo‘yicha murojaat",
        "🏫 Dars jarayonlari va xonalari": "Dars jarayonlari va xonalari bo‘yicha murojaat"
    }

    topics_ru = {
        "💳 Вопрос по оплате контракта": "Вопрос по оплате контракта",
        "🧾 Вопрос по экзамену": "Вопрос по экзамену",
        "📚 Учебный процесс": "Учебный процесс",
        "💻 По LMS": "Вопрос по LMS",
        "🏫 Процесс занятий и аудитории": "Процесс занятий и аудитории"
    }

    if lang == "uz" and text in topics_uz:
        context.user_data["topic"] = topics_uz[text]
        await update.message.reply_text("Iltimos, savolingizni yozing:")
    elif lang == "ru" and text in topics_ru:
        context.user_data["topic"] = topics_ru[text]
        await update.message.reply_text("Пожалуйста, напишите ваш вопрос:")
    else:
        topic = context.user_data.get("topic")
        if topic:
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"📨 *{topic}*\n👤 @{user.username or user.full_name}\n\n{text}",
                parse_mode="Markdown"
            )
            if lang == "uz":
                await update.message.reply_text("✅ Xabaringiz yuborildi.")
            else:
                await update.message.reply_text("✅ Ваше сообщение отправлено.")
            context.user_data["topic"] = None
        else:
            if lang == "uz":
                await update.message.reply_text("Bo‘limni tanlang.")
            elif lang == "ru":
                await update.message.reply_text("Выберите раздел.")
            else:
                await update.message.reply_text("Tilni tanlang / Выберите язык.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
