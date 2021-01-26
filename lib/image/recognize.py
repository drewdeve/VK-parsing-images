from io import BytesIO

from PIL import Image, ImageDraw
from lib.image.compare import Compare
from lib.image.process import Process
from lib.util.util import get_min_key



class Recognize:

    def __init__(self, process: Process, compare: Compare):
        self.proc = process
        self.comp = compare

    @staticmethod
    def create_image(image_bytes: bytes) -> Image:
        return Image.open(BytesIO(image_bytes))

    def get_code(self, image: Image) -> str:
        image = self.proc.resize(image, 1086, 664)
        crop = image.crop([150, 250, 930, 350])
        no_noise = self.proc.remove_noise(crop)
        gray = self.proc.get_grayscale(no_noise)
        th = self.proc.thresholding(gray)
        normal = self.create_crop(th)
        text = ''
        for litter in self.get_litters(normal):
            standart = self.place_in_center(self.create_crop(litter), 50, 60)
            last = self.comp.get_best_find(self.comp.get_chain(standart))
            h_p = self.get_height_of_line(litter) * 100 // normal.size[1]
            if last == '-' and h_p > 70:
                last = '_'
            text += last
        return text.upper()

    def get_num(self, image: Image) -> str:
        image = self.proc.resize(image, 1086, 664)
        no_noise = self.proc.remove_noise(image)
        gray = self.proc.get_grayscale(no_noise)
        th = self.proc.thresholding(gray)
        normal = th
        draw = ImageDraw.Draw(normal)
        # normal.show()
        # MAIN TEXT
        draw.rectangle([150, 250, 930, 350], fill='#ffffff')
        # 1WIN LOGO
        draw.rectangle([141, 110, 278, 145], fill='#ffffff')
        # FIRST SMALL NUMBER (BOTTOM_LEFT)
        draw.rectangle([109, 476, 212, 502], fill='#ffffff')
        # SECOND SMALL NUMBER (BOTTOM_LEFT)
        draw.rectangle([347, 476, 392, 504], fill='#ffffff')

        # CORNERS
        draw.rectangle([56, 48, 73, 70], fill='#ffffff')
        draw.rectangle([1012, 48, 1029, 70], fill='#ffffff')
        draw.rectangle([56, 545, 72, 567], fill='#ffffff')
        draw.rectangle([1014, 545, 1029, 567], fill='#ffffff')

        # BET WATERMARK (BOTTOM_RIGHT)
        draw.rectangle([835, 434, 969, 514], fill='#ffffff')

        crop = normal.crop([56, 48, 1030, 566])
        normal = self.create_crop(crop)
        text = ''
        for litter in self.get_litters(normal):
            standart = self.place_in_center(self.create_crop(litter), 50, 60)
            # standart.save('base2/2.jpg')
            # print(self.comp.get_chain(standart))
            last = self.comp.get_best_find_2(self.comp.get_chain(standart))
            h_p = self.get_height_of_line(litter) * 100 // normal.size[1]
            if last == '-' and h_p > 70:
                last = '_'
            text += last
        return text

    def create_crop(self, crop: Image, w_border: int = 0, h_border: int = 0) -> Image:
        crop = self.add_borders(crop, 10, 10)
        X, Y = crop.size
        colors = list(crop.getdata())

        xl = []
        xr = []
        ys = []

        for y in range(Y):
            arr = colors[y * X:(y + 1) * X]
            m = get_min_key(arr)
            if m is not None:
                xl.append(m)
                xr.append(X - get_min_key(arr[::-1]))
                ys.append(0)
            else:
                ys.append(255)

        if not any(ys):
            return None

        min_y = get_min_key(ys)
        max_y = Y - get_min_key(ys[::-1])
        min_x = min(xl)
        max_x = max(xr)

        w = max_x - min_x
        h = max_y - min_y

        new_crop = crop.crop((min_x, min_y, max_x, max_y))
        return self.add_borders(new_crop, w_border, h_border)

    @staticmethod
    def get_litters(image: Image):
        X, Y = image.size
        colors = list(image.getdata())
        borders = []
        last = False
        i = 0
        for x in range(X):
            arr = [colors[X * y + x] for y in range(Y)]
            if arr.count(0) >= 2 and not last:
                borders.append([i])
                last = True
            elif arr.count(0) <= 2 and last:
                borders[-1].append(i)
                last = False
            i += 1
        borders[-1].append(i)
        return [image.crop([border[0], 0, border[1], Y])
                for border in borders]

    @staticmethod
    def is_empty(crop: Image) -> bool:
        return all(list(crop.getdata()))

    @staticmethod
    def get_height_of_line(crop: Image) -> int:
        X, Y = crop.size
        colors = list(crop.getdata())
        for i in range(X * Y):
            if not colors[i]:
                return i // X
        return Y

    @staticmethod
    def add_borders(image: Image, w_border: int = 0, h_border: int = 0):
        X, Y = image.size
        result = Image.new("1", (X + w_border * 2, Y + h_border * 2), 255)
        result.paste(image, (w_border, h_border))
        return result

    @staticmethod
    def place_in_center(crop: Image, width: int, height: int):
        result = Image.new("1", (width, height), 255)
        X, Y = crop.size
        x = (width - X) // 2
        y = (height - Y) // 2
        result.paste(crop, (x, y))
        return result
