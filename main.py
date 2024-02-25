from telebot.types import InputMediaPhoto

from parser import search_images
from utils.logger import logger
from utils.config import settings
import telebot

logger.info("start")

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


@bot.message_handler(content_types=["text"])
@notifier_handler
def query(message: telebot.types.Message):
    logger.info(f"Received query: {message}")

    photos = search_images(message.text)
    media_group = []
    for photo in photos:
        media_group.append(
            InputMediaPhoto(
                photo
            )
        )

    bot.send_media_group(message.chat.id, media_group)


bot.infinity_polling()
