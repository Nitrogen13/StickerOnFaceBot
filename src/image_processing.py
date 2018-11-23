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

    sign = 1 if math.fabs(face_box.roll) < 90 else -1
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


def rotate_point(x, y, angle):
    angle = math.radians(angle)
    cos = math.cos(angle)
    sin = math.sin(angle)

    rx = x * cos - y * sin
    ry = x * sin + y * cos
    return rx, ry


def get_cropped_face(source, face_box):
    # Find center of the face
    diag_x, diag_y = rotate_point(face_box.width, face_box.height, face_box.roll)
    center_x, center_y = int(face_box.left + diag_x / 2), int(face_box.top + diag_y / 2)
    radius = int(math.sqrt(face_box.width ** 2 + face_box.height ** 2) / 2)
    print("center: %d, %d; radius: %d" % (center_x, center_y, radius))

    # crop around face and rotate
    crop_coordinates = (center_x - radius, center_y - radius, center_x + radius, center_y + radius)
    face = source.crop(crop_coordinates).rotate(face_box.roll, expand=1)

    # crop blank spaces after rotation
    rotation_angle = math.radians(face_box.roll)
    padding = int(2 * radius * min(abs(math.cos(rotation_angle)), abs(math.sin(rotation_angle))))
    face = face.crop((padding, padding, face.size[0] - padding, face.size[1] - padding))

    return face


def half_paste(left_side, right_side):
    width, height = left_side.size
    half_width = width // 2

    half_face = right_side.crop((half_width, 0, width, height))
    result = left_side.copy()
    result.paste(half_face, (half_width, 0), half_face)
    return result


def kekefy(source, faces):
    print("Kekefy the image...")
    results = []

    boxes = [FaceBox(face, source.size[0], source.size[1]) for face in faces]
    for box in boxes:
        face = get_cropped_face(source, box).convert("RGBA")
        flipped_face = face.transpose(Image.FLIP_LEFT_RIGHT)

        results.append(half_paste(face, flipped_face).convert("RGB"))
        results.append(half_paste(flipped_face, face).convert("RGB"))

    return results
