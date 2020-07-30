from time import time
from typing import Callable

from entity import IntelligentEntity


class Event:
    def __init__(self, entity: IntelligentEntity):
        self.entity = entity
        self.time = time() + entity.update_interval

    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time

    def process(self):
        self.entity.ai.perform()