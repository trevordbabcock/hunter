import numpy.random as nprand
from random import randrange
from typing import Tuple

import ai
import colors
from stats import Stats

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
        self.update_interval_start = update_interval_range[0]
        self.update_interval_stop = update_interval_range[1]
        self.update_interval_step = update_interval_step
        self.ai = ai

    def get_update_interval(self):
        return (randrange(self.update_interval_start, self.update_interval_stop, self.update_interval_step) * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return True # TODO only if not dead

    def eat(self, entity):
        pass

class Hunter(IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "H", colors.white(), colors.light_gray(), ai.HunterAI(self), [Stats.map["hunter"]["update-interval-start"], Stats.map["hunter"]["update-interval-end"]], Stats.map["hunter"]["update-interval-step"])
        self.vision_distance = Stats.map["hunter"]["vision-distance"]
    
    def can_see(self, entity):
        vd = self.vision_distance
        visible_x = (self.x - vd) < entity.x and entity.x < (self.x + vd)
        visible_y = (self.y - vd) < entity.y and entity.y < (self.y + vd)

        return visible_x and visible_y

    def eat(self, entity):
        print("HUNTER ATE SOMETHING")

    def is_hungry(self):
        return nprand.rand() < Stats.map["hunter"]["is-hungry"]

class Rabbit(IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "R", colors.white(), colors.light_gray(), ai.RabbitAI(self), [Stats.map["rabbit"]["update-interval-start"], Stats.map["rabbit"]["update-interval-end"]], Stats.map["rabbit"]["update-interval-step"])
