from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
import google.generativeai as genai
import asyncio

# Инициализация Google Gemini
GOOGLE_API_KEY = 'AIzaSyDRsYWDqHrAljAXtuAu4bDbg3aS-G0uLcA'  # Замените на ваш новый ключ API  # Ваш API ключ
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Проверка работы API при запуске
try:
    response = model.generate_content("Привет")
    print("API Check - Success:", response.text)
except Exception as e:
    print("API Check - Error:", e)

# Списки для различных ответов бота (для простых команд)
GREETINGS = [
    "Привет! Как дела?",
    "Здравствуйте! Рад вас видеть!",
    "Приветствую! Как настроение?",
    "Хай! Как жизнь?"
]

FUN_FACTS = [
    "Медоеды известны тем, что не боятся никого, даже львов!",
    "Колибри - единственные птицы, которые могут летать задом наперед.",
    "Муравьи никогда не спят!",
    "Сердце синего кита настолько большое, что человек может плавать по его артериям.",
    "Октопусы имеют три сердца!"
]

# Игра "Угадай число"
GAME_STATE = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ['🤖 Gemini Chat', '🎮 Играть'],
        ['🎲 Случайный факт', '❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я бот, работающий на основе Google Gemini! Я умею:\n"
        "1. Общаться с помощью Gemini\n"
        "2. Играть в игру 'Угадай число'\n"
        "3. Рассказывать интересные факты\n"
        "\nВыберите действие на клавиатуре или используйте команды:\n"
        "/chat - Начать общение с Gemini\n"
        "/play - Начать игру\n"
        "/fact - Получить случайный факт\n"
        "/help - Помощь",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Я умею:\n"
        "🤖 Общаться через Gemini - просто нажмите кнопку или /chat\n"
        "🎮 Играть в 'Угадай число' - нажмите 'Играть' или /play\n"
        "🎲 Рассказывать факты - нажмите 'Случайный факт' или /fact\n"
        "❓ Показывать помощь - /help"
    )


async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    GAME_STATE[user_id] = random.randint(1, 100)
    await update.message.reply_text(
        "Давайте поиграем в 'Угадай число'!\n"
        "Я загадал число от 1 до 100. Попробуйте угадать!"
    )


async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fact = random.choice(FUN_FACTS)
    await update.message.reply_text(f"🎲 Случайный факт: {fact}")


async def chat_with_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text

    try:
        # Простой запрос без использования чата
        response = model.generate_content(
            f"Ты дружелюбный русскоязычный ассистент. Ответь на сообщение пользователя: {user_message}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=800,
            )
        )

        await update.message.reply_text(response.text)

    except Exception as e:
        print(f"Detailed error in chat_with_gemini: {str(e)}")  # Для отладки
        await update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте через несколько секунд."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    user_id = update.effective_user.id

    # Обработка кнопок меню
    if user_message == "🎮 играть":
        await play_game(update, context)
        return
    elif user_message == "🎲 случайный факт":
        await random_fact(update, context)
        return
    elif user_message == "❓ помощь":
        await help_command(update, context)
        return
    elif user_message == "🤖 gemini chat":
        await update.message.reply_text("Теперь я буду отвечать с помощью Gemini. О чём поговорим?")
        return

    # Проверка, играет ли пользователь в игру
    if user_id in GAME_STATE:
        try:
            guess = int(user_message)
            target = GAME_STATE[user_id]

            if guess == target:
                del GAME_STATE[user_id]
                await update.message.reply_text("🎉 Поздравляю! Вы угадали число!")
            elif guess < target:
                await update.message.reply_text("Загаданное число больше!")
            else:
                await update.message.reply_text("Загаданное число меньше!")
            return
        except ValueError:
            pass

    # Если не игра, используем Gemini
    await chat_with_gemini(update, context)


def main() -> None:
    # Вставьте ваш токен бота
    token = "7818121330:AAFxve8Yg29gsFdRnCb7sK96EvfeBm9FEDQ"

    application = ApplicationBuilder().token(token).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("play", play_game))
    application.add_handler(CommandHandler("fact", random_fact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()