from .samplers_base import RandomSampler, Sampler
import random
from PIL import Image, ImageFont
from dataclasses import dataclass


from itertools import product


class DefaultColorSampler(Sampler):
    def __init__(self, step=8):
        r = range(0, 255, step)
        self.colors = tuple(product(r, r, r))

    def __len__(self):
        return len(self.colors)

    def __iter__(self):
        return iter(self.colors)

    def __getitem__(self, idx):
        return self.colors[idx]


@dataclass
class RandomColorSampler(RandomSampler):
    min_r: int = 0
    min_g: int = 0
    min_b: int = 0
    max_r: int = 255
    max_g: int = 255
    max_b: int = 255

    def __getitem__(self, idx):
        r = random.randint(self.min_r, self.max_r)
        g = random.randint(self.min_g, self.max_g)
        b = random.randint(self.min_b, self.max_b)
        return (r, g, b)


class DefaultBackgroundSampler(RandomSampler):
    def __init__(self):
        self.color_sampler = DefaultColorSampler(
            min_r=225,
            min_g=225,
            min_b=225,
        )

    def __getitem__(self, _):
        color = random.choice(self.color_sampler)
        return Image.new("RGB", (512, 512), color)


class DefaultFontSampler(RandomSampler):
    def __init__(self):
        self.font = ImageFont.load_default()

    def __getitem__(self, _):
        return self.font
