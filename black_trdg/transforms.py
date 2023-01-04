from PIL import Image, ImageFilter
from typing import Callable, List
from PIL.Image import Resampling
from dataclasses import dataclass
import numpy as np
import random


def rotate(image, degree):
    return image.rotate(degree, expand=True, resample=Resampling.BILINEAR)


def gaussian_blur(image, radius):
    kernel = ImageFilter.GaussianBlur(radius=radius)
    return image.filter(kernel)


def box_blur(image, radius, Filter):
    kernel = ImageFilter.BoxBlur(radius=radius)
    return image.filter(kernel)


@dataclass
class RandomGaussianBlur:
    min_radius: float = 1
    max_radius: float = 3

    def __call__(self, image):
        radius = random.random(
            np.arange(self.min_radius, self.max_radius, 0.01))
        return gaussian_blur(radius, radius)


@dataclass
class RandomBoxBlur:
    min_radius: float = 1
    max_radius: float = 3

    def __call__(self, image):
        radius = random.random(
            np.arange(self.min_radius, self.max_radius, 0.01))
        return box_blur(radius, radius)


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
