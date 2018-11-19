import sys

sys.path.append("lib")

import telebot
from src import bot


def lambda_handler(event, context):
    # initialize
    token = open("key.txt").read()
    bot_instance = bot.meme_bot_factory(token)

    # convert event to updates
    updates = bot.event_to_updates(event)

    # process event
    bot_instance.process_new_updates(updates)

    return ''
