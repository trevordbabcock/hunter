import numpy.random as nprand
from typing import Tuple

from hunter_pkg.helpers import math
from hunter_pkg.helpers import rng

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import status_effects as stfx


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Entity:
    def __init__(self, engine, x: int, y: int, char: str, color: Tuple[int, int, int], bg_color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.bg_color = bg_color
        self.engine = engine

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy


class IntelligentEntity(Entity):
    def __init__(self, engine, x: int, y: int, char: str, color: Tuple[int, int, int], bg_color: Tuple[int, int, int], ai, update_interval_range: list, update_interval_step: float):
        super().__init__(engine, x, y, char, color, bg_color)
        self.alive = True
        self.ai = ai
        self.update_interval_start = update_interval_range[0]
        self.update_interval_stop = update_interval_range[1]
        self.update_interval_step = update_interval_step
        self.status_effects = []
        self.min_health, self.max_health = [0, 0]
        self.min_hunger, self.max_hunger = [0, 0]
        self.min_energy, self.max_energy = [0, 0]

    def get_update_interval(self):
        return (rng.range(self.update_interval_start, self.update_interval_stop, self.update_interval_step) * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return self.alive

    def eat(self, entity):
        raise NotImplementedError

    def die(self):
        raise NotImplementedError

    @property
    def curr_health(self):
        return self.__curr_health
    
    @curr_health.setter
    def curr_health(self, curr_health):
        self.__curr_health = math.clamp(curr_health, self.min_health, self.max_health)

        if self.alive and self.curr_health <= 0:
            self.die()

    @property
    def curr_hunger(self):
        return self.__curr_hunger
    
    @curr_hunger.setter
    def curr_hunger(self, curr_hunger):
        self.__curr_hunger = math.clamp(curr_hunger, self.min_hunger, self.max_hunger)

        if self.curr_hunger <= 0:
            self.apply_se_once(stfx.Starvation)
        elif self.curr_hunger > 0:
            self.remove_se(stfx.Starvation)

    @property
    def curr_energy(self):
        return self.__curr_energy
    
    @curr_energy.setter
    def curr_energy(self, curr_energy):
        self.__curr_energy = math.clamp(curr_energy, self.min_energy, self.max_energy)

        if self.curr_energy <= 0:
            self.apply_se_once(stfx.SleepDeprivation)
        elif self.curr_energy > 0:
            self.remove_se(stfx.SleepDeprivation)

    def apply_se(self, status_effect_class):
        """
        Apply status effect
        """
        self.status_effects.append(status_effect_class())

    def apply_se_once(self, status_effect_class):
        """
        Only apply status effect if not already affected
        """
        if not self.is_affected_by(status_effect_class):
            self.apply_se(status_effect_class)
    
    def remove_se(self, status_effect_class):
        for e in self.status_effects:
            if e != None:
                if isinstance(e, status_effect_class):
                    self.status_effects.remove(e)

    def is_affected_by(self, status_effect_class):
        return any(isinstance(se, status_effect_class) for se in self.status_effects)


class StaticEntity():
    def __init__(self, engine, x, y, update_interval):
        self.engine = engine
        self.x = x
        self.y = y
        self.update_interval = update_interval
    
    def progress(self):
        raise NotImplementedError

    def get_update_interval(self):
        return (self.update_interval  * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return True # TODO only if not dead