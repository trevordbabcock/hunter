from random import randrange
from typing import Tuple

import ai
import colors
import entity
from stats import Stats


class StaticEntity():
    def __init__(self, engine, x, y, update_interval):
        self.engine = engine
        self.x = x
        self.y = y
        self.update_interval = update_interval
    
    def progress(self):
        raise NotImplementedError

    def get_update_interval(self):
        return (self.update_interval  * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return True # TODO only if not dead

class BerryBush(StaticEntity):
    def __init__(self, engine, x, y):
        super().__init__(engine, x, y, Stats.map["berry-bush"]["update-interval"]) # ms
        self.bg_color = colors.dark_green()
        self.num_berries = randrange(Stats.map["berry-bush"]["spawn-min-berries"], Stats.map["berry-bush"]["spawn-max-berries"], 1)

    def progress(self):
        self.grow_berry()
    
    def pick_berry(self):
        if self.num_berries > 0:
            self.num_berries -= 1
            return Berry()
        else:
            return None

    def grow_berry(self):
        self.num_berries += Stats.map["berry-bush"]["grow-berries"]

class Berry():
    def __init__(self):
        pass