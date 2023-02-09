import yaml
import random
from os import makedirs, path
from traceback import print_exc
from argparse import ArgumentParser
from icecream import ic
from black_trdg import samplers as S
from black_trdg import transforms, generator
from tqdm import tqdm
from matplotlib import pyplot as plt


def read_config(file):
    with open(file) as io:
        config = yaml.load(io, Loader=yaml.FullLoader)
    return config


def main():
    parser = ArgumentParser()
    parser.add_argument("config", help="Path to config file")
    parser.add_argument("output", help="Path to output directory")
    parser.add_argument("--count", "-n", dest="count",
                        help="Number of samples")
    args = parser.parse_args()

    config = read_config(args.config)

    # Text samplers
    samplers = []
    for f in config['texts']['vocabs']:
        sampler = S.VocabFileSampler(
            f,
            length=(config['min_length'], config['max_length'])
        )
        samplers.append(sampler)
    del sampler
    for f in config['texts']['dictionaries']:
        sampler = S.TextFile(f)
        samplers.append(sampler)
    del sampler
    for f in config['texts'].get('directories', []):
        sampler = S.TextDirectory(f, suffix=".txt")
        samplers.append(sampler)
    texts = S.CombineSampler(samplers)

    # Background samplers
    samplers = []
    for d in config["backgrounds"].get("images", []):
        sampler = S.BackgroundDirectory(d)
        samplers.append(sampler)
    for d in config["backgrounds"].get("colors", []):
        sampler = S.DefaultBackgroundSampler(min=d['from'], max=d['to'])
        samplers.append(sampler)
    backgrounds = S.CombineSampler(samplers)

    # Font samplers
    fonts = S.FontDirectory(config['fonts'])

    # Other samplers
    # TODO
    text_colors = S.DefaultColorSampler()
    transform = transforms.RandomApply([
        transforms.RandomRotate(-3, 3),
        transforms.RandomPadding((-5, 20))
    ])
    background_transform = transforms.RandomApply([
        transforms.GaussianNoise()
    ])

    g = generator.Generator(
        texts=texts,
        backgrounds=backgrounds,
        fonts=fonts,
        text_colors=text_colors,
        transform=transform,
        background_transform=background_transform,
        count=args.count,
    )

    # Generate data
    annotations = []
    output_path = args.output
    image_dir = "images"
    count = 0
    makedirs(path.join(output_path, image_dir), exist_ok=True)
    for (image, text) in tqdm(g, "Generating"):
        count += 1
        name = path.join(image_dir, f"{count:09d}.jpg")
        out_path = path.join(output_path, name)
        try:
            image.save(out_path)
            annotations.append(f"{image_dir}/{name}\t{text}")
        except ValueError:
            ic(text)
            print_exc()

    with open(path.join(output_path, "annotations.txt"), "w") as f:
        f.write("\n".join(annotations))


if __name__ == "__main__":
    main()
