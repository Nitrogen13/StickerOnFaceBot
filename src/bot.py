import sys

sys.path.append("lib")
import io
import time
import telebot
import logging

from PIL import Image

from src import image_processing, s3_helper, face_analyzing

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


def meme_bot_factory(token):
    """
    Creates a bot instance and configures handlers
    :param token: tg bot token
    :return: pyTelegramBotAPI bot instance
    """
    bot = telebot.TeleBot(token, threaded=False)

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(chat_id=message.chat.id, text='Hello {}! Send me some picture, that contains faces and I will memify it!'.format(message.from_user.first_name))

    @bot.message_handler(content_types=["photo"])
    def on_message_picture(message):
        print("Got pic")
        chat_id = message.chat.id
        message_id = message.message_id
        photo = message.photo
        photo_id = photo[len(photo) - 1].file_id
        file = bot.get_file(photo_id)
        with io.BytesIO() as image_bytes:
            r = bot.download_file(file.file_path)
            image_bytes.write(r)
            image_bytes.seek(0)
            s3_helper.save_unprocessed_image(image_bytes.getvalue(), chat_id)
        print("Photo successfully saved!")

        print("Analyzing photo")
        source = s3_helper.get_last_saved_source(chat_id)
        if not source:
            print("Source image to analyze not found!")
            return  # Handle source not found

        faces = s3_helper.get_faces_on_last_source(chat_id)
        if not faces:
            bot.send_message(chat_id=chat_id, text="I cannot recognize any face :(", reply_to_message_id=message_id)
            return  # Handle faces not found

        message = face_analyzing.get_random_message(faces)
        bot.send_message(chat_id=chat_id, text=message, reply_to_message_id=message_id)
        bot.send_message(chat_id=chat_id, text="Now send me some sticker!")

    @bot.message_handler(content_types=["sticker"])
    def on_message_sticker(message):
        print("Got sticker")
        chat_id = message.chat.id
        message_id = message.message_id
        sticker_id = message.sticker.file_id
        file = bot.get_file(sticker_id)
        with io.BytesIO() as mask_bytes:
            try:
                r = bot.download_file(file.file_path)
                mask_bytes.write(r)
                mask = Image.open(mask_bytes)
                print("Sticker successfully downloaded!")
                bot.send_message(chat_id=chat_id, text="Good choice!",
                                 reply_to_message_id=message_id)
            except Exception as e:
                bot.send_message(chat_id=chat_id, text="Something went wrong :(")
                print(e)
                return

            source = s3_helper.get_last_saved_source(chat_id)

            if not source:
                print("Source image to memefy not found!")
                bot.send_message(chat_id=chat_id, text="You should send picture first :)",
                                 reply_to_message_id=message_id)
                return  # Handle source not found

            faces = s3_helper.get_faces_on_last_source(chat_id)

            if not faces:
                print("Faces to memefy not found!")
                bot.send_message(chat_id=chat_id, text="I think picture does not contain any faces :(",
                                 reply_to_message_id=message_id)
                return  # Handle faces not found

            # mEmEs TiMe
            processed = image_processing.memefy(source, mask, faces)

            # Save result to s3
            with io.BytesIO() as image_bytes:
                print("Saving processed image...")
                processed.save(image_bytes, format='JPEG')
                url = s3_helper.save_processed_image(image_bytes.getvalue(), chat_id)
                print("Image saved at {}".format(url))

        # url += "?t=%s" % (int(time.time()))
        url += "?t={}".format(time.time())
        print(url)
        bot.send_photo(chat_id=chat_id, photo=url)

    return bot
