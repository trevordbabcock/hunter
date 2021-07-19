#!/usr/bin/env python3

from opensimplex import OpenSimplex
import random as rand
import time


def main():
    height = 50
    width = 38
    zoom = 0.3

    map = generate_map(height, width, zoom)
    map.render()


def generate_map(height, width, zoom=1, seed=123):
    if seed == None:
        seed = rand.randrange(0, 1000000)
        rand.seed(seed)
        print(f"seed: {seed}")
    else:
        rand.seed(seed)
    
    elevation_thresholds = {
        "mountain": 0.85,
        "land": 0.33,
        "water": 0,
    }

    moisture_thresholds = {
        "forest": 0.5,
    }

    elevation_octaves = [
        Octave(1, 2,  rand.randrange(0, 10000), height, width, zoom),
        Octave(1, 4,  rand.randrange(0, 10000), height, width, zoom),
        Octave(1, 8,  rand.randrange(0, 10000), height, width, zoom),
        Octave(1, 16, rand.randrange(0, 10000), height, width, zoom),
    ]

    moisture_octaves = [
        # randrange(0, 10000)
        Octave(0.7, 2, rand.randrange(0, 10000), height, width, zoom),
        Octave(1,   4, rand.randrange(0, 10000), height, width, zoom),
        Octave(1,   8, rand.randrange(0, 10000), height, width, zoom),
    ]

    # fertility_octaves = []

    elevation_nmap = generate_noise_map(height, width, elevation_octaves)
    elevation_nmap = normalize_noise_map(elevation_nmap)
    moisture_nmap = generate_noise_map(height, width, moisture_octaves)
    moisture_nmap = normalize_noise_map(moisture_nmap)
    geo_map = convert_noise_maps_to_geo_map(height, width, elevation_nmap, moisture_nmap, elevation_thresholds, moisture_thresholds)

    return Map(height, width, zoom, elevation_nmap, moisture_nmap, geo_map)

def generate_noise_map(height, width, octaves):
    noise_map = []

    seed_str = 'seeds: '
    for oct in octaves:
        seed_str += f'{str(oct.seed)}, '

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

def convert_noise_maps_to_geo_map(height, width, e_nmap, m_nmap, elevation_thresholds, moisture_thresholds):
    forest_threshold = 0.5
    geo_map = []
    
    for y in range(height):
        geo_map.append([])

        for x in range(width):
            e = e_nmap[y][x]
            m = m_nmap[y][x]
            if e > elevation_thresholds["mountain"]:
                t = "^"
            elif e > elevation_thresholds["land"]:
                if m > moisture_thresholds["forest"]:
                    t = "F"
                else:
                    t = "G"
            else:
                t = "~"
            
            geo_map[y].append(t)

    return geo_map


class Map():
    def __init__(self, height, width, zoom, elevation_nmap, moisture_nmap, geo_map):
        self.height = height
        self.width = width
        self.zoom = zoom
        self.elevation_nmap = elevation_nmap
        self.moisture_nmap = moisture_nmap
        self.geo_map = geo_map

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                print(self.geo_map[y][x], end="  ")

            print("")


class Octave():
    def __init__(self, a, z, seed, map_height, map_width, zoom):
        self.a = a
        self.z = z
        self.seed = seed
        self.gen = OpenSimplex(seed)
        self.map_height = map_height
        self.map_width = map_width
        self.zoom = zoom
    
    def noise(self, x, y):
        return self.a * self.gen.noise2d(self.z * self.zoom * x * self.map_width / self.map_height, self.z * self.zoom * y * 1)


if __name__ == "__main__":
    main()
