from json import loads
import numpy as np
from os import popen
from tcod.console import Console

from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import camp as cp

from hunter_pkg.helpers.coord import Coord
from hunter_pkg.helpers import generic as gen
from hunter_pkg.helpers import math

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import terrain


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

terrain_map = {
    "G": terrain.Grass(),
    "F": terrain.Forest(),
    "^": terrain.Mountain(),
    "~": terrain.Water(),
}

class GameMap:
    def __init__(self, width, height, seed, show_fog):
        self.height = height
        self.width = width
        self.tiles, self.path_map = self.init_empty_map()
        self.show_fog = show_fog
        self.next_redraw_column = None
        self.generate_map(seed)
        #self.load_map_from_file('resources/maps/large_zoomed_map.txt')
        self.redraw_all()

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

    def generate_map(self, seed):
        stream = popen(f"ruby bin/generate_map.rb {self.height}x{self.width} hunter_pkg/config/map/standard-map.json {seed} --json")
        map_data = loads(stream.read())

        for y in range(len(map_data["grid"])):
            row = map_data["grid"][y]
            for x in range(len(row)):
                self.tiles[y].append(Tile(self, terrain_map[row[x].strip()], x, y))
                self.path_map[y].append(1 if self.tiles[y][x].terrain.walkable else 0)

    def in_bounds(self, x, y):
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def clamp_coord(self, x, y):
        max_x = self.width - 1
        max_y = self.height - 1
        dest = Coord()
        dest.x = math.clamp(x, 0, max_x)
        dest.y = math.clamp(y, 0, max_y)

        return dest

    def render(self, console, time_of_day):
        indices = np.argwhere(self.redraw_matrix>0)

        for y, x in indices:
            console.tiles_rgb[x,y] = self.tiles[y][x].get_graphic_dt(time_of_day)

        self.redraw_reset()

    def get_tile(self, x, y):
        if y < 0 or x < 0 or y >= self.height or x >= self.width:
            return None
        else:
            return self.tiles[y][x]

    def redraw_tile(self, x, y):
        self.redraw_matrix[y, x] = True

    def redraw_tiles(self, top_left_coord, bottom_right_coord):
        for y in range(top_left_coord.y, bottom_right_coord.y + 1):
            for x in range(top_left_coord.x, bottom_right_coord.x + 1):
                self.redraw_matrix[y, x] = True

    def redraw_reset(self):
        self.redraw_matrix = np.zeros((self.height, self.width), dtype=bool)

    def redraw_all(self):
        self.redraw_matrix = np.ones((self.height, self.width), dtype=bool)

    def redraw_all_transition(self):
        self.next_redraw_column = self.width - 1

    def progress_redraw_all_transition(self):
        if self.next_redraw_column != None:
            for i in range(3):
                for row in self.redraw_matrix:
                    row[self.next_redraw_column] = True
                
                if self.next_redraw_column == 0:
                    self.next_redraw_column = None
                    break
                else:
                    self.next_redraw_column -= 1


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
                    if isinstance(entity, cp.Camp) and entity.is_visible():
                        return self.terrain.get_graphic_dt(time_of_day, entity.char, entity.fg_color, entity.bg_color)
                    elif isinstance(entity, bb.BerryBush) and entity.is_visible():
                        return self.terrain.get_graphic_dt(time_of_day, None, None, entity.bg_color(time_of_day))
            else:
                return (ord(" "), colors.black(), colors.black())
        else:
            for entity in self.entities:
                if isinstance(entity, cp.Camp) and entity.is_visible():
                    return self.terrain.get_graphic_dt(time_of_day, entity.char, entity.fg_color, entity.bg_color)
                elif isinstance(entity, bb.BerryBush) and entity.is_visible():
                    return self.terrain.get_graphic_dt(time_of_day, None, None, colors.dark_green(time_of_day))

            if self.hovered:
                return self.terrain.get_graphic_dt(time_of_day, None, None, colors.light_gray())

        return self.terrain.get_graphic_dt(time_of_day, None, None, None) # gross as hell

    def add_entities(self, entities):
        self.entities.extend(entities)
        self.redraw()

    def remove_entities(self, entities):
        for e in entities:
            self.entities.remove(e)

        self.redraw()

    # TODO should probably be moved off of Tile
    def select_next_entity(self, engine):
        if len(self.entities) > 0:
            current_index = None

            for i in range(len(self.entities)):
                if self.entities[i] == engine.selected_entity:
                    current_index = i
                    break

            if current_index == None:
                next_index = 0
            else:
                next_index = current_index + 1

            if next_index >= len(self.entities):
                next_index = 0
            
            if gen.has_method(engine.selected_entity, "deselect"):
                engine.selected_entity.deselect()

            engine.selected_entity = None
            flog.debug("deselected")

            engine.selected_entity = self.entities[next_index]

            if gen.has_method(engine.selected_entity, "select"):
                engine.selected_entity.select()

            flog.debug(f"{engine.selected_entity.__class__} is selected")
        else:
            if gen.has_method(engine.selected_entity, "deselect"):
                engine.selected_entity.deselect()

            engine.selected_entity = None
            flog.debug("deselected")

    def reveal(self):
        self.explored = True
        self.redraw()
    
    def redraw(self):
        self.game_map.redraw_tile(self.x, self.y)
    