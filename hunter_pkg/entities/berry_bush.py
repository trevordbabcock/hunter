from typing import Tuple

from hunter_pkg.entities import base_entity
from hunter_pkg.helpers import rng

from hunter_pkg import colors
from hunter_pkg import stats


class BerryBush(base_entity.StaticEntity):
    def __init__(self, engine, x, y):
        super().__init__(engine, x, y, stats.Stats.map()["berry-bush"]["update-interval"]) # ms
        self.bg_color = colors.dark_green
        self.berry_limit = rng.range(stats.Stats.map()["berry-bush"]["min-berry-limit"], stats.Stats.map()["berry-bush"]["max-berry-limit"])
        self.num_berries = rng.range(stats.Stats.map()["berry-bush"]["spawn-min-berries"], stats.Stats.map()["berry-bush"]["spawn-max-berries"], 1)

    def progress(self):
        self.grow_berry()
    
    def pick_berry(self):
        if self.num_berries > 0:
            self.num_berries -= 1
            return Berry()
        else:
            return None

    def grow_berry(self):
        if self.num_berries < self.berry_limit:
            self.num_berries += rng.range(stats.Stats.map()["berry-bush"]["grow-min-berries"], stats.Stats.map()["berry-bush"]["grow-max-berries"])

class Berry():
    def __init__(self):
        self.nutritional_value = stats.Stats.map()["berry"]["nutritional-value"]

    def consume(self):
        pass