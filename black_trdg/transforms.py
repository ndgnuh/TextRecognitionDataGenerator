from PIL import Image
from PIL.Image import Resampling
from dataclasses import dataclass
import random


@dataclass
class RandomRotate:
    min_degree: int = -3
    max_degree: int = 3

    def __call__(self, image):
        degree = random.randint(self.min_degree, self.max_degree)
        # NEAREST IS NOT ENOUGH
        # TEXT IMAGE WILL BE BROKEN BY THE ROTATION
        return image.rotate(degree, expand=True, resample=Resampling.BILINEAR)


@dataclass
class RandomShear:
    min_degree: int = -3
    max_degree: int = -3
