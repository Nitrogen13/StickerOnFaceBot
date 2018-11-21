from PIL import Image

class FaceBox:
    def __init__(self, face, source_width, source_height):
        self.left = int(face['BoundingBox']['Left'] * source_width)
        self.top = int(face['BoundingBox']['Top'] * source_height)
        self.right = int((face['BoundingBox']['Left'] + face['BoundingBox']['Width']) * source_width)
        self.bottom = int((face['BoundingBox']['Top'] + face['BoundingBox']['Height']) * source_height)
        self.roll = face['Pose']['Roll']

    def width(self):
        return self.right - self.left

    def height(self):
        return self.bottom - self.top

    def size(self):
        return self.width(), self.height()

    def coordinates(self):
        return [self.left, self.top, self.right, self.bottom]


def memefy(source, mask, faces):
    print("Memefy the image...")

    boxes = [FaceBox(face, source.size[0], source.size[1]) for face in faces]
    for box in boxes:
        scaled_mask = mask.resize(box.size(), Image.ANTIALIAS).rotate(-box.roll, expand=1)
        source.paste(scaled_mask, (box.left, box.top), scaled_mask)

    return source


if __name__ == '__main__':
    # tests

    src_bytes = open("test_img/Vanya.jpg", 'rb')
    mask = Image.open("test_img/sticker.webp")

    # memefier.save_unprocessed_image(src_bytes, "test")
    # faces = memefier.get_faces(memefier.get_source_image_s3_name("test"))
    # print("faces: %s" % faces)

    # coordinates for Vanya.jpg
    faces = [{'BoundingBox': {'Width': 0.16969697177410126, 'Height': 0.2545454502105713, 'Left': 0.38333332538604736,
                              'Top': 0.21590909361839294},
              'Landmarks': [{'Type': 'eyeLeft', 'X': 0.44117608666419983, 'Y': 0.31642162799835205},
                            {'Type': 'eyeRight', 'X': 0.4994202256202698, 'Y': 0.3300350308418274},
                            {'Type': 'nose', 'X': 0.45734497904777527, 'Y': 0.37112942337989807},
                            {'Type': 'mouthLeft', 'X': 0.43496692180633545, 'Y': 0.4051054120063782},
                            {'Type': 'mouthRight', 'X': 0.4843645989894867, 'Y': 0.41589558124542236}],
              'Pose': {'Roll': 9.168045043945312, 'Yaw': -9.777241706848145, 'Pitch': -8.776867866516113},
              'Quality': {'Brightness': 80.83344268798828, 'Sharpness': 95.54405975341797},
              'Confidence': 99.99983215332031}]

    res = memefy(Image.open(src_bytes), mask, faces)
    res.save("test.jpg")
