from PIL import Image, ImageFilter
from typing import Callable, List, Tuple
from PIL.Image import Resampling
from dataclasses import dataclass
import numpy as np
import random
import cv2


def rotate(image, degree):
    return image.rotate(degree, expand=True, resample=Resampling.BILINEAR)


def gaussian_blur(image, radius):
    kernel = ImageFilter.GaussianBlur(radius=radius)
    return image.filter(kernel)


def box_blur(image, radius):
    kernel = ImageFilter.BoxBlur(radius=radius)
    return image.filter(kernel)


def motion_blur(image, size, vertical=True):
    kernel_motion_blur = np.zeros((size, size))
    if vertical:
        kernel_motion_blur[int((size-1)/2), :] = np.ones(size)
    else:
        kernel_motion_blur[:, int((size-1)/2)] = np.ones(size)
    kernel_motion_blur = kernel_motion_blur / size
    image = np.array(image)
    result = cv2.filter2D(image, -1, kernel_motion_blur)
    result = Image.fromarray(image)
    return result


def padding(image, x1, y1, x2, y2):
    np_image = np.array(image)
    np_image = np.pad(np_image, [(y1, y2), (x1, x2), (0, 0)], 'constant')
    image = Image.fromarray(np_image)
    return image


@dataclass
class RandomMotionBlur:
    sizes: Tuple[int] = (1, 3, 5, 7)

    def __call__(self, image):
        size = random.choice(self.sizes)
        if random.choice([True, False]):
            image = motion_blur(image, size, vertical=True)
        if random.choice([True, False]):
            image = motion_blur(image, size, vertical=False)
        return image


@dataclass
class RandomPadding:
    def __init__(self, x1, y1=None, x2=None, y2=None):
        self.x1 = x1
        self.y1 = y1 if y1 is not None else x1
        self.y2 = y2 if y2 is not None else x1
        self.x2 = x2 if x2 is not None else x1

    def __call__(self, image):
        x1 = random.randint(*self.x1)
        x2 = random.randint(*self.x2)
        y1 = random.randint(*self.y1)
        y2 = random.randint(*self.y2)
        return padding(image, x1, y1, x2, y2)


@dataclass
class RandomGaussianBlur:
    min_radius: float = 1
    max_radius: float = 2

    def __call__(self, image):
        radius = random.choice(
            np.arange(self.min_radius, self.max_radius, 0.01))
        return gaussian_blur(image, radius)


@dataclass
class RandomBoxBlur:
    min_radius: float = 1
    max_radius: float = 2

    def __call__(self, image):
        radius = random.choice(
            np.arange(self.min_radius, self.max_radius, 0.01))
        return box_blur(image, radius)


@dataclass
class RandomRotate:
    min_degree: int = -3
    max_degree: int = 3

    def __call__(self, image):
        degree = random.randint(self.min_degree, self.max_degree)
        # NEAREST IS NOT ENOUGH
        # TEXT IMAGE WILL BE BROKEN BY THE ROTATION
        return rotate(image, degree)


class GaussianNoise:
    def __call__(self, image):
        image = np.array(image, dtype='uint8') / 255
        noise = np.random.randn(*image.shape) / 10
        image = np.clip(image + noise, 0, 1)
        image = (image * 255).round().astype('uint8')
        image = Image.fromarray(image)
        return image


# TODO: just do it
# def patched_gaussian_noise(image, patch_size):
#     w, h = image.size
#     nw = w//self.patch_size
#     nh = h//self.patch_size
#     noise = np.random.randn(nw, nh, image.getchannels())
#     noise = (noise * 255).round().astype('uint8')


@ dataclass
class Sometime:
    t: Callable
    p: float = 0.5

    def __call__(self, image):
        if random.random() < self.p:
            return self.t(image)
        else:
            return image


class RandomApply:
    def __init__(self, ts: List[Callable], ps=None):
        if ps == None:
            ps = [0.5 for _ in ts]

        assert len(ps) == len(ts)
        self.ts = ts
        self.ps = ps

    def __call__(self, image):
        for t, p in zip(self.ts, self.ps):
            if random.random() < p:
                image = t(image)
        return image


@dataclass
class OneOf:
    transformations: List

    def __call__(self, image):
        transform = random.choice(self.transformations)
        return transform(image)
