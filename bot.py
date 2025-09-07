from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = "8092801274:AAG0PhrfYVaQ83IusIgQzWhf2Sa19jo-ywI"
SUPPORT_GROUP_ID = -4859105133  # ID групи підтримки

# Словарь: message_id у групі -> user_id
user_message_map = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Вітаємо! Це Айфоша BOT. Напишіть своє питання, і ми відповімо вам у найближчий час."
    )


# Користувач пише у приват
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # Текст
    if update.message.text:
        sent = await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=f"📩 Нове звернення від @{user.username or 'без_никнейма'}:\n\n{update.message.text}"
        )
    
    # Фото
    elif update.message.photo:
        photo = update.message.photo[-1]  # берем самое большое
        sent = await context.bot.send_photo(
            chat_id=SUPPORT_GROUP_ID,
            photo=photo.file_id,
            caption=f"📷 Фото від @{user.username or 'без_никнейма'}"
        )

    # Видео
    elif update.message.video:
        video = update.message.video
        sent = await context.bot.send_video(
            chat_id=SUPPORT_GROUP_ID,
            video=video.file_id,
            caption=f"🎬 Відео від @{user.username or 'без_никнейма'}"
        )
    else:
        await update.message.reply_text("Тип повідомлення не підтримується.")
        return

    # Прив’язуємо id повідомлення групи до користувача
    user_message_map[sent.message_id] = user.id


# Відповідь з групи
async def support_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        reply_id = update.message.reply_to_message.message_id
        if reply_id in user_message_map:
            user_id = user_message_map[reply_id]

            # Текст
            if update.message.text:
                await context.bot.send_message(chat_id=user_id, text=update.message.text)

            # Фото
            elif update.message.photo:
                photo = update.message.photo[-1]
                await context.bot.send_photo(chat_id=user_id, photo=photo.file_id, caption=update.message.caption)

            # Видео
            elif update.message.video:
                video = update.message.video
                await context.bot.send_video(chat_id=user_id, video=video.file_id, caption=update.message.caption)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Приватні повідомлення від користувачів
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE, user_message))

    # Повідомлення в групі підтримки
    app.add_handler(MessageHandler(filters.Chat(SUPPORT_GROUP_ID), support_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
