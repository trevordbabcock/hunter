import enum

from hunter_pkg.entities import maps

from hunter_pkg.helpers.coord import Coord
from hunter_pkg.helpers import math
from hunter_pkg.helpers import rng

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import stats
from hunter_pkg import status_effects as stfx


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Entity:
    def __init__(self, engine, x, y, char, color, bg_color, name="<Unknown>", article="<Unknown>"):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.base_color = color
        self.bg_color = bg_color
        self.base_bg_color = bg_color
        self.engine = engine
        self.selected = False
        self.name = name
        self.entity_name = name
        self.entity_article = article

    def move(self, dx, dy):
        dest_x = self.x + dx
        dest_y = self.y + dy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not self.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return

        self.engine.game_map.tiles[self.y][self.x].remove_entities([self])
        self.engine.game_map.tiles[dest_y][dest_x].add_entities([self])

        self.x += dx
        self.y += dy

    def move_to(self, dest):
        x_adjacent = abs(self.x - dest.x) <= 1
        y_adjacent = abs(self.y - dest.y) <= 1

        if not (x_adjacent and y_adjacent):
            return
        if not self.engine.game_map.in_bounds(dest.x, dest.y):
            return
        if not self.engine.game_map.tiles[dest.y][dest.x].terrain.walkable:
            return

        self.engine.game_map.tiles[self.y][self.x].remove_entities([self])
        self.engine.game_map.tiles[dest.y][dest.x].add_entities([self])

        self.x = dest.x
        self.y = dest.y

    def coord(self):
        return Coord(self.x, self.y)

    def select(self):
        self.selected = True
        self.color = colors.dark_gray()
        self.bg_color = colors.yellow()

    def deselect(self):
        self.selected = False
        self.color = self.base_color
        self.bg_color = self.base_bg_color


class IntelligentEntity(Entity):
    def __init__(self, engine, x, y, char, color, bg_color, ai, name, article="a"):
        super().__init__(engine, x, y, char, color, bg_color, name, article)
        self.alive = True
        self.ai = ai
        self.status_effects = []
        self.min_health, self.max_health = [0, 0]
        self.min_hunger, self.max_hunger = [0, 0]
        self.min_energy, self.max_energy = [0, 0]
        self.recent_actions = []
        self.max_recent_actions = stats.Stats.map()["entity"]["max-recent-actions"]
        self.min_recent_actions = stats.Stats.map()["entity"]["min-recent-actions"]
        self.attacker = None

    def requeue(self):
        return self.alive

    def eat(self, entity):
        raise NotImplementedError

    def harm(self, damage, attacker):
        self.curr_health -= damage
        self.attacker = attacker

    def heal(self, healing):
        self.curr_health += healing

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

    def is_target_in_range(self, target):
        return self.x == target.x and self.y == target.y

    def try_flush_recent_actions(self):
        if len(self.recent_actions) > self.max_recent_actions:
            self.recent_actions = self.recent_actions[self.max_recent_actions-self.min_recent_actions:]
            flog.debug("flushed entity recent_actions")


class StaticEntity():
    def __init__(self, engine, x, y, update_interval, name="<Unknown>"):
        self.engine = engine
        self.x = x
        self.y = y
        self.update_interval = update_interval
        self.name = name
        self.entity_name = name
    
    def progress(self):
        raise NotImplementedError

    def get_update_interval(self):
        return (self.update_interval  * 0.001) * (1.0/self.engine.game_speed)

    def requeue(self):
        return True # TODO only if not dead

    def coord(self):
        return Coord(self.x, self.y)

# for entities that can be hidden using the entity overview panel
class Hideable():
    def is_visible(self):
        if self.name in maps.entity_overview_map:
            return self.engine.settings["entity-visibility"][maps.entity_overview_map[self.name]]
