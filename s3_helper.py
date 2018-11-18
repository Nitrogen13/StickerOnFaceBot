import io

import boto3

from PIL import Image
from botocore.exceptions import ClientError

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
    return str(chat_id) + SOURCE_IMAGE_NAME_SUFFIX


def get_processed_image_s3_name(chat_id):
    return str(chat_id) + PROCESSED_IMAGE_NAME_SUFFIX


def save_unprocessed_image(image, chat_id):
    print("Upload source image...")
    try:
        unprocessed_bucket.put_object(Body=image, Key=get_source_image_s3_name(chat_id))
    except Exception as e:
        print(e)


def save_processed_image(image, chat_id):
    print("Upload processed image...")
    key = get_processed_image_s3_name(chat_id)
    processed_bucket.put_object(Body=image, Key=key, ACL="public-read")
    return "https://%s.s3.amazonaws.com/%s" % (PROCESSED_IMAGES_BUCKET_NAME, key)


def get_last_saved_source(chat_id):
    print("Downloading source image...")
    data = io.BytesIO()
    try:
        unprocessed_bucket.download_fileobj(get_source_image_s3_name(chat_id), data)
        return Image.open(data)
    except Exception as e:
        print("Download error: %s", e)
        return None


def get_faces_on_last_source(chat_id):
    resp = rekognition.detect_faces(Image={
        'S3Object': {
            'Bucket': UNPROCESSED_IMAGES_BUCKET_NAME,
            'Name': get_source_image_s3_name(chat_id),
        }
    },
        Attributes=['ALL'])

    if 'FaceDetails' in resp:
        return resp['FaceDetails']
    else:
        return None


if __name__ == '__main__':
    chat_id = "69420"

    # When you get a source image:
    source = open("test_img/Vanya.jpg", 'rb')  # Get source image from user
    save_unprocessed_image(source, chat_id)

    # When you get a sticker
    mask = Image.open("test_img/pika.png")  # Get mask from image or from sticker

    source = get_last_saved_source(chat_id)
    if not source:
        print("Source image to memefy not found!")
        exit()  # Handle source not found

    faces = get_faces_on_last_source(get_source_image_s3_name(chat_id))
    if not faces:
        print("Faces to memefy not found!")
        exit()  # Handle faces not found

    # mEmEs TiMe
    processed = image_processing.memefy(source, mask, faces)

    # Save result to s3
    image_bytes = io.BytesIO()
    processed.save(image_bytes, format='JPEG')
    url = save_processed_image(image_bytes.getvalue(), chat_id)
    print(url)
