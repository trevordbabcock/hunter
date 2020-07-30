import numpy as np  # type: ignore
from tcod.console import Console

import tile_types


tile_type_map = {
    "G": tile_types.ground,
    "F": tile_types.forest,
    "^": tile_types.mountain,
    "~": tile_types.water,
}

class GameMap:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.ground, order="F")
        self.load_map_from_file('resources/maps/large_zoomed_map.txt')

    def load_map_from_file(self, filepath):
        with open(filepath) as file:
            line = file.readline()
            y = 0
            while line:
                x = 0
                cells = line.split(" ")

                for cell in cells:
                    if cell != '':
                        self.tiles[x, y] = tile_type_map[cell.strip()]
                        x = x + 1

                line = file.readline()
                y = y + 1

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        console.tiles_rgb[0:self.width, 0:self.height] = self.tiles["dark"]
