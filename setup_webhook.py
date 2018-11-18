import telebot

token = open("key.txt").read()

bot = telebot.TeleBot(token)

bot.delete_webhook()
bot.set_webhook(url="https://nogxc0l2p8.execute-api.eu-central-1.amazonaws.com/bot/h00k")
