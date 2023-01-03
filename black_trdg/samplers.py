from .samplers_base import RandomSampler
import random
from PIL import Image, ImageFont


class DefaultColorSampler(RandomSampler):
    def __getitem__(self, idx):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return (r, g, b)


class DefaultBackgroundSampler(RandomSampler):
    def __init__(self):
        self.color_sampler = DefaultColorSampler()

    def __getitem__(self, _):
        color = random.choice(self.color_sampler)
        return Image.new("RGB", (512, 512), color)


class DefaultFontSampler(RandomSampler):
    def __init__(self):
        self.font = ImageFont.load_default()

    def __getitem__(self, _):
        return self.font
