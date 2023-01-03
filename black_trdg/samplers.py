import random
from itertools import product
from PIL import Image, ImageFont
from dataclasses import dataclass
from typing import Tuple
from os import path, listdir


from .samplers_base import RandomSampler, Sampler


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
    min: Tuple[int, int, int] = (0, 0, 0)
    max: Tuple[int, int, int] = (255, 255, 255)

    def __getitem__(self, idx):
        min_r, min_g, min_b = self.min
        max_r, max_g, max_b = self.max
        r = random.randint(min_r, max_r)
        g = random.randint(min_g, max_g)
        b = random.randint(min_b, max_b)
        return (r, g, b)


class DefaultBackgroundSampler(RandomSampler):
    def __init__(self):
        self.color_sampler = RandomColorSampler(
            max=(90, 90, 90)
        )

    def __getitem__(self, _):
        color = random.choice(self.color_sampler)
        return Image.new("RGB", (512, 512), color)


class DefaultFontSampler(RandomSampler):
    def __init__(self):
        self.font = ImageFont.load_default()

    def __getitem__(self, _):
        return self.font


class FontFile(Sampler):
    def __init__(self, file, size=36):
        self.font = ImageFont.truetype(file, size=36)

    def __iter__(self):
        return iter((self[0],))

    def __len__(self):
        return 1

    def __getitem__(self, _):
        return self.font


class FontDirectory(Sampler):
    def __init__(self, fontdir, size=36):
        self.fonts = [
            ImageFont.truetype(path.join(fontdir, file), size=36)
            for file in listdir(fontdir)
        ]

    def __iter__(self):
        return iter(self.fonts)

    def __len__(self):
        return len(self.fonts)

    def __getitem__(self, i):
        return self.fonts[i]
