#!/usr/bin/env python3

from opensimplex import OpenSimplex
from random import randrange
import time


def main():
    height = 50
    width = 38
    zoom = 0.5

    # height = 65
    # width = 150

    octaves = [
        # Octave(0.5,     2, randrange(0, 10000), height, width),
        # Octave(0.5,     4, randrange(0, 10000), height, width),
        # Octave(0.25,    8, randrange(0, 10000), height, width),
        # Octave(0.025,   16, randrange(0, 10000), height, width),

        Octave(1,         zoom * 2, 9732, height, width),
        Octave(1,         zoom * 4, 44, height, width),
        Octave(1,         zoom * 8, 103, height, width),
        Octave(1,         zoom * 16, 3062, height, width),

        # Octave(0.5,     zoom * 2, 9732, height, width),
        # Octave(0.5,     zoom * 4, 44, height, width),
        # Octave(0.25,    zoom * 8, 103, height, width),
        # Octave(0.025,   zoom * 16, 3026, height, width),
        # Octave(0.025,   zoom * 32, 3026, height, width),
    ]

    nmap = generate_noise_map(height, width, octaves)
    nmap = normalize_noise_map(nmap)
    render_noise_map(nmap)
    render_geo_map(nmap)


def generate_noise_map(height, width, octaves):
    noise_map = []

    seed_str = 'seeds: '
    for oct in octaves:
        seed_str += f'{str(oct.seed)}, '

    print(seed_str)

    for y in range(height):
        noise_map.append([])

        for x in range(width):
            nx = x/width - 0.5
            ny = y/height - 0.5

            ls = []

            for oct in octaves:
                ls.append(oct.a * oct.noise(nx, ny))

            r = 0
            for l in ls:
                r += l

            r = round(r, 3)
            noise_map[y].append(r)

    return noise_map

def normalize_noise_map(nmap):
    min = None
    max = None

    for y, row in enumerate(nmap):
        for x, n in enumerate(row):
            if max == None or n > max:
                max = n
            if min == None or n < min:
                min = n

    for y, row in enumerate(nmap):
        for x, n in enumerate(row):
            row[x] = normalize_to_range(n, min, max, 0, 1)

    return nmap

def normalize_to_range(n, old_min, old_max, new_min, new_max):
    return round((new_max - new_min)/(old_max - old_min)*(n-old_max)+new_max, 3) # rounding here might be a bad idea

def render_noise_map(nmap):
    for y, row in enumerate(nmap):
        for x, n in enumerate(row):
            str_n = "%01.3f"%n

            #print(str_n, end=" ")
        
        #print("\n")


def render_geo_map(nmap):
    for y, row in enumerate(nmap):
        for x, n in enumerate(row):
            if n > 0.93:
                char = "^"
                t = f'\033[0;31m{char}\033[0m'
            elif n > 0.85:
                char = "m"
                t = f'\033[0;31m{char}\033[0m'
            elif n > 0.65:
                char = "%"
                t = f'\033[0;33m{char}\033[0m'
            elif n > 0.6:
                char = "0"
                t = f'\033[0;33m{char}\033[0m'
            elif n > 0.55:
                char = "o"
                t = f'\033[0;33m{char}\033[0m'
            elif n > 0.33:
                char = "="
                t = f'\033[0;32m{char}\033[0m'
            else:
                char = "~"
                t = f'\033[0;34m{char}\033[0m'

            print(t, end="  ")

        print("")


class Octave():
    def __init__(self, a, z, seed, map_height, map_width):
        self.a = a
        self.z = z
        self.seed = seed
        self.gen = OpenSimplex(seed)
        self.map_height = map_height
        self.map_width = map_width
    
    def noise(self, x, y):
        return self.a * self.gen.noise2d(self.z * x * self.map_width / self.map_height, self.z * y * 1)


if __name__ == "__main__":
    main()
