import numpy.random as nprand
from random import randrange
from typing import Tuple

from hunter_pkg.ai import hunter_ai
from hunter_pkg.ai import rabbit_ai
from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg.stats import Stats


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, engine, x: int, y: int, char: str, color: Tuple[int, int, int], bg_color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.bg_color = bg_color
        self.engine = engine

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
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
        return (randrange(self.update_interval_start, self.update_interval_stop, self.update_interval_step) * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return self.alive

    def eat(self, entity):
        pass

class Hunter(IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "H", colors.white(), colors.light_gray(), hunter_ai.HunterAI(self), [Stats.map()["hunter"]["update-interval-start"], Stats.map()["hunter"]["update-interval-end"]], Stats.map()["hunter"]["update-interval-step"])
        self.alive = True
        self.max_hunger = Stats.map()["hunter"]["max-hunger"]
        self.max_health = Stats.map()["hunter"]["max-health"]
        self.max_energy = Stats.map()["hunter"]["max-energy"]
        self.curr_hunger = Stats.map()["hunter"]["starting-hunger"]
        self.curr_health = Stats.map()["hunter"]["starting-health"]
        self.curr_energy = Stats.map()["hunter"]["starting-energy"]
        self.vision_distance = Stats.map()["hunter"]["vision-distance"]
    
    def can_see(self, entity):
        vd = self.vision_distance
        visible_x = (self.x - vd) < entity.x and entity.x < (self.x + vd)
        visible_y = (self.y - vd) < entity.y and entity.y < (self.y + vd)

        return visible_x and visible_y

    def eat(self, entity):
        flog.debug("hunter ate something")
        self.curr_hunger += entity.nutritional_value

    def is_hungry(self):
        return self.curr_hunger < Stats.map()["hunter"]["hunger-threshold-low"]

    def is_still_hungry(self):
        return self.curr_hunger < Stats.map()["hunter"]["hunger-threshold-high"]

    def die(self):
        flog.debug("omg hunter died")
        self.alive = False
        self.char = "X"

    def progress(self):
        if self.curr_hunger == 0:
            self.die()
        else:
            self.curr_hunger -= Stats.map()["hunter"]["hunger-loss"]

class Rabbit(IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "R", colors.white(), colors.light_gray(), rabbit_ai.RabbitAI(self), [Stats.map()["rabbit"]["update-interval-start"], Stats.map()["rabbit"]["update-interval-end"]], Stats.map()["rabbit"]["update-interval-step"])
    
    def progress(self):
        pass
