import requests
from bs4 import BeautifulSoup
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = "8092801274:AAG0PhrfYVaQ83IusIgQzWhf2Sa19jo-ywI"
SUPPORT_GROUP_ID = -4859105133  # ID групи підтримки

# Словарь: message_id у групі -> user_id
user_message_map = {}


# ==== ФУНКЦИЯ ДЛЯ ПАРСИНГА КУРСА ====
def get_usd_rate():
    url = "https://kurs.sumy.ua/uk/"
    r = requests.get(url, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")

    # ищем блок с курсом USD
    usd_block = soup.find("div", {"id": "USD"})
    if not usd_block:
        return "⚠️ Не удалось получить курс."

    buy = usd_block.find("div", class_="buy").text.strip()
    sell = usd_block.find("div", class_="sale").text.strip()
    return f"💵 USD\nКупівля: {buy} грн\nПродаж: {sell} грн"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["💵 Курс валют"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Вітаємо! Це Айфоша. Напишіть своє питання або подивіться курс валют.",
        reply_markup=reply_markup
    )


# ===== КОМАНДА /kurs =====
async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rate = get_usd_rate()
    await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=rate)


# ===== Обработка кнопки "Курс валют" =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "💵 Курс валют":
        rate = get_usd_rate()
        await context.bot.send_message(chat_id=SUPPORT_GROUP_ID, text=rate)


# ===== Приватные сообщения от пользователей =====
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if update.message.text:
        sent = await context.bot.send_message(
            chat_id=SUPPORT_GROUP_ID,
            text=f"📩 Нове звернення від @{user.username or 'без_никнейма'}:\n\n{update.message.text}"
        )
    elif update.message.photo:
        photo = update.message.photo[-1]
        sent = await context.bot.send_photo(
            chat_id=SUPPORT_GROUP_ID,
            photo=photo.file_id,
            caption=f"📷 Фото від @{user.username or 'без_никнейма'}"
        )
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

    user_message_map[sent.message_id] = user.id


# ===== Ответ из группы =====
async def support_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        reply_id = update.message.reply_to_message.message_id
        if reply_id in user_message_map:
            user_id = user_message_map[reply_id]

            if update.message.text:
                await context.bot.send_message(chat_id=user_id, text=update.message.text)
            elif update.message.photo:
                photo = update.message.photo[-1]
                await context.bot.send_photo(chat_id=user_id, photo=photo.file_id, caption=update.message.caption)
            elif update.message.video:
                video = update.message.video
                await context.bot.send_video(chat_id=user_id, video=video.file_id, caption=update.message.caption)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kurs", kurs))

    # Кнопка "Курс валют"
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Курс валют"), button_handler))

    # Приватные сообщения
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE, user_message))

    # Сообщения в группе поддержки
    app.add_handler(MessageHandler(filters.Chat(SUPPORT_GROUP_ID), support_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
