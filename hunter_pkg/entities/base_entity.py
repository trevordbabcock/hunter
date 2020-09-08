import numpy.random as nprand
from typing import Tuple

from hunter_pkg.helpers import rng

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg.stats import Stats


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Entity:
    def __init__(self, engine, x: int, y: int, char: str, color: Tuple[int, int, int], bg_color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.bg_color = bg_color
        self.engine = engine

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy


class IntelligentEntity(Entity):
    def __init__(self, engine, x: int, y: int, char: str, color: Tuple[int, int, int], bg_color: Tuple[int, int, int], ai, update_interval_range: list, update_interval_step: float):
        super().__init__(engine, x, y, char, color, bg_color)
        self.alive = True
        self.ai = ai
        self.update_interval_start = update_interval_range[0]
        self.update_interval_stop = update_interval_range[1]
        self.update_interval_step = update_interval_step

    def get_update_interval(self):
        return (rng.range(self.update_interval_start, self.update_interval_stop, self.update_interval_step) * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return self.alive

    def eat(self, entity):
        pass


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