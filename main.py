from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from collections import defaultdict

# Инициализация Google Gemini
GOOGLE_API_KEY = 'AIzaSyDRsYWDqHrAljAXtuAu4bDbg3aS-G0uLcA'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Словарь для хранения истории разговоров
conversation_history = defaultdict(list)
MAX_HISTORY_LENGTH = 30  # Максимальное количество сообщений в истории
MAX_TOKENS_ESTIMATE = 4096  # Примерное ограничение на токены для модели


def estimate_tokens(text: str) -> int:
    """Грубая оценка количества токенов в тексте"""
    # В среднем, один токен ~ 4 символа для русского языка
    return len(text) // 4


# Создаем клавиатуру для бота
def get_keyboard():
    keyboard = [
        [KeyboardButton("🚀 Поговорить с Gemini")],
        [KeyboardButton("❓ Что ты умеешь?")],
        [KeyboardButton("🔄 Очистить историю")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conversation_history[user_id] = []  # Очищаем историю при старте
    await update.message.reply_text(
        "Привет! 👋 Я - умный бот на основе Gemini.\n"
        "Давай пообщаемся или я помогу тебе с заданием! 😊\n"
        "Теперь я помню наш разговор и могу поддерживать длительную беседу.",
        reply_markup=get_keyboard()
    )


async def clear_history(user_id: int, update: Update) -> None:
    conversation_history[user_id] = []
    await update.message.reply_text(
        "История разговора очищена! Начнем сначала 😊",
        reply_markup=get_keyboard()
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text

    # Добавляем информацию о длине истории
    history_length = len(conversation_history[user_id]) // 2  # Делим на 2, так как храним и вопросы, и ответы
    if history_length > 0:
        context.user_data['history_length'] = history_length

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
            "• Написать текст или эссе\n"
            "• Поддерживать длительную беседу\n"
            f"• Помнить до {MAX_HISTORY_LENGTH} предыдущих сообщений\n\n"
            "Просто напиши свой вопрос! 😊",
            reply_markup=get_keyboard()
        )
        return

    if user_message == "🔄 Очистить историю":
        await clear_history(user_id, update)
        return

    try:
        # Добавляем сообщение пользователя в историю
        conversation_history[user_id].append(f"User: {user_message}")

        # Ограничиваем длину истории
        if len(conversation_history[user_id]) > MAX_HISTORY_LENGTH * 2:  # *2 потому что храним и вопросы, и ответы
            conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY_LENGTH * 2:]

        # Формируем контекст из истории с учетом ограничения токенов
        history = conversation_history[user_id]
        conversation_context = ""
        total_tokens = 0

        # Идем от последних сообщений к первым
        for message in reversed(history):
            tokens = estimate_tokens(message)
            if total_tokens + tokens > MAX_TOKENS_ESTIMATE:
                break
            conversation_context = message + "\n" + conversation_context
            total_tokens += tokens

        # Формируем промпт с историей разговора
        prompt = (
            "Ты дружелюбный русскоязычный ассистент. "
            "Вот история нашего разговора:\n"
            f"{conversation_context}\n"
            "Продолжи разговор, отвечая на последнее сообщение пользователя"
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=800,
            )
        )

        # Добавляем ответ бота в историю
        conversation_history[user_id].append(f"Assistant: {response.text}")

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
