from random import randrange
from typing import Tuple

import ai
import colors

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

class Hunter(IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "H", colors.white(), colors.light_gray(), ai.HunterAI(self), [1000, 1500], 100) # milliseconds
        self.vision_distance = 7

    # def get_visible_map(self):
    #     visible_map = [None] * (self.vision_distance * 2)
    #     y_range_start = self.y - self.vision_distance
    #     y_range_end = self.y + self.vision_distance
    #     x_range_start = self.x - self.vision_distance
    #     x_range_end = self.x + self.vision_distance
    #     tmp_map = self.engine.game_map.tiles[y_range_start:y_range_end]

    #     for y in range(len(tmp_map)):
    #         visible_map[y] = tmp_map[y][x_range_start:x_range_end]

    #     return visible_map
    
    def can_see(self, entity):
        vd = self.vision_distance
        visible_x = (self.x - vd) < entity.x and entity.x < (self.x + vd)
        visible_y = (self.y - vd) < entity.y and entity.y < (self.y + vd)

        return visible_x and visible_y

class Rabbit(IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "R", colors.white(), colors.light_gray(), ai.RabbitAI(self), [1000, 3000], 100) # milliseconds
