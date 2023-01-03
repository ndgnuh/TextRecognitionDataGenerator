from black_trdg import generator, samplers, transforms
from os import makedirs, path
from tqdm import tqdm
import cv2
import numpy as np

texts = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque feugiat vulputate tellus, nec luctus neque pretium aliquam. Nullam nec dapibus magna, finibus tristique urna. Ut lacus enim, tincidunt quis laoreet nec, faucibus eget ante. Fusce sed vestibulum orci. Etiam consectetur mi est, a vehicula est posuere non. Nulla et augue ac nunc iaculis malesuada. Donec vestibulum bibendum aliquet. Aliquam lacinia tempor dictum. Donec at sagittis lorem. Nunc sodales mauris id sapien auctor volutpat. Praesent hendrerit pharetra tincidunt.
""".split(" ")

texts = samplers.CombineSampler([
    samplers.TextFile(
        "words1.txt"),
    samplers.TextFile(
        "words2.txt"),
    texts
])
g = generator.Generator(
    texts=texts,
    backgrounds=samplers.BackgroundDirectory("bg1"),
    fonts=samplers.FontDirectory("fonts"),
    text_colors=samplers.DefaultColorSampler(),
    transform=transforms.RandomRotate(-4, 4),
    background_transform=transforms.RandomApply([
        transforms.GaussianNoise()
    ]),
)

annotations = []
output_path = "outputs_easy"
image_dir = "images"
count = 0
makedirs(path.join(output_path, image_dir), exist_ok=True)
for (image, text) in tqdm(g, "Generating"):
    count += 1
    name = path.join(image_dir, f"{count:09d}.jpg")
    out_path = path.join(output_path, name)
    annotations.append(f"{out_path}\t{text}")
    image.save(out_path)

with open(path.join(output_path, "annotations.txt"), "w") as f:
    f.write("\n".join(annotations))
