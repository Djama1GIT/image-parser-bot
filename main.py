from utils.logger import logger
from utils.config import settings
import telebot

logger.info("start")

bot = telebot.TeleBot(settings.TOKEN)
updates = bot.get_updates()


@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message):
    bot.reply_to(message, settings.WELCOME_MESSAGE)


@bot.message_handler(content_types=["text"])
def query(message: telebot.types.Message):
    logger.info(f"Received the query: {message}")


bot.infinity_polling()
