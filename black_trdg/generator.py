from PIL import ImageFont, Image, ImageDraw
from typing import Tuple
from random import randint
from os import path, listdir
import random

from .colors import get_bg_fg_pairings


def generate(
    background: Image,
    text: str,
    font: ImageFont,
    text_color: Tuple[int, int, int],
    stroke_width: int = 0,
):
    """
    - Load the font, use a big font size so that the image is not broken
    - Calculate text bounding box
    - Crop a patch from the background
    - Put the text on the background
    - Distortion, affine transform, etc... [TODO]
    - Resize to desired size
    - Returns both image and text
    """
    # Calculate and get the cropped background
    bg_width, bg_height = background.size
    x1, y1, x2, y2 = font.getbbox(text, stroke_width=stroke_width)
    crop_width, crop_height = x2 - x1, y2 - x1
    if bg_width <= crop_width or bg_height <= crop_height:
        background = background.resize((crop_width, crop_height))
    else:
        crop_x1 = randint(0, bg_width - crop_width - 1)
        crop_y1 = randint(0, bg_height - crop_height - 1)
        crop_box = (crop_x1,
                    crop_y1,
                    crop_x1 + crop_width,
                    crop_y1 + crop_height)
        background = background.crop(crop_box)

    # Put text on background
    draw = ImageDraw.Draw(background)
    draw.font = font
    draw.text((0, 0), text, font=font, fill=text_color)

    return background


def prepare_assets(asset: str, load_function):
    if not isinstance(asset, str):
        return asset

    if path.isfile(asset):
        return [load_function(asset)]
    elif path.isdir(asset):
        return [
            load_function(path.join(asset, file))
            for file in listdir(asset)
        ]
    else:
        raise ValueError("invalid asset")


def load_textfile(textfile):
    with open(textfile) as f:
        return [line.strip() for line in f.readlines()]


class Generator:
    def __init__(self,
                 texts,
                 backgrounds,
                 fonts,
                 text_colors=[(0, 0, 0)],
                 seed=None):
        self.texts = prepare_assets(texts, load_textfile)
        self.backgrounds = prepare_assets(backgrounds, Image.open)
        self.fonts = prepare_assets(
            fonts,
            lambda f: ImageFont.truetype(f, size=32)
        )
        self.text_colors = prepare_assets(text_colors, None)

        self.bg_fg_pairings = get_bg_fg_pairings(
            self.backgrounds, self.text_colors,
        )

        assert len(
            self.bg_fg_pairings) > 0, "No good color matching found, try changing the background/foreground colors"
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def __len__(self):
        return 1000

    def __iter__(self):
        return iter((self[0],))

    def __getitem__(self, _):
        background, text_color = random.choice(self.bg_fg_pairings)
        text = random.choice(self.texts)
        font = random.choice(self.fonts)
        image = generate(background=background,
                         text=text,
                         font=font,
                         text_color=text_color)
        return image, text
