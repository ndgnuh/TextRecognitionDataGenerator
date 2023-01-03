import random
from itertools import product
from PIL import Image, ImageFont
from dataclasses import dataclass
from typing import Tuple
from os import path, listdir
from itertools import cycle


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


class CombineSampler(Sampler):
    def __init__(self, samplers):
        self.samplers = samplers
        self.lens = list(map(len, self.samplers))
        self.n_samplers = len(samplers)

    def __len__(self):
        return sum(self.lens)

    def __getitem__(self, idx):
        sampler_idx = idx % self.n_samplers
        sample_idx = (idx // self.n_samplers) % self.lens[sampler_idx]
        return self.samplers[sampler_idx][sample_idx]


class TextFile(Sampler):
    def __init__(self, file, encoding="utf-8", delim="\n"):
        with open(file, encoding=encoding) as io:
            self.lines = [line.strip() for line in io.read().split(delim)]

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, i):
        return self.lines[i]


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


class BackgroundDirectory(Sampler):
    def __init__(self, bgdir, max_size=None):
        self.backgrounds = [
            Image.open(path.join(bgdir, file))
            for file in listdir(bgdir)
        ]
        if max_size is not None:
            for bg in self.backgrounds:
                bg.thumbnail(max_size)

    def __len__(self):
        return len(self.backgrounds)

    def __getitem__(self, i):
        return self.backgrounds[i]
