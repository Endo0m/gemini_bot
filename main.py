from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Инициализация Google Gemini
GOOGLE_API_KEY = 'AIzaSyDRsYWDqHrAljAXtuAu4bDbg3aS-G0uLcA'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Проверка работы API при запуске
try:
    response = model.generate_content("Привет")
    print("API Check - Success:", response.text)
except Exception as e:
    print("API Check - Error:", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я умный бот на основе Gemini. 🤖\n"
        "Я могу поговорить с вами или даже помочь с домашним заданием!\n"
        "Просто напишите мне что-нибудь, и я с радостью отвечу. 😊"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = model.generate_content(
            f"Ты дружелюбный русскоязычный ассистент. Ответь на сообщение пользователя: {update.message.text}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=800,
            )
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error in handle_message: {str(e)}")
        await update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте написать мне через несколько секунд."
        )


def main() -> None:
    # Токен вашего бота
    token = "7818121330:AAFxve8Yg29gsFdRnCb7sK96EvfeBm9FEDQ"

    application = ApplicationBuilder().token(token).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Bot started!")
    application.run_polling()


if __name__ == "__main__":
    main()
