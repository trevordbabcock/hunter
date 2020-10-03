from tcod.console import Console

from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import camp as cp

from hunter_pkg import colors
from hunter_pkg import terrain


terrain_map = {
    "G": terrain.Grass(),
    "F": terrain.Forest(),
    "^": terrain.Mountain(),
    "~": terrain.Water(),
}

class GameMap:
    def __init__(self, width: int, height: int, show_fog):
        self.height = height
        self.width = width
        self.tiles, self.path_map = self.init_empty_map()
        self.show_fog = show_fog
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
                        self.tiles[y].append(Tile(self, terrain_map[cell.strip()], x, y))
                        self.path_map[y].append(1 if self.tiles[y][x].terrain.walkable else 0)
                        x = x + 1

                line = file.readline()
                y = y + 1

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console, time_of_day):
        for y in range(self.height):
            for x in range(self.width):
                console.tiles_rgb[x,y] = self.tiles[y][x].get_graphic_dt(time_of_day)

    def add_entities_to_tile(self, x, y, entities):
        for e in entities:
            self.tiles[y][x].entities.append(e)


class Tile:
    def __init__(self, game_map, terrain, x, y):
        self.game_map = game_map
        self.terrain = terrain
        self.entities = []
        self.x = x
        self.y = y
        self.hovered = False
        self.explored = False

    # TODO fix this; it is nightmare fuel
    def get_graphic_dt(self, time_of_day):
        if self.game_map.show_fog:
            if self.hovered:
                if self.explored:
                    for entity in self.entities:
                        if isinstance(entity, cp.Camp):
                            return self.terrain.get_graphic_dt(time_of_day, entity.char, entity.fg_color, entity.bg_color)

                    return self.terrain.get_graphic_dt(time_of_day, None, None, colors.light_gray())
                else:
                    return self.terrain.get_graphic_dt(time_of_day, ord(" "), None, colors.light_gray())
            elif self.explored:
                for entity in self.entities:
                    if isinstance(entity, cp.Camp):
                        return self.terrain.get_graphic_dt(time_of_day, entity.char, entity.fg_color, entity.bg_color)
                    elif isinstance(entity, bb.BerryBush):
                        return self.terrain.get_graphic_dt(time_of_day, None, None, entity.bg_color(time_of_day))
            else:
                return (ord(" "), colors.black(), colors.black())
        else:
            for entity in self.entities:
                if isinstance(entity, cp.Camp):
                    return self.terrain.get_graphic_dt(time_of_day, entity.char, entity.fg_color, entity.bg_color)
                elif isinstance(entity, bb.BerryBush):
                    return self.terrain.get_graphic_dt(time_of_day, None, None, colors.dark_green(time_of_day))

            if self.hovered:
                return self.terrain.get_graphic_dt(time_of_day, None, None, colors.light_gray())

        return self.terrain.get_graphic_dt(time_of_day, None, None, None) # gross as hell
