from dataclasses import dataclass
from typing import Optional, Tuple
from PIL import Image
from os import path, listdir
from functools import cached_property, lru_cache
from tqdm import tqdm
import random


@dataclass(eq=True, frozen=True)
class ImageDir:
    path: str
    max_size: Optional[Tuple[int, int]] = None

    @cached_property
    def files(self):
        files = []
        pbar = tqdm(listdir(self.path), desc="Verifying files")
        for file in pbar:
            try:
                file_path = path.join(self.path, file)
                Image.open(file_path)
                files.append(file_path)
            except Exception:
                print(f"Can't load {file}")

        return files

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return len(self.files)

    @lru_cache
    def __getitem__(self, i):
        image = Image.open(self.files[i])
        image.load()
        if self.max_size is not None:
            image.thumbnail(self.max_size)
        return image


@dataclass(eq=True, frozen=True)
class Color:
    a: Tuple = (0, 0, 0)
    b: Tuple = (23, 23, 23)
    image: bool = True
    count: int = 1

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return self.count

    def __getitem__(self, idx):
        min_r, min_g, min_b = self.a
        max_r, max_g, max_b = self.b
        r = random.randint(min_r, max_r)
        g = random.randint(min_g, max_g)
        b = random.randint(min_b, max_b)
        c = (r, g, b)
        if self.image:
            return Image.new("RGB", (32, 32), c)
        else:
            return c
