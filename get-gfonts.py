import json
from argparse import ArgumentParser
from os import path
parser = ArgumentParser()
parser.add_argument("--lang")
parser.add_argument("--display", action="store_true", default=False)
parser.add_argument("--handwriting", action="store_true", default=False)
parser.add_argument("--monospace", action="store_true", default=False)

args = parser.parse_args()
with open("./webfonts.json", encoding="utf-8") as f:
    data = json.load(f)['items']

if args.lang is not None:
    data = [font for font in data
            if args.lang in font['subsets']]

if not args.display:
    data = [font for font in data
            if font['category'] != 'display']
if not args.handwriting:
    data = [font for font in data
            if font['category'] != 'handwriting']
if not args.monospace:
    data = [font for font in data
            if font['category'] != 'monospace']

fonts = []
for font in data:
    family = font['family']
    for name, url in font['files'].items():
        _, ext = path.splitext(url)
        fonts.append(f"{family}{name}{ext}\t{url}")

print("\n".join(fonts))
