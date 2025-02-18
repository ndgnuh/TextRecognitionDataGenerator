import random
from itertools import product
from PIL import Image, ImageFont
from dataclasses import dataclass
from typing import Tuple
from os import path, listdir
from itertools import cycle


from .utils import find
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
    def __init__(self, max=(90, 90, 90), min=(0, 0, 0)):
        self.color_sampler = RandomColorSampler(
            max=max,
            min=min
        )

    def __getitem__(self, _):
        color = random.choice(self.color_sampler)
        return Image.new("RGB", (1024, 1024), color)


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
        return max(self.lens) * self.n_samplers

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
        self.fonts = []
        for file in listdir(fontdir):
            try:
                font = ImageFont.truetype(path.join(fontdir, file), size=36)
                self.fonts.append(font)
            except Exception:
                print(f"Can't load {file}")

    def __iter__(self):
        return iter(self.fonts)

    def __len__(self):
        return len(self.fonts)

    def __getitem__(self, i):
        return self.fonts[i]


class BackgroundDirectory(Sampler):
    def __init__(self, bgdir, max_size=None):

        self.backgrounds = []
        for file in listdir(bgdir):
            try:
                bg = Image.open(path.join(bgdir, file))
                self.backgrounds.append(bg)
            except Exception:
                print(f"Can't load {file}")

        if max_size is not None:
            for bg in self.backgrounds:
                bg.thumbnail(max_size)

    def __len__(self):
        return len(self.backgrounds)

    def __getitem__(self, i):
        return self.backgrounds[i]


def TextDirectory(root_dir, suffix, encoding="utf-8", delim="\n"):
    files = find(root_dir, name=suffix, type="f")
    samplers = [TextFile(file, encoding, delim) for file in files]
    return CombineSampler(samplers)


class VocabFileSampler(Sampler):
    def __init__(self, vocab_file, length):
        with open(vocab_file) as f:
            vocabs = f.read().strip()
            if " " not in vocabs:
                vocabs = vocabs + " "
            self.vocabs = vocabs

        if isinstance(length, int):
            self.min_length = length
            self.max_length = length
        else:
            self.min_length = min(length)
            self.max_length = max(length)

    def __len__(self):
        return 100_000

    def __getitem__(self, idx):
        k = random.randint(self.min_length, self.max_length)
        list_text = random.choices(self.vocabs, k=k)
        text = ''.join(list_text)
        return text
