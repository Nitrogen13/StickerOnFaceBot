import io

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import File

import image_processing
import s3_helper


def hello(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Hello {}'.format(update.message.from_user.first_name))


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Send me some sticker or pic!")


def on_message_sticker(bot, update):
    print("Got sticker")
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    sticker_id = update.message.sticker.file_id
    file = bot.get_file(sticker_id)
    with io.BytesIO() as mask_bytes:
        file.download(out=mask_bytes)

        source = s3_helper.get_last_saved_source(chat_id)
        if not source:
            print("Source image to memefy not found!")
            return  # Handle source not found

        faces = s3_helper.get_faces_on_last_source(chat_id)
        if not faces:
            print("Faces to memefy not found!")
            return  # Handle faces not found

        # mEmEs TiMe
        processed = image_processing.memefy(source, mask_bytes.getvalue(), faces)

        # Save result to s3
        with io.BytesIO() as image_bytes:
            processed.save(image_bytes, format='JPEG')
            url = s3_helper.save_processed_image(image_bytes.getvalue(), chat_id)
    print(url)

    print("Sticker successfully downloaded!")
    bot.sendMessage(chat_id=chat_id, text=get_sticker_options(sticker_id), reply_to_message_id=message_id)
    bot.send_photo(chat_id=chat_id, photo=url)


def on_message_picture(bot, update):
    print("Got pic")
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    photo = update.message.photo
    photo_id = photo[len(photo) - 1].file_id
    file = bot.get_file(photo_id)
    with io.BytesIO() as image_bytes:
        file.download(out=image_bytes)
        s3_helper.save_unprocessed_image(image_bytes.getvalue(), chat_id)
    print("Photo successfully saved!")
    bot.sendMessage(chat_id=chat_id, text="Got pic with id{}".format(photo_id), reply_to_message_id=message_id)


def get_sticker_options(sticker_id):
    """
    Finds information about the input sticker.
    """
    message = "ID: {sticker_id}" \
              "".format(sticker_id=sticker_id)

    return message


updater = Updater(str(open("key.txt", 'r').readline()).replace("\n", ""))
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('hello', hello))
dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(MessageHandler(Filters.photo, on_message_picture))
dispatcher.add_handler(MessageHandler(Filters.sticker, on_message_sticker))

updater.start_polling()
updater.idle()
