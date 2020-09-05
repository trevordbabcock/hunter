from random import randrange
from typing import Tuple

from hunter_pkg.entities import base_entity
from hunter_pkg import colors
from hunter_pkg import stats


class BerryBush(base_entity.StaticEntity):
    def __init__(self, engine, x, y):
        super().__init__(engine, x, y, stats.Stats.map()["berry-bush"]["update-interval"]) # ms
        self.bg_color = colors.dark_green
        self.num_berries = randrange(stats.Stats.map()["berry-bush"]["spawn-min-berries"], stats.Stats.map()["berry-bush"]["spawn-max-berries"], 1)

    def progress(self):
        self.grow_berry()
    
    def pick_berry(self):
        if self.num_berries > 0:
            self.num_berries -= 1
            return Berry()
        else:
            return None

    def grow_berry(self):
        self.num_berries += stats.Stats.map()["berry-bush"]["grow-berries"]

class Berry():
    def __init__(self):
        self.nutritional_value = stats.Stats.map()["berry"]["nutritional-value"]