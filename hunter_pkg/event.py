from time import time
from typing import Callable

from hunter_pkg import entity as ent


class Event:
    def __init__(self, entity: ent.IntelligentEntity):
        self.entity = entity
        self.time = time() + entity.get_update_interval()

    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time

    def process(self):
        if hasattr(self.entity, "ai"):
            self.entity.ai.perform()
        else:
            self.entity.progress()