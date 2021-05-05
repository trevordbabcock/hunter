from collections import deque

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import entity_actions as enta

from hunter_pkg.helpers import direction
from hunter_pkg.helpers import generic as gen
from hunter_pkg.helpers import math
from hunter_pkg.helpers import rng
from hunter_pkg.helpers import time_of_day as tod

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder as pf
from hunter_pkg import stats
from hunter_pkg import terrain as trrn
from hunter_pkg import vision_map as vsmap


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Deer(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "D", colors.white(), colors.light_gray(), DeerAI(self), "Deer")
        self.alive = True
        self.asleep = False
        self.max_health = stats.Stats.map()["deer"]["max-health"]
        self.curr_health = stats.Stats.map()["deer"]["starting-health"]
        self.nutritional_value = stats.Stats.map()["deer"]["nutritional-value"]
        self.vision_distance = stats.Stats.map()["deer"]["vision-distance"]
        self.recent_actions = []
        self.hidden = False

    def is_hungry(self):
        return rng.rand() < stats.Stats.map()["deer"]["hunger-chance"]

    def is_tired(self):
        return self.engine.time_of_day == tod.NIGHT
    

    def die(self):
        flog.debug("a deer died")
        self.alive = False
        self.char = "x"

    def consume(self):
        try:
            self.engine.game_map.tiles[self.y][self.x].entities.remove(self)
        except ValueError:
            return False

        self.engine.intelligent_entities.remove(self)
        self.engine.game_map.redraw_tile(self.x, self.y)

        return True

    def progress(self):
        self.try_flush_recent_actions()

    def selection_info(self):
        info = [self.name]

        if not self.alive:
            info.append("*Dead*")
        
        info.extend([
            f"Coord: ({self.x},{self.y})",
            f"Hlth: {self.curr_health}/{self.max_health}",
        ])

        return info


class DeerAI():
    def __init__(self, deer):
        self.deer = deer
        self.action_queue = deque()
        self.default_cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["default"]

    def perform(self):
        cooldown = self.default_cooldown

        if len(self.action_queue) > 0:
            action = self.action_queue.popleft()
            cooldown = action.cooldown if gen.has_member(action, 'cooldown') else self.default_cooldown 
            action.perform()
        else:
            actions = self.decide_what_to_do()
            for a in actions:
                self.action_queue.append(a)
        
        return cooldown

    def decide_what_to_do(self):
        actions = []
        
        if self.deer.is_hungry():
            flog.debug("deer is hungry")
            self.action_queue.append(SearchAreaAction(self.deer, (trrn.Grass, trrn.Forest)))
        elif self.deer.is_tired():
            flog.debug("deer is tired")
            self.deer.recent_actions.append("Deer is laying down.")
            self.deer.ai.action_queue.append(SleepAction(self.deer))
        else:
            self.roam()
        
        return actions

    def roam(self):
        flog.debug("deer is roaming")
        dist = stats.Stats.map()["deer"]["roam-distance"]
        max_x = self.deer.engine.game_map.width - 1
        max_y = self.deer.engine.game_map.height - 1
        dest_x = math.clamp(rng.range_int(self.deer.x - dist, self.deer.x + dist + 1), 0, max_x)
        dest_y = math.clamp(rng.range_int(self.deer.y - dist, self.deer.y + dist + 1), 0, max_y)
        dest = self.deer.engine.game_map.tiles[dest_y][dest_x]

        for action in pf.path_to_dest(self.deer, [dest.x, dest.y], MovementAction):
            self.deer.ai.action_queue.append(action)


class MovementAction():
    def __init__(self, deer, dy, dx):
        self.deer = deer
        self.dx = dx
        self.dy = dy
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["movement-action"]
    
    def perform(self):
        if self.deer.alive:
            self.deer.move(self.dx, self.dy)


class SearchAreaAction(enta.SearchAreaActionBase):
    def __init__(self, deer, search_for_classes):
        self.deer = deer
        self.search_radius = self.deer.vision_distance[self.deer.engine.time_of_day]
        self.search_for_classes = [c.__name__ for c in search_for_classes]
    
    def perform(self):
        search_area = self.get_search_area(self.deer, self.search_radius, vsmap.circle)
        found_terrain = self.find_terrain(search_area, self.search_for_classes)

        if len(found_terrain) > 0:
            dest = rng.pick_rand(found_terrain)

            for action in pf.path_to_dest(self.deer, [dest.x, dest.y], MovementAction):
                self.deer.ai.action_queue.append(action)
            
            self.deer.ai.action_queue.append(GrazeAction(self.deer))
        else:
            self.deer.ai.roam()


class GrazeAction():
    def __init__(self, deer):
        self.deer = deer
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["graze-action"]

    def perform(self):
        flog.debug("deer is grazing")
        self.deer.recent_actions.append("Deer is grazing.")


class SleepAction():
    def __init__(self, deer):
        self.deer = deer

    def perform(self):
        sleep_in = rng.rand() < stats.Stats.map()["deer"]["sleep-in-chance"]

        if self.deer.is_tired():
            flog.debug("deer is sleeping")
            self.deer.recent_actions.append("Deer is asleep.")
            self.deer.asleep = True
            self.deer.ai.action_queue.append(SleepAction(self.deer))
        else:
            flog.debug("deer woke up")
            self.deer.recent_actions.append("Deer woke up.")
            self.deer.asleep = False
