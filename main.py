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
from black_trdg import samplers


def read_config(file):
    with open(file) as io:
        config = yaml.load(io, Loader=yaml.FullLoader)
    return config


def init_from_config(
    ns,  # namespace
    config,
    copy=False
):
    if copy:
        config = copy(config)
    name = config.pop("name")
    Class = getattr(ns, name)
    return Class(**config)


def init_samplers(configs):
    ss = []
    for config in configs:
        sampler = init_from_config(samplers, config)
        ss.append(sampler)
    return samplers.CombineSampler(ss)


def main():
    parser = ArgumentParser()
    parser.add_argument("config", help="Path to config file")
    args = parser.parse_args()

    config = read_config(args.config)

    # Text samplers
    # samplers = []
    # for f in config['texts']['vocabs']:
    #     sampler = S.VocabFileSampler(
    #         f,
    #         length=(config['min_length'], config['max_length'])
    #     )
    #     samplers.append(sampler)
    # for f in config['texts']['dictionaries']:
    #     sampler = S.TextFile(f, config['min_length'], config['max_length'])
    #     samplers.append(sampler)
    # for f in config['texts'].get('directories', []):
    #     sampler = S.TextDirectory(f, suffix=".txt")
    #     samplers.append(sampler)
    # texts = S.CombineSampler(samplers)

    texts = init_samplers(config['texts'])
    backgrounds = init_samplers(config['backgrounds'])
    fonts = init_samplers(config['fonts'])
    text_colors = init_samplers(config['foregrounds'])
    count = config['count']

    transform = transforms.RandomApply([
        transforms.RandomRotate(-3, 3),
        transforms.RandomPadding((1, 10))
    ])
    background_transform = transforms.RandomApply([
        transforms.GaussianNoise()
    ])

    g = generator.Generator(
        texts=texts,
        backgrounds=backgrounds,
        fonts=fonts,
        text_colors=text_colors,
        transform=lambda x: x,
        background_transform=lambda x: x,
        count=count,
    )

    # Generate data
    annotations = []
    output_path = config['output']
    image_dir = "images"
    count = 0
    makedirs(path.join(output_path, image_dir), exist_ok=True)
    for (image, text) in tqdm(g, "Generating"):
        count += 1
        name = path.join(image_dir, f"{count:09d}.jpg")
        out_path = path.join(output_path, name)
        try:
            image.save(out_path)
            annotations.append(f"{name}\t{text}")
        except ValueError:
            ic(text)
            print_exc()

    with open(path.join(output_path, "annotations.txt"), "w") as f:
        f.write("\n".join(annotations))


if __name__ == "__main__":
    main()
