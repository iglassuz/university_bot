from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔹 Твой токен и ID группы
BOT_TOKEN = "7834055152:AAHbGBpdWlS3KiycHh39-e1X-Vn98BFyzn4"
GROUP_CHAT_ID = -1003138276027

# 🔹 Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📩 Отправить жалобу"], ["❓ Задать вопрос"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋\nЯ бот университета. Выберите, что хотите сделать:",
        reply_markup=reply_markup
    )

# 🔹 Обработка сообщений студентов
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📩 Отправить жалобу":
        await update.message.reply_text("✍️ Напишите вашу жалобу:")
        context.user_data["mode"] = "complaint"
    elif text == "❓ Задать вопрос":
        await update.message.reply_text("💬 Напишите ваш вопрос:")
        context.user_data["mode"] = "question"
    else:
        mode = context.user_data.get("mode")
        if mode == "complaint":
            msg = f"⚠️ *Новая жалоба от студента:*\n\n{text}"
        elif mode == "question":
            msg = f"💭 *Новый вопрос от студента:*\n\n{text}"
        else:
            msg = f"📨 *Сообщение от студента:*\n\n{text}"

        # Отправляем сообщение в группу университета
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode="Markdown")
        await update.message.reply_text("✅ Ваше сообщение отправлено администрации!")

# 🔹 Запуск бота
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен и работает...")
    app.run_polling()

if __name__ == "__main__":
    main()
