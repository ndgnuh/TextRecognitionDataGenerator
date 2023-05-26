from fontTools.ttLib import TTFont
from fontTools.unicode import Unicode
import sys
from argparse import ArgumentParser
from os import path
import os

parser = ArgumentParser()
parser.add_argument("--vocab", "-c", required=True)
parser.add_argument("font")
args = parser.parse_args()

if path.isdir(args.font):
    args.font = [path.join(args.font, font) for font in os.listdir(args.font)]
else:
    args.font = [args.font]

with open(args.vocab) as f:
    vocab = f.read().replace("\n", "")


def has_glyph(font, glyph):
    for table in font['cmap'].tables:
        if ord(glyph) in table.cmap.keys():
            return True
    return False


for font_file in args.font:
    font = TTFont(font_file)
    missings = []
    for c in vocab:
        if not has_glyph(font, c):
            missings.append(c)
    if len(missings) > 0:
        print("Missing %s in %s" % (font_file, missings))
