from random import randrange
from typing import Tuple

import ai
import colors
import entity


class StaticEntity():
    def __init__(self, engine, update_interval):
        self.engine = engine
        self.update_interval = update_interval
    
    def progress(self):
        raise NotImplementedError

    def get_update_interval(self):
        return (self.update_interval  * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return True # TODO only if not dead

class BerryBush(StaticEntity):
    def __init__(self, engine):
        super().__init__(engine, 25000) # ms
        self.bg_color = colors.dark_green()
        self.num_berries = randrange(12, 25, 1)

    def progress(self):
        self.grow_berry()
    
    def pick_berry(self):
        if self.num_berries > 0:
            self.num_berries -= 1
            return Berry()
        else:
            return None

    def grow_berry(self):
        self.num_berries += 1

class Berry():
    def __init__(self):
        pass