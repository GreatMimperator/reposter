import os
import tempfile
import uuid

import ffmpeg
from telegram import Update, Message, File
from telegram.ext import Application, MessageHandler, CallbackContext, filters

from config_parser import *

async def download_and_convert_video(file_info: File) -> tuple[str, str]:
    unique_filename = f"{uuid.uuid4()}"
    tmp_file_path = os.path.join(tempfile.gettempdir(), unique_filename)
    await file_info.download_to_drive(tmp_file_path)
    mp4_file_path = tmp_file_path + ".mp4"
    ffmpeg.input(tmp_file_path).output(mp4_file_path).run()
    return tmp_file_path, mp4_file_path

# Функция для пересылки сообщений в каналы
async def forward_to_channels_with_check(update: Update, context: CallbackContext, admin_ids: list[int], channel_ids: list[int]):
    bot = context.bot
    message = update.message
    user_chat_id = message.chat.id
    if message.from_user.id not in admin_ids:
        await bot.send_message(
            chat_id=user_chat_id,
            text="Вы не являетесь админом. Нужно добавить ваш идентификатор в конфиг"
        )
        return

    if message.photo:
        for channel_id in channel_ids:
            await context.bot.send_photo(chat_id=channel_id, photo=message.photo[-1], caption=message.caption)
    elif message.video:
        for channel_id in channel_ids:
            await context.bot.send_video(chat_id=channel_id, video=message.video.file_id, caption=message.caption)
    elif message.document:
        if message.document.mime_type == "video/quicktime":
            file_info = await context.bot.get_file(message.document.file_id)
            input_file_path = None
            converted_video_path = None
            try:
                input_file_path, converted_video_path = await download_and_convert_video(file_info)
                if converted_video_path:
                    with open(converted_video_path, 'rb') as video:
                        for channel_id in channel_ids:
                            await context.bot.send_video(chat_id=channel_id, video=video, filename=message.document.file_name)
            except ffmpeg.Error as e:
                await bot.send_message(
                    chat_id=user_chat_id,
                    text="Ошибка при конвертации!"
                )
                return
            finally:
                if input_file_path is not None and os.path.exists(input_file_path):
                    os.remove(input_file_path)
                if converted_video_path is not None and os.path.exists(converted_video_path):
                    os.remove(converted_video_path)
        else:
            file = message.document
            for channel_id in channel_ids:
                await context.bot.send_document(chat_id=channel_id, document=file.file_id, caption=message.caption)
    elif message.text:
        for channel_id in channel_ids:
            await context.bot.send_message(chat_id=channel_id, text=message.text)
    else:
        await bot.send_message(
            chat_id=user_chat_id,
            text="Ошибка! Неизвестный тип сообщения"
        )
        return
    await bot.send_message(
        chat_id=user_chat_id,
        text="Готово!"
    )

def main():
    # Загружаем токен из конфигурации
    config = load_config()

    # Создаём объект Application с токеном
    application = Application.builder().token(get_bot_token(config)).build()

    # Регистрируем обработчик для всех сообщений
    application.add_handler(
        MessageHandler(
            filters.ALL,
            lambda update, context:
                forward_to_channels_with_check(
                    update=update,
                    context=context,
                    admin_ids=get_admin_ids(config),
                    channel_ids=get_linkable_channel_ids(config)
                )
        )
    )

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()