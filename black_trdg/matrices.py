from math import sin, cos, tan, radians
import numpy as np
# Check this out:
# https://en.wikipedia.org/wiki/Affine_transformation#/media/File:2D_affine_transformation_matrix.svg


def translate(x, y):
    return np.array([
        [1, 0, x],
        [0, 1, y],
        [0, 0, 1]
    ])


def scale(rx, ry):
    return np.array([
        [rx, 0, 0],
        [0, ry, 0],
        [0, 0, 1]
    ])


def rotate(degree):
    r = radians(degree)
    cr = cos(r)
    sr = sin(r)
    return np.array([
        [cr, -sr, 0],
        [sr, cr, 0],
        [0, 0, 1]
    ])


def shearx(degree):
    r = radians(degree)
    return np.array([
        [1, tan(r), 0],
        [0, 1, 0],
        [0, 0, 1]
    ])


def sheary(degree):
    r = radians(degree)
    return np.array([
        [1, 0, 0],
        [tan(r), 1, 0],
        [0, 0, 1]
    ])


def compose(matrices):
    m = matrices[0]
    for m2 in matrices[1:]:
        m = np.dot(m, m2)
    return m
