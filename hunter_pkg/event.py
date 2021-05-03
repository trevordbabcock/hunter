from time import time
from typing import Callable

from hunter_pkg import stats

from hunter_pkg.helpers import generic as gen


class Event:
    def __init__(self, entity, time):
        self.entity = entity
        self.time = time

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


class EntropyEvent(Event):
    def __init__(self, entity):
        update_interval = entity.update_interval if gen.has_member(entity, "update_interval") else stats.Stats.map()["settings"]["default-update-interval"]
        super().__init__(entity, entity.engine.game_time + update_interval)
        
    def process(self):
        self.entity.progress()


class AIEvent(Event):
    def __init__(self, entity, time):
        super().__init__(entity, time)

    def process(self):
        return self.entity.ai.perform()
