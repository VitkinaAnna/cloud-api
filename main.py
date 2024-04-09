from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, filters, ContextTypes, MessageHandler
import os
from google.cloud import language_v1


# Задання шляху до сертифікату аутентифікації
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/apvitkina/Desktop/api-lab-derev-43302f7971a0.json"

# Створення клієнта для використання Google Cloud Language API
client = language_v1.LanguageServiceClient()

# Константи для токену і імені бота
TOKEN: Final = '6388445868:AAGompUVPgYEhtBYEwfGwHtktramiMe2tVg'
BOT_USERNAME: Final = '@google_api_anna_bot'

# Обробник команди /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт!")

# Обробник команди /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Допомога!")

# Обробник команди /custom
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введіть текст для аналізу")

# Функція обробки відповіді на повідомлення
def handle_response(text: str) -> str:

    # Перетворення тексту на нижній регістр для аналізу
    processed: str = text.lower()

    # Створення об'єкта документа для аналізу сентименту
    document = {"content": text, "type_": language_v1.Document.Type.PLAIN_TEXT}
    # Виклик сервісу аналізу сентименту
    response = client.analyze_sentiment(request={'document': document})
    sentiment_score = response.document_sentiment.score

    # Визначення сентименту на основі отриманого показника
    if sentiment_score > 0:
        sentiment = "позитивний"
    elif sentiment_score < 0:
        sentiment = "негативний"
    else:
        sentiment = "нейтральний"

    return f'Сентимент тексту: {sentiment}.'

# Обробник отриманих повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type:str = update.message.chat.type
    text: str = update.message.text

    print(f'Користувач({update.message.chat.id}) у чаті {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Бот:', response)
    await update.message.reply_text(response)

# Обробник помилок
async def error(update: Update, contex: ContextTypes.DEFAULT_TYPE):
    print (f'Помилка під час оновлення {update}: {contex.error}')

if __name__ =='__main__':
    print('Запуск')
    app = Application.builder().token(TOKEN).build()

    # Додавання обробників команд
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Додавання обробника повідомлень
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Додавання обробника помилок
    app.add_error_handler(error)

    print('Опитування')
    app.run_polling(poll_interval=3)
