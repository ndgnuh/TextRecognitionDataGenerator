from PIL import ImageFont
from os import listdir
from os.path import join as joinpath


class FontDir:
    def __init__(self, path, size=36):
        self.fonts = []
        for file in listdir(path):
            try:
                fpath = joinpath(path, file)
                font = ImageFont.truetype(fpath, size=36)
                self.fonts.append(font)
            except Exception:
                print(f"Can't load {file}")

    def __iter__(self):
        return iter(self.fonts)

    def __len__(self):
        return len(self.fonts)

    def __getitem__(self, i):
        return self.fonts[i]


class FontFile:
    def __init__(self, path, size=36):
        self.font = ImageFont.truetype(path, size=36)

    def __iter__(self):
        return iter([self.font])

    def __len__(self):
        return 1

    def __getitem__(self, i):
        return self.font
