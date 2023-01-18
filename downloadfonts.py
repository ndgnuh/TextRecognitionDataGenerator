import questionary as Q
import gdown
import os
import json
from os import path
from tqdm import tqdm
from argparse import Namespace
from lenses import bind


def read_json(f):
    with open(f, encoding="utf-8") as io:
        return json.load(io)


def unique(s):
    return sorted(list(set(s)))


catalogue = read_json("webfonts.json")["items"]

choices = Namespace()
choices.categories = unique(bind(catalogue).Each()["category"].collect())
choices.subsets = unique(bind(catalogue).Each()["subsets"].Each().collect())
choices.variants = unique(bind(catalogue).Each()["variants"].Each().collect())

prompts = dict(
    category=Q.checkbox("Font styles",
                        choices=choices.categories,
                        default="sans-serif"),
    subset=Q.autocomplete("Subset (language)",
                          choices=choices.subsets,
                          default="latin",
                          validate=lambda x: x in choices.subsets),
    variants=Q.checkbox("Font variants",
                        choices=choices.variants,
                        default="regular"),
)

answers = dict()
for k, v in prompts.items():
    answers[k] = v.ask()

fonts = catalogue
fonts = [font for font in fonts
         if answers['subset'] in font['subsets']
         and font['category'] in answers['category']]

font_files = dict()
for font in tqdm(fonts, "Getting font files URI"):
    for variant in answers['variants']:
        uri = font['files'].get(variant, None)
        if uri is not None:
            name = font['family'] + "_" + variant
            name = name.replace(" ", "+")
            font_files[name] = uri

output_directory = Q.path(
    "Output directory?",
    default=path.join("resources", "fonts", answers['subset']) + "/"
).ask()
os.makedirs(output_directory, exist_ok=True)
for name, uri in tqdm(font_files.items(), "Downloading Fonts"):
    ext = path.splitext(uri)[-1]
    output = path.join(output_directory, f"{name}{ext}")
    gdown.download(uri, output)
