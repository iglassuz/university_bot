from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# === НАСТРОЙКИ ===
TOKEN = "7834055152:AAHbGBpdWlS3KiycHh39-e1X-Vn98BFyzn4"
ADMIN_CHAT_ID = -1003138276027  # ID группы администраторов

# === СТАРТ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🇺🇿 O'zbekcha"), KeyboardButton("🇷🇺 Русский")]
    ]
    await update.message.reply_text(
        "Tilni tanlang / Выберите язык:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# === ОБРАБОТКА ВЫБОРА ЯЗЫКА ===
async def handle_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "O'zbekcha" in text:
        context.user_data["lang"] = "uz"
        keyboard = [
            [KeyboardButton("💳 Kontrakt to'lovi bo'yicha")],
            [KeyboardButton("🧾 Imtihon bo'yicha savol")],
            [KeyboardButton("📚 Dars jarayonlari")],
            [KeyboardButton("🌐 LMS bo'yicha")],
            [KeyboardButton("🏫 Dars jarayonlari va xonalari")]
        ]
        await update.message.reply_text(
            "Bo'limni tanlang:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    elif "Русский" in text:
        context.user_data["lang"] = "ru"
        keyboard = [
            [KeyboardButton("💳 По оплате контракта")],
            [KeyboardButton("🧾 Вопрос по экзамену")],
            [KeyboardButton("📚 Учебный процесс")],
            [KeyboardButton("🌐 По LMS")],
            [KeyboardButton("🏫 Процесс обучения и аудитории")]
        ]
        await update.message.reply_text(
            "Выберите раздел:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

# === ПОЛУЧЕНИЕ СООБЩЕНИЯ ОТ СТУДЕНТА ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message.text

    # Отправляем в группу админу
    msg_to_admin = (
        f"📩 <b>Новое сообщение от студента</b>\n"
        f"👤 Имя: {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💬 Сообщение:\n{message}\n\n"
        f"Чтобы ответить, используйте:\n<code>/reply {user.id} ваш_ответ</code>"
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg_to_admin,
        parse_mode="HTML"
    )

    # Отправляем студенту подтверждение
    lang = context.user_data.get("lang", "ru")
    if lang == "uz":
        await update.message.reply_text("Xabaringiz yuborildi ✅")
    else:
        await update.message.reply_text("Ваше сообщение отправлено ✅")

# === КОМАНДА ОТВЕТА АДМИНА ===
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        return  # только админ-группа может использовать /reply

    try:
        user_id = int(context.args[0])
        text_to_send = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"📩 Ответ от администратора:\n{text_to_send}")
        await update.message.reply_text("✅ Ответ отправлен пользователю.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}\n\nИспользуй формат:\n/reply [user_id] [текст]")

# === ГЛАВНАЯ ФУНКЦИЯ ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(MessageHandler(filters.Regex("O'zbekcha|Русский"), handle_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
