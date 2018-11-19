import telebot

WEB_HOOK_URL = "https://magxnvqnk0.execute-api.eu-west-1.amazonaws.com/default_stage/h00k"

token = open("key.txt").read()

bot = telebot.TeleBot(token)

bot.delete_webhook()
bot.set_webhook(url=WEB_HOOK_URL)
