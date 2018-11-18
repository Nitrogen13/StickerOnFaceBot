import sys
import logging

sys.path.append("lib")

import telebot

logger = telebot.logger
logger.setLevel(logging.DEBUG)


def meme_bot_factory(token):
    bot = telebot.TeleBot(token, threaded=False)

    @bot.message_handler(commands=["start", "help"])
    def start(message):
        logger.log(logging.DEBUG, "handling hello")
        bot.reply_to(message, "replying to message with id {}".format(message.message_id))

    @bot.message_handler(content_types=["text"])
    def on_text_message(message):
        logger.log(logging.DEBUG, "handling text")
        bot.reply_to(message, "pong!")

    return bot


def lambda_handler(event, context):
    # log
    print("Event: {}".format(event))

    # initialize
    token = open("key.txt").read()
    bot = meme_bot_factory(token)

    # read updates from lambda event
    update = telebot.types.Update.de_json(event)

    # process updates
    bot.process_new_updates([update])

    return ''
