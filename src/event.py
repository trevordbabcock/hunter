from time import time
from typing import Callable

from entity import IntelligentEntity
from game_map import GameMap


class Event:
    def __init__(self, entity: IntelligentEntity):
        self.entity = entity
        self.time = time() + entity.get_update_interval()

    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time

    def process(self):
        self.entity.ai.perform()