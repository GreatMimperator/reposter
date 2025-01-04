import configparser
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters

from config_parser import *

# Функция-обработчик для любых сообщений
async def echo(update: Update, context: CallbackContext):
    # Отправить обратно то же сообщение, которое было получено
    await update.message.reply_text(update.message.text)


def main():
    # Загружаем токен из конфигурации
    config = load_config()
    bot_token = get_bot_token(config)

    # Создаём объект Application с токеном
    application = Application.builder().token(bot_token).build()

    # Регистрируем обработчик для всех сообщений
    application.add_handler(MessageHandler(filters.TEXT, echo))

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()