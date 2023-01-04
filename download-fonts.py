from argparse import ArgumentParser
from os import path
from tqdm import tqdm
import gdown

parser = ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")

args = parser.parse_args()

with open(args.input) as f:
    data = [line.strip().split("\t") for line in f.readlines()]


for name, url in tqdm(data):
    output = path.join(args.output, name).replace(" ", "_")
    gdown.download(url, output)
