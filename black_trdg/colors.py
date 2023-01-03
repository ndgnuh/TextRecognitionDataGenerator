from typing import List, Tuple
from PIL import Image
from itertools import product


def get_luminance(rgb):
    # input is 255-base rgb
    r, g, b = rgb
    L = 0.2126*r + 0.72152 * g + 0.0722*b
    L = L / 255
    return L


def get_contrast(c1, c2):
    if not isinstance(c1, float):
        c1 = get_luminance(c1)
    if not isinstance(c2, float):
        c2 = get_luminance(c2)
    contrast = (max(c1, c2) + 0.05) / (min(c1, c2) + 0.05)
    return contrast


def get_dominance_colors(image, num_colors):
    image = image.copy()
    image.thumbnail((56, 56))
    q_image = image.quantize(num_colors).convert("RGB")
    return set([color for _, color in q_image.getcolors()])


def safe_tqdm(iterable, *a, **k):
    try:
        from tqdm import tqdm
        return tqdm(
            iterable,
            *a, **k
        )
    except ImportError:
        return iterable


def get_bg_fg_pairings(backgrounds: List[Image.Image],
                       colors: List[Tuple[int, int, int]],
                       num_colors: int = 3,
                       contrast_threshold: float = 3):
    pairings = []
    for background in safe_tqdm(backgrounds, "Pairing bg and fg colors"):
        palettes = get_dominance_colors(background, num_colors)
        for fg in colors:
            min_contrast = min(get_contrast(bg, fg) for bg in palettes)
            if min_contrast >= contrast_threshold:
                pairings.append((background, fg))
    return pairings
