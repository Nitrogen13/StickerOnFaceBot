import io

from PIL import Image


def get_face_boxes(faces, source_size):
    # this list comprehension builds a bounding box around the faces
    return [
        (
            int(f['BoundingBox']['Left'] * source_size[0]),
            int(f['BoundingBox']['Top'] * source_size[1]),
            int((f['BoundingBox']['Left'] + f['BoundingBox']['Width']) * source_size[0]),
            int((f['BoundingBox']['Top'] + f['BoundingBox']['Height']) * source_size[1]),
            # we store the final coordinate of the bounding box as the pitch of the face
            f['Pose']['Roll']
        )
        for f in faces
    ]


def build_masked_image(source, mask, boxes):
    for box in boxes:
        size = (box[2] - box[0], box[3] - box[1])
        scaled_mask = mask.rotate(-box[4], expand=1).resize(size, Image.ANTIALIAS)
        # we cut off the final element of the box because it's the rotation
        source.paste(scaled_mask, box[:4], scaled_mask)


def memefy(source, mask, faces):
    print("Memefy the image...")
    boxes = get_face_boxes(faces, source.size)
    if boxes:
        build_masked_image(source, mask, boxes)
    else:
        return None

    image_bytes = io.BytesIO()
    source.save(image_bytes, format='JPEG')

    return image_bytes.getvalue()
