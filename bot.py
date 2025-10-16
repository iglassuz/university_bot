from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 Твои данные
TOKEN = "7834055152:AAHbGBpdWlS3KiycHh39-e1X-Vn98BFyzn4"
ADMIN_CHAT_ID = -1003138276027

# 🗂 Храним состояние пользователей
user_state = {}

# 🗃 Сопоставляем сообщения, чтобы знать, кому ответить
message_links = {}

# 🌐 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🇺🇿 O'zbek tili", "🇷🇺 Русский язык"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Tilni tanlang / Выберите язык:", reply_markup=reply_markup)

# 🌍 Выбор языка
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if "O'zbek" in text:
        user_state[user_id] = {"lang": "uz", "step": "menu"}
        keyboard = [
            ["💰 Kontrakt to'lovi bo'yicha"],
            ["🧾 Imtihon bo'yicha savol"],
            ["📚 Dars jarayonlari"],
            ["💻 LMS bo'yicha"],
            ["🏫 Dars jarayonlari va xonalari"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Bo'limni tanlang:", reply_markup=reply_markup)

    elif "Русский" in text:
        user_state[user_id] = {"lang": "ru", "step": "menu"}
        keyboard = [
            ["💰 По оплате контракта"],
            ["🧾 Вопрос по экзамену"],
            ["📚 Учебный процесс"],
            ["💻 По LMS системе"],
            ["🏫 Учебные занятия и аудитории"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите раздел:", reply_markup=reply_markup)

# 🧭 Обработка выбора раздела
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    lang = user_state.get(user_id, {}).get("lang", "uz")

    user_state[user_id]["step"] = "waiting_message"
    user_state[user_id]["topic"] = text

    if lang == "uz":
        await update.message.reply_text("Savolingizni yozing 👇")
    else:
        await update.message.reply_text("Напишите свой вопрос 👇")

# 📩 Получение вопроса от студента
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Если студент пишет вопрос
    if user_id in user_state and user_state[user_id].get("step") == "waiting_message":
        topic = user_state[user_id].get("topic", "No topic")
        lang = user_state[user_id].get("lang", "uz")
        name = update.message.from_user.full_name
        username = update.message.from_user.username or "no_username"

        # Отправляем сообщение админу
        msg_text = (
            f"📩 Yangi xabar / Новое сообщение\n\n"
            f"👤 {name} (@{username})\n"
            f"🆔 ID: {user_id}\n"
            f"📘 Bo'lim / Раздел: {topic}\n\n"
            f"💬 Xabar / Сообщение:\n{text}"
        )

        sent_message = await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg_text)

        # Сохраняем связь между сообщениями
        message_links[sent_message.message_id] = user_id

        # Ответ студенту
        if lang == "uz":
            await update.message.reply_text("Xabaringiz yuborildi ✅")
        else:
            await update.message.reply_text("Ваше сообщение отправлено ✅")

        user_state[user_id]["step"] = "menu"

    # Если пишет админ (ответ)
    elif update.message.chat_id == ADMIN_CHAT_ID and update.message.reply_to_message:
        replied_id = update.message.reply_to_message.message_id
        if replied_id in message_links:
            student_id = message_links[replied_id]
            await context.bot.send_message(chat_id=student_id, text=f"📬 Администратор:\n{update.message.text}")
            await update.message.reply_text("✅ Ответ отправлен студенту.")
        else:
            await update.message.reply_text("⚠️ Этот ответ не связан с сообщением студента.")

    else:
        await start(update, context)

# 🚀 Основная функция
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("O'zbek tili|Русский язык"), choose_language))
    app.add_handler(MessageHandler(filters.Regex(
        "Kontrakt to'lovi bo'yicha|Imtihon bo'yicha savol|Dars jarayonlari|LMS bo'yicha|Dars jarayonlari va xonalari|"
        "По оплате контракта|Вопрос по экзамену|Учебный процесс|По LMS системе|Учебные занятия и аудитории"
    ), handle_menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
