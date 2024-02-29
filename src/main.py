import os.path
import uuid
from io import BytesIO
from typing import List

from telebot.types import InputMediaPhoto

from parser import QueryImageSearcher, ImageFileImageSearcher
from utils.logger import logger
from utils.config import Settings
import telebot

logger.info("start")

settings = Settings()

bot = telebot.TeleBot(settings.TOKEN)
updates = bot.get_updates()


def notifier_handler(func):
    def wrapper(*args, **kwargs):
        notifier_id = None
        message = args[0]

        try:
            notifier_id = bot.send_message(message.chat.id, "Processing...").message_id
            func(*args, **kwargs)
        except Exception as e:
            bot.send_message(message.chat.id, "An error has occurred. Try again later.")
            logger.error(f"Error occurred during message processing: {e}")
        finally:
            if notifier_id:
                bot.delete_message(message.chat.id, notifier_id)

    return wrapper


@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message):
    bot.reply_to(message, settings.WELCOME_MESSAGE)


def send_media_group_from_photos(chat_id: int, photos: List[BytesIO]):
    media_group = [InputMediaPhoto(photo) for photo in photos]
    bot.send_media_group(chat_id, media_group)


@bot.message_handler(content_types=["text"])
@notifier_handler
def query(message: telebot.types.Message):
    logger.info(f"Received query: {message}")

    photos: List[BytesIO] = QueryImageSearcher().search_and_download_images(message.text)
    send_media_group_from_photos(message.chat.id, photos)

    logger.info(f"Images have been downloaded and sent, "
                f"query: {message.text}, "
                f"user: {message.from_user.id}")


@bot.message_handler(content_types=["photo"])
@notifier_handler
def image(message: telebot.types.Message):
    logger.info(f"Received image")

    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    filename = f"{uuid.uuid4()}.jpeg"
    path_to_image = os.path.join(os.getcwd(), filename)
    with open(path_to_image, 'wb') as new_file:
        new_file.write(downloaded_file)

    photos: List[BytesIO] = ImageFileImageSearcher().search_and_download_images(path_to_image)
    send_media_group_from_photos(message.chat.id, photos)

    os.remove(path_to_image)
    logger.info(f"Images have been downloaded and sent, "
                f"image: {filename}, "
                f"user: {message.from_user.id}")


bot.infinity_polling()
