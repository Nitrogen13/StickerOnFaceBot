import math

from PIL import Image


class FaceBox:
    def __init__(self, face, source_width, source_height):
        self.left = int(face['BoundingBox']['Left'] * source_width)
        self.top = int(face['BoundingBox']['Top'] * source_height)
        self.width = int(face['BoundingBox']['Width'] * source_width)
        self.height = int(face['BoundingBox']['Height'] * source_height)
        self.roll = face['Pose']['Roll']


def outer_fit(source, mask, face_box):
    mask_width, mask_height = mask.size
    if mask_width > mask_height:
        height = face_box.height
        width = mask_width / mask_height * height
        delta_len = (width - face_box.width) / 2
        horizontal_expand = True
    else:
        width = face_box.width
        height = mask_height / mask_width * width
        delta_len = (height - face_box.height) / 2
        horizontal_expand = False

    delta_y = delta_len * math.sin(math.radians(face_box.roll))
    delta_x = delta_len * math.cos(math.radians(face_box.roll))

    sign = 1 if math.fabs(face_box.roll ) < 90 else -1
    if horizontal_expand:
        top = face_box.top - sign * delta_y
        left = face_box.left - sign * delta_x
    else:
        top = face_box.top - sign * delta_x
        left = face_box.left - sign * delta_y

    scaled_mask = mask.resize((int(width), int(height)), Image.ANTIALIAS).rotate(-face_box.roll, expand=1)
    source.paste(scaled_mask, (int(left), int(top)), scaled_mask)


def memefy(source, mask, faces):
    print("Memefy the image...")
    mask = mask.convert("RGBA")
    source = source.convert("RGBA")
    boxes = [FaceBox(face, source.size[0], source.size[1]) for face in faces]
    for box in boxes:
        outer_fit(source, mask, box)

    return source.convert("RGB")

