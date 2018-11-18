import io

import boto3

from PIL import Image

import image_processing

REGION_NAME = "eu-west-1"
UNPROCESSED_IMAGES_BUCKET_NAME = "ninjazz.img.unprocessed"
PROCESSED_IMAGES_BUCKET_NAME = "ninjazz.images.processed"

SOURCE_IMAGE_NAME_SUFFIX = "_source.jpg"
PROCESSED_IMAGE_NAME_SUFFIX = "_processed.jpg"

rekognition = boto3.client('rekognition', region_name=REGION_NAME)

s3 = boto3.resource('s3', region_name=REGION_NAME)
unprocessed_bucket = s3.Bucket(UNPROCESSED_IMAGES_BUCKET_NAME)
processed_bucket = s3.Bucket(PROCESSED_IMAGES_BUCKET_NAME)


def get_source_image_s3_name(chat_id):
    return chat_id + SOURCE_IMAGE_NAME_SUFFIX


def get_processed_image_s3_name(chat_id):
    return chat_id + PROCESSED_IMAGE_NAME_SUFFIX


def save_unprocessed_image(image, chat_id):
    print("Upload source image...")
    unprocessed_bucket.put_object(Body=image, Key=get_source_image_s3_name(chat_id))


def save_processed_image(image, chat_id):
    print("Upload processed image...")
    key = get_processed_image_s3_name(chat_id)
    processed_bucket.put_object(Body=image, Key=key, ACL="public-read")
    return "https://%s.s3.amazonaws.com/%s" % (PROCESSED_IMAGES_BUCKET_NAME, key)


def get_last_saved_source(chat_id):
    print("Downloading source image...")
    data = io.BytesIO()
    unprocessed_bucket.download_fileobj(get_source_image_s3_name(chat_id), data)
    return Image.open(data)


def get_faces(image_s3_name):
    resp = rekognition.detect_faces(Image={
        'S3Object': {
            'Bucket': UNPROCESSED_IMAGES_BUCKET_NAME,
            'Name': image_s3_name,
        }
    })

    if 'FaceDetails' in resp:
        return resp['FaceDetails']
    else:
        return None


if __name__ == '__main__':
    chat_id = "69420"

    # When you get a source image:
    source = open("Vanya.jpg", 'rb')  # Get source image from user
    save_unprocessed_image(source, chat_id)

    # When you get a sticker
    mask = Image.open("pika.png")  # Get mask from image or from sticker

    source = get_last_saved_source(chat_id)
    if not source:
        # Handle source not found
        pass

    faces = get_faces(get_source_image_s3_name(chat_id))
    if not faces:
        # Handle faces not found
        pass

    processed = image_processing.memefy(source, mask, faces)
    url = save_processed_image(processed, chat_id)
    print(url)
