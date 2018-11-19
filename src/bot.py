import sys

sys.path.append("lib")
import io
import time
import telebot
import logging

from PIL import Image

from src import image_processing, s3_helper

logger = telebot.logger
logger.setLevel(logging.INFO)


def event_to_updates(event):
    """
    Convert AWS Lambda event to telegram API update
    :param event: lambda event
    :return: [telebot.types.Update]
    """
    update = telebot.types.Update.de_json(event)
    return [update]


def get_sticker_options(sticker_id):
    """
    Finds information about the input sticker.
    """
    message = "ID: {sticker_id}" \
              "".format(sticker_id=sticker_id)

    return message


def meme_bot_factory(token):
    """
    Creates a bot instance and configures handlers
    :param token: tg bot token
    :return: pyTelegramBotAPI bot instance
    """
    bot = telebot.TeleBot(token, threaded=False)

    @bot.message_handler(commands=["hello"])
    def hello(message):
        bot.send_message(chat_id=message.chat.id, text='Hello {}'.format(message.from_user.first_name))

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(chat_id=message.chat.id, text="Send me some sticker or pic!")

    @bot.message_handler(content_types=["photo"])
    def on_message_picture(message):
        logging.info("Got pic")
        chat_id = message.chat.id
        message_id = message.message_id
        photo = message.photo
        photo_id = photo[-1].file_id
        file = bot.get_file(photo_id)
        with io.BytesIO() as image_bytes:
            r = bot.download_file(file.file_path)
            image_bytes.write(r)
            image_bytes.seek(0)
            s3_helper.save_unprocessed_image(image_bytes.getvalue(), chat_id)
        logging.info("Photo successfully saved!")
        bot.send_message(chat_id=chat_id, text="Got pic with id{}".format(photo_id), reply_to_message_id=message_id)

    @bot.message_handler(content_types=["sticker"])
    def on_message_sticker(message):
        logging.info("Got sticker")
        chat_id = message.chat.id
        message_id = message.message_id
        sticker_id = message.sticker.file_id
        file = bot.get_file(sticker_id)
        with io.BytesIO() as mask_bytes:
            try:
                r = bot.download_file(file.file_path)
                mask_bytes.write(r)
                mask = Image.open(mask_bytes)
                logging.info("Sticker successfully downloaded!")
            except Exception as e:
                logging.exception(e)
                return

            source = s3_helper.get_last_saved_source(chat_id)
            if not source:
                logging.info("Source image to memefy not found!")
                return  # Handle source not found

            faces = s3_helper.get_faces_on_last_source(chat_id)
            if not faces:
                logging.info("Faces to memefy not found!")
                return  # Handle faces not found

            # mEmEs TiMe
            processed = image_processing.memefy(source, mask, faces)

            # Save result to s3
            with io.BytesIO() as image_bytes:
                processed.save(image_bytes, format='JPEG')
                url = s3_helper.save_processed_image(image_bytes.getvalue(), chat_id)

        # url += "?t=%s" % (int(time.time()))
        url += "?t={}".format(time.time())
        logging.info(url)

        bot.send_message(chat_id=chat_id, text=get_sticker_options(sticker_id), reply_to_message_id=message_id)
        bot.send_photo(chat_id=chat_id, photo=url)

    return bot


"""
def on_message_picture_beard(bot, update):
    logging.info("Got pic for beard")
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    photo = update.message.photo
    photo_id = photo[len(photo) - 1].file_id
    file = bot.get_file(photo_id)
    with io.BytesIO() as image_bytes:
        file.download(out=image_bytes)
        image_bytes.seek(0)
        s3_helper.save_unprocessed_image(image_bytes.getvalue(), chat_id)
    logging.info("Photo successfully saved!")

    logging.info("Analyzing beard")
    with io.BytesIO() as mask_bytes:
        try:
            file.download(out=mask_bytes)
            mask = Image.open(mask_bytes)
            logging.info("Photo with beard successfully downloaded!")
        except Exception as e:
            logging.exception(e)
            return

        source = s3_helper.get_last_saved_source(chat_id)
        if not source:
            logging.info("Source image to memefy not found!")
            return  # Handle source not found

        faces = s3_helper.get_faces_on_last_source(chat_id)
        if not faces:
            logging.info("Faces to memefy not found!")
            return  # Handle faces not found

    if faces[0].get('Beard').get('Value'):
        bot.sendMessage(chat_id=chat_id, text='I\'m %0.02f percent sure, that you have great beard!' % float(
            faces[0].get('Beard').get('Confidence')),
                        reply_to_message_id=message_id)
    else:
        bot.sendMessage(chat_id=chat_id, text='Sad, that you have no beard((99(',
                        reply_to_message_id=message_id)

    if faces[0].get('Mustache').get('Value'):
        bot.sendMessage(chat_id=chat_id, text='I\'m %0.02f percent sure, that you have great mustache!' % float(
            faces[0].get('Mustache').get('Confidence')),
                        reply_to_message_id=message_id)
    else:
        bot.sendMessage(chat_id=chat_id, text='Sad, that you have no mustache((99(',
                        reply_to_message_id=message_id)
"""

"""
updater = Updater(str(open("key.txt", 'r').readline()).replace("\n", ""))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('hello', hello))
dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(MessageHandler(Filters.photo, on_message_picture_beard))
dispatcher.add_handler(MessageHandler(Filters.photo, on_message_picture))
dispatcher.add_handler(MessageHandler(Filters.sticker, on_message_sticker))

updater.start_polling()
updater.idle()
"""
