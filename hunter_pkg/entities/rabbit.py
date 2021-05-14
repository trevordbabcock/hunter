from collections import deque

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import entity_actions as enta

from hunter_pkg.helpers.coord import Coord
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

class Rabbit(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "R", colors.white(), colors.light_gray(), RabbitAI(self), "Rabbit")
        self.alive = True
        self.asleep = False
        self.max_health = stats.Stats.map()["rabbit"]["max-health"]
        self.curr_health = stats.Stats.map()["rabbit"]["starting-health"]
        self.nutritional_value = stats.Stats.map()["rabbit"]["nutritional-value"]
        self.vision_distance = stats.Stats.map()["rabbit"]["vision-distance"]
        self.recent_actions = []
        self.burrow = None
        self.hidden = False

    def is_hungry(self):
        return rng.rand() < stats.Stats.map()["rabbit"]["hunger-chance"]

    def is_tired(self):
        return self.engine.time_of_day == tod.MORNING or self.engine.time_of_day == tod.AFTERNOON
    

    def die(self):
        flog.debug("a rabbit died")
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

    def hide(self):
        self.hidden = True
        self.engine.game_map.redraw_tile(self.x, self.y)

    def unhide(self):
        self.hidden = False
        self.engine.game_map.redraw_tile(self.x, self.y)

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

        if self.burrow != None:
            info.append(f"Brrw: ({self.burrow.x},{self.burrow.y})")

        return info


class RabbitAI():
    def __init__(self, rabbit):
        self.rabbit = rabbit
        self.action_queue = deque()
        self.default_cooldown = stats.Stats.map()["rabbit"]["action-cooldowns"]["default"]

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

        # if afraid
        #   if burrow is close
        #     go to burrow
        #   else
        #     run away
        
        if self.rabbit.is_hungry():
            flog.debug("rabbit is hungry")
            self.action_queue.append(SearchAreaAction(self.rabbit, (trrn.Grass, trrn.Forest)))
        elif self.rabbit.is_tired():
            flog.debug("rabbit is tired")
            self.rabbit.recent_actions.append("Rabbit is going to its burrow.")
            self.rabbit.ai.action_queue.append(MovementAction(self.rabbit, self.rabbit.burrow.coord(), None, SleepAction(self.rabbit)))
        else:
            self.roam()
        
        return actions

    def roam(self):
        flog.debug("rabbit is roaming")
        dist = stats.Stats.map()["rabbit"]["roam-distance"]
        unclamped_x = rng.range_int(self.rabbit.x - dist, self.rabbit.x + dist + 1)
        unclamped_y = rng.range_int(self.rabbit.y - dist, self.rabbit.y + dist + 1)

        self.rabbit.ai.action_queue.append(MovementAction(self.rabbit, self.rabbit.engine.game_map.clamp_coord(unclamped_x, unclamped_y)))


class MovementAction():
    def __init__(self, rabbit, dest, path=None, final_action=None):
        self.rabbit = rabbit
        self.dest = dest
        self.path = path
        self.final_action = final_action
        self.cooldown = stats.Stats.map()["rabbit"]["action-cooldowns"]["movement-action"]
    
    def perform(self):
        if self.rabbit.alive:
            if not self.path:
                self.path = deque(pf.get_path(self.rabbit.engine.game_map.path_map, self.rabbit.coord(), self.dest))

            if len(self.path) > 0:
                dest = self.path.popleft()
                self.rabbit.move_to(dest)

                if len(self.path) > 0:
                    self.rabbit.ai.action_queue.append(MovementAction(self.rabbit, dest, self.path, self.final_action))
                elif self.final_action:
                    self.rabbit.ai.action_queue.append(self.final_action)
            elif self.final_action:
                self.rabbit.ai.action_queue.append(self.final_action)


class SearchAreaAction(enta.SearchAreaActionBase):
    def __init__(self, rabbit, search_for_classes):
        self.rabbit = rabbit
        self.search_radius = self.rabbit.vision_distance[self.rabbit.engine.time_of_day]
        self.search_for_classes = [c.__name__ for c in search_for_classes]
    
    def perform(self):
        search_area = self.get_search_area(self.rabbit, self.search_radius, vsmap.square)
        found_terrain = self.find_terrain(search_area, self.search_for_classes)

        if len(found_terrain) > 0:
            dest = rng.pick_rand(found_terrain)
            self.rabbit.ai.action_queue.append(MovementAction(self.rabbit, Coord(dest.x, dest.y), None, GrazeAction(self.rabbit)))
        else:
            self.rabbit.ai.roam()


class GrazeAction():
    def __init__(self, rabbit):
        self.rabbit = rabbit
        self.cooldown = stats.Stats.map()["rabbit"]["action-cooldowns"]["graze-action"]

    def perform(self):
        flog.debug("rabbit is grazing")
        self.rabbit.recent_actions.append("Rabbit is grazing.")


class SleepAction():
    def __init__(self, rabbit):
        self.rabbit = rabbit

    def perform(self):
        sleep_in = rng.rand() < stats.Stats.map()["rabbit"]["sleep-in-chance"]

        if self.rabbit.is_tired() or sleep_in:
            flog.debug("rabbit is sleeping")
            self.rabbit.recent_actions.append("Rabbit is asleep in its burrow.")
            self.rabbit.asleep = True
            self.rabbit.hide()
            self.rabbit.ai.action_queue.append(SleepAction(self.rabbit))
        else:
            flog.debug("rabbit woke up")
            self.rabbit.recent_actions.append("Rabbit woke up and is leaving its burrow.")
            self.rabbit.asleep = False
            self.rabbit.unhide()
            
        
class Burrow():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = ord("B")
        self.fg_color = colors.white()
        self.bg_color = colors.light_gray()
        self.occupied = False

    def coord(self):
        return Coord(self.x, self.y)