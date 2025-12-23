__doc__ = "this file contains just 1 class for the half-tone effect"
from PIL import Image, ImageFile
import numpy as np
from math import sqrt


class HalfTone:
    def __init__(self, img: ImageFile, k, hex_size=10, max_brightness=150):
        """:parameter k: compression ratio; for clarity >= 1
        :parameter hex_size: area for 1 circle
        :parameter max_brightness if hex brightness more than max_brightness then radius = 0"""
        size = img.size
        self.width, self.height = size
        img = img.convert("L").resize((int(self.width * k), int(self.height * k)))
        self.arr = np.array(img)
        self.output = np.ones_like(self.arr)*255
        self.hex = hex_size
        self.max_brightness = max_brightness

    def __get_hex_brightness(self, x_center, y_center) -> int:
        total = 0
        hex_size = self.hex
        for y in range(y_center - (hex_size // 2), y_center + (hex_size // 2)):
            for x in range(x_center - (hex_size // 2), x_center + (hex_size // 2)):
                try:
                    total += int(self.arr[y][x])
                except IndexError:
                    break
        hex_brightness = total // hex_size ** 2
        return hex_brightness if hex_brightness <= 255 else 255

    def __get_radius(self, brightness) -> int:
        """more brightness -> less radius of circle"""
        if brightness > self.max_brightness:
            return 0
        if brightness == 0:
            return self.hex
        r = int((10 * self.hex / brightness) + (self.hex * 0.2))
        if r >= self.hex:
            return self.hex
        return r

    def __draw_circle(self, cx, cy, r):
        """using discriminant to find x_positions of intersection with y = current_y function"""
        if not r:
            return
        y = cy - r
        while y <= cy + r:
            DISCRIMINANT = int(sqrt(-4 * y ** 2 + 8 * cy * y - 4 * cy ** 2 + 4 * r ** 2))
            x1 = (2 * cx - DISCRIMINANT) // 2
            x2 = (2 * cx + DISCRIMINANT) // 2
            x = x1
            while x <= x2:
                try:
                    self.output[y][x] = 0
                except IndexError:
                    return
                x += 1
            y += 1

    def half_tone(self) -> Image:
        half_hex = self.hex // 2
        start_x = half_hex
        for cy in range(0, len(self.arr), self.hex):
            for cx in range(start_x, len(self.arr[0]), self.hex):
                brightness = self.__get_hex_brightness(cx, cy)
                r = self.__get_radius(brightness)
                self.__draw_circle(cx, cy, r)
            if start_x == half_hex:   # for a checkerboard arrangement of circles
                start_x = 0
            else:
                start_x = half_hex
        return Image.fromarray(self.output)


# show sample
if __name__ == "__main__":
    img_ = Image.open("sample.jpg")
    result = HalfTone(img_, 1.2, hex_size=10).half_tone()
    result.show()
    result.save("result.jpg")
