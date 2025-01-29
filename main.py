from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Инициализация Google Gemini
GOOGLE_API_KEY = 'AIzaSyDRsYWDqHrAljAXtuAu4bDbg3aS-G0uLcA'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


# Создаем клавиатуру для бота
def get_keyboard():
    keyboard = [
        [KeyboardButton("🚀 Поговорить с Gemini")],
        [KeyboardButton("❓ Что ты умеешь?")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! 👋 Я - умный бот на основе Gemini.\n"
        "Давай пообщаемся или я помогу тебе с заданием! 😊",
        reply_markup=get_keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text

    if user_message == "🚀 Поговорить с Gemini":
        await update.message.reply_text(
            "Я готов помочь! Спрашивай что угодно 😊",
            reply_markup=get_keyboard()
        )
        return

    if user_message == "❓ Что ты умеешь?":
        await update.message.reply_text(
            "🤖 Я - мощная нейросеть Gemini!\n\n"
            "Я могу помочь тебе с чем угодно:\n"
            "• Ответить на любые вопросы\n"
            "• Помочь с домашним заданием\n"
            "• Объяснить сложные темы\n"
            "• Помочь с программированием\n"
            "• Написать текст или эссе\n\n"
            "Просто напиши свой вопрос! 😊",
            reply_markup=get_keyboard()
        )
        return

    try:
        response = model.generate_content(
            f"Ты дружелюбный русскоязычный ассистент. Ответь на сообщение пользователя: {user_message}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=800,
            )
        )
        await update.message.reply_text(
            response.text,
            reply_markup=get_keyboard()
        )
    except Exception as e:
        print(f"Error in handle_message: {str(e)}")
        await update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте написать мне через несколько секунд.",
            reply_markup=get_keyboard()
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
