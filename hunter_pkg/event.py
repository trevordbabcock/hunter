from time import time
from typing import Callable


class Event:
    def __init__(self, entity):
        self.entity = entity
        self.time = entity.engine.game_time + entity.get_update_interval()

    def __lt__(self, other):
        if self.time == other.time:
            # Not really sure this is necessary
            return f"{self.entity.x}{self.entity.y}" < f"{other.entity.x}{other.entity.y}"
        else:
            return self.time < other.time
    
    def __gt__(self, other):
        if self.time == other.time:
            # Not really sure this is necessary
            return f"{self.entity.x}{self.entity.y}" > f"{other.entity.x}{other.entity.y}"
        else:
            return self.time > other.time

    def process(self):
        if hasattr(self.entity, "ai"):
            self.entity.ai.perform()

        self.entity.progress()