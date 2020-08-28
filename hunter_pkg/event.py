from time import time
from typing import Callable


class Event:
    def __init__(self, entity):
        self.entity = entity
        self.time = time() + entity.get_update_interval()

    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time

    def process(self):
        if hasattr(self.entity, "ai"):
            self.entity.ai.perform()

        self.entity.progress()