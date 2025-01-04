import os
import tempfile
import uuid

import ffmpeg
from telegram import Update, Message, File
from telegram.ext import Application, MessageHandler, CallbackContext, filters

from config_parser import *

# Функция для конвертации видео в формат mp4
def convert_to_mp4(input_file: str, output_file: str):
    try:
        ffmpeg.input(input_file).output(output_file).run()
        return output_file
    except ffmpeg.Error as e:
        print(f"Ошибка конвертации: {e}")
        return None
    
async def download_and_convert_video(file_info: File) -> tuple[str, str]:

    # Генерируем уникальное имя файла, чтобы избежать конфликтов
    unique_filename = f"{uuid.uuid4()}"  # Замените расширение в зависимости от исходного формата

    # Путь для временного сохранения файла
    tmp_file_path = os.path.join(tempfile.gettempdir(), unique_filename)

    # Скачиваем файл во временную папку
    await file_info.download_to_drive(tmp_file_path)

    # Указываем путь для конвертированного файла
    mp4_file_path = tmp_file_path + ".mp4"

    # Используем ffmpeg для конвертации в MP4
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
        video = message.video
        for channel_id in channel_ids:
            await context.bot.send_video(chat_id=channel_id, video=video.file_id, caption=message.caption)
    elif message.document:
        if message.document.mime_type == "video/quicktime":
            # Загружаем файл
            file_info = await context.bot.get_file(message.document.file_id)
            input_file_path, converted_video_path = await download_and_convert_video(file_info)

            if converted_video_path:
                # Отправляем видео в канал
                with open(converted_video_path, 'rb') as video:
                    for channel_id in channel_ids:
                        await context.bot.send_video(chat_id=channel_id, video=video)

                # Удаляем временные файлы
                os.remove(input_file_path)
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