import math

from PIL import Image

from src import s3_helper
import tests


class FaceBox:
    def __init__(self, face, source_width, source_height):
        self.left = int(face['BoundingBox']['Left'] * source_width)
        self.top = int(face['BoundingBox']['Top'] * source_height)
        self.width = int(face['BoundingBox']['Width'] * source_width)
        self.height = int(face['BoundingBox']['Height'] * source_height)
        self.roll = face['Pose']['Roll']


def outer_fit(source, mask, face_box):
    mask_width, mask_height = mask.size
    print("mask_width: %s, mask_height: %s " % (mask_width, mask_height))
    print("face_width: %s, face_height: %s " % (face_box.width, face_box.height))
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

    print("delta_len: %d" % delta_len)
    delta_y = delta_len * math.sin(math.radians(face_box.roll))
    delta_x = delta_len * math.cos(math.radians(face_box.roll))

    sign = 1 if face_box.roll > 0 else -1
    if horizontal_expand:
        top = face_box.top - sign * delta_y
        left = face_box.left - sign * delta_x
    else:
        top = face_box.top - sign * delta_x
        left = face_box.left - sign * delta_y

    print("width: %f, height: %f" % (top, left))
    print("roll: %f" % face_box.roll)
    print("dy: %f, dx: %f" % (delta_y, delta_x))
    print("top: %f, left: %f" % (top, left))
    scaled_mask = mask.resize((int(width), int(height)), Image.ANTIALIAS).rotate(-face_box.roll, expand=1)
    source.paste(scaled_mask, (int(left), int(top)), scaled_mask)


def memefy(source, mask, faces):
    print("Memefy the image...")

    boxes = [FaceBox(face, source.size[0], source.size[1]) for face in faces]
    for box in boxes:
        outer_fit(source, mask, box)

    return source


if __name__ == '__main__':
    # tests
    test_chat_id = "test"

    for source_file_name, cached_faces in tests.sources.items():
        print("Working on %s..." % source_file_name)
        src_bytes = open("../tests/sources/%s" % source_file_name, 'rb')
        mask = Image.open("../tests/masks/lmao.webp")

        if not cached_faces:
            s3_helper.save_unprocessed_image(src_bytes, test_chat_id)
            faces = s3_helper.get_faces_on_last_source(test_chat_id)
            print("faces on %s : %s" % (source_file_name, faces))
        else:
            faces = cached_faces

        res = memefy(Image.open(src_bytes), mask, faces)
        res.save("%s_processed.jpg" % source_file_name)
