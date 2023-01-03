from PIL import ImageFont, Image, ImageDraw
from typing import Tuple, Optional, Callable
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
    transform: Optional[Callable] = None,
    background_transform: Optional[Callable] = None,
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
    # Estimate the text bounding box
    x1, y1, x2, y2 = font.getbbox(text, stroke_width=stroke_width)
    crop_width, crop_height = x2 - x1, y2 - x1

    # Create the empty text box
    text_mask = Image.new("RGBA", (crop_width, crop_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_mask)
    draw.font = font
    draw.text((0, 0), text, font=font, fill=text_color)

    # Apply transformation(s) if any
    if transform is not None:
        text_mask = transform(text_mask)

    # Get the real crop size and get the cropped background
    crop_width, crop_height = text_mask.size
    bg_width, bg_height = background.size
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
    if background_transform is not None:
        background = background_transform(background)

    # Composite fg and bg
    output = Image.alpha_composite(background.convert("RGBA"), text_mask)
    output = output.convert("RGB")  # To write JPG

    return output


def prepare_assets(asset: str, load_function):
    if not isinstance(asset, str):
        return asset

    if path.isfile(asset):
        return [load_function(asset)]
    elif path.isdir(asset):
        assets = [
            load_function(path.join(asset, file))
            for file in listdir(asset)
        ]
        return assets
    else:
        raise ValueError("invalid asset")


def load_textfile(textfile):
    with open(textfile) as f:
        return [line.strip() for line in f.readlines()]


class Generator(tuple):
    def __init__(self,
                 texts,
                 backgrounds,
                 fonts,
                 text_colors=[(0, 0, 0)],
                 transform=None,
                 background_transform=None,
                 count=None,
                 seed=None):
        self.texts = prepare_assets(texts, load_textfile)
        self.count = len(self.texts) if count is None else count
        self.backgrounds = prepare_assets(backgrounds, Image.open)
        self.fonts = prepare_assets(
            fonts,
            lambda f: ImageFont.truetype(f, size=48)
        )
        self.text_colors = prepare_assets(text_colors, None)

        self.bg_fg_pairings = get_bg_fg_pairings(
            self.backgrounds, self.text_colors,
        )
        self.background_transform = background_transform
        self.transform = transform

        assert len(
            self.bg_fg_pairings) > 0, "No good color matching found, try changing the background/foreground colors"
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def __len__(self):
        return self.count

    def __iter__(self):
        return iter(self[i] for i in range(self.count))

    def __getitem__(self, _):
        background, text_color = random.choice(self.bg_fg_pairings)
        text = random.choice(self.texts)
        font = random.choice(self.fonts)
        image = generate(background=background,
                         text=text,
                         font=font,
                         text_color=text_color,
                         transform=self.transform,
                         background_transform=self.background_transform)
        return image, text
