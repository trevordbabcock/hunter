from typing import Tuple

import ai
import colors

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int], bg_color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.bg_color = bg_color

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

class IntelligentEntity(Entity):
    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int], bg_color: Tuple[int, int, int], ai, update_interval: float):
        super().__init__(x, y, char, color, bg_color)
        self.update_interval = update_interval
        self.ai = ai

    def requeue(self):
        return True # TODO only if not dead

class Hunter(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "H", colors.white(), colors.light_gray())

class Rabbit(IntelligentEntity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "R", colors.white(), colors.light_gray(), ai.RabbitAI(self), 1)
