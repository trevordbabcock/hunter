from tcod.console import Console

from hunter_pkg import colors
from hunter_pkg import static_entity
from hunter_pkg import terrain


terrain_map = {
    "G": terrain.Ground(),
    "F": terrain.Forest(),
    "^": terrain.Mountain(),
    "~": terrain.Water(),
}

class GameMap:
    def __init__(self, width: int, height: int):
        self.height = height
        self.width = width
        self.tiles, self.path_map = self.init_empty_map()
        self.load_map_from_file('resources/maps/large_zoomed_map.txt')

    def init_empty_map(self):
        tiles = []
        path_map = []

        for i in range(self.height):
            tiles.append([])
            path_map.append([])

        return tiles, path_map

    def load_map_from_file(self, filepath):
        with open(filepath) as file:
            line = file.readline()
            y = 0
            while line:
                x = 0
                cells = line.split(" ")

                for cell in cells:
                    if cell != '':
                        self.tiles[y].append(Tile(terrain_map[cell.strip()], x, y))
                        self.path_map[y].append(1 if self.tiles[y][x].terrain.walkable else 0)
                        x = x + 1

                line = file.readline()
                y = y + 1


    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        for y in range(self.height):
            for x in range(self.width):
                console.tiles_rgb[x,y] = self.tiles[y][x].get_graphic_dt()

class Tile:
    def __init__(self, terrain, x, y):
        self.terrain = terrain
        self.entities = []
        self.x = x
        self.y = y

    def get_graphic_dt(self):
        for entity in self.entities:
            if isinstance(entity, static_entity.BerryBush):
                return self.terrain.get_graphic_dt(None, None, colors.dark_green())

        return self.terrain.get_graphic_dt(None, None, None) # gross as hell
