import cv2
import numpy as np
from PIL import Image


class Process:

    # get grayscale image
    @staticmethod
    def get_grayscale(image: Image) -> Image:
        return Image.fromarray(cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY))

    @staticmethod
    def change_contrast_and_brightness(image: Image, alpha: float, beta: float) -> Image:
        """
        :param image: Image (in grayscale)
        :param alpha: float 1.0-3.0
        :param beta: float 0-100
        :return: Image
        """
        image = np.array(image)
        new_image = np.zeros(image.shape, image.dtype)
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                new_image[y, x] = np.clip(alpha * image[y, x] + beta, 0, 255)
        return Image.fromarray(new_image)

    # noise removal
    @staticmethod
    def remove_noise(image: Image) -> Image:
        return Image.fromarray(cv2.medianBlur(np.array(image), 3))

    @staticmethod
    def resize(image: Image, width: int, height: int) -> Image:
        """
        :param image: Image
        :type width: int
        :type height: int
        """
        return image.resize((width, height), Image.ANTIALIAS)

    # thresholding
    @staticmethod
    def thresholding(image: Image, inv: bool = True) -> Image:
        mode = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
        # return Image.fromarray(cv2.threshold(np.array(image), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])
        return Image.fromarray(cv2.threshold(np.array(image), 230, 255, mode)[1])

    @staticmethod
    def invert_colors(image: Image) -> Image:
        return Image.fromarray(~np.array(image))
