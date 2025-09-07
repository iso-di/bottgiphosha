
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === НАЛАШТУВАННЯ ===
TOKEN = "8092801274:AAG0PhrfYVaQ83IusIgQzWhf2Sa19jo-ywI"
SUPPORT_GROUP_ID = -4859105133  # ID групи підтримки (зі знаком -100...)

# Словник: message_id у групі -> user_id
user_message_map = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Вітаємо! Це Айфоша BOT. Напишіть своє питання, і ми відповімо вам у найближчий час."
    )


# Користувач пише у приват
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # Відправляємо у групу підтримки
    sent = await context.bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=f"📩 Нове звернення від @{user.username or user.id}:\n\n{text}"
    )

    # Прив’язуємо id повідомлення групи до користувача
    user_message_map[sent.message_id] = user.id

    # ❌ Не надсилаємо підтвердження користувачу


# Відповідь з групи
async def support_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        reply_id = update.message.reply_to_message.message_id
        if reply_id in user_message_map:
            user_id = user_message_map[reply_id]
            text = update.message.text

            # Пересилаємо користувачу
            await context.bot.send_message(
                chat_id=user_id,
                text=f"💬 Відповідь від менеджера:\n{text}"
            )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Приватні повідомлення від користувачів
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, user_message))

    # Повідомлення в групі підтримки
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, support_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
