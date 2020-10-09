import enum

from hunter_pkg import colors
from hunter_pkg import stats

class Camp:
    def __init__(self, engine, x, y):
        self.engine = engine
        self.x = x
        self.y = y
        self.char = ord("C")
        self.fg_color = colors.white()
        self.bg_color = colors.light_gray()
        self.components = [FirePit(engine), Bedroll(), WoodPile()]


class CampComponent():
    def name(self):
        return self.__class__.__name__


class FirePit(CampComponent):
    def __init__(self, engine):
        self.engine = engine
        self.update_interval = stats.Stats.map()["fire-pit"]["duration"]
        self.state = None
    
    def ignite(self):
        self.state = FireState.Ignited
        self.engine.event_queue.append()

    def extinguish(self):
        self.state = FireState.Extinguished
    
    def progress(self):
        self.extinguish


class FireState(enum.Enum):
    Extinguished = 1
    Ignited = 2


class Bedroll(CampComponent):
    def __init__(self):
        self.occupied = False
        self.comfort = stats.Stats.map()["bedroll"]["comfort"]
        self.wake_chance = stats.Stats.map()["bedroll"]["wake-chance"]


class WoodPile(CampComponent):
    def __init__(self):
        self.fuel = []
