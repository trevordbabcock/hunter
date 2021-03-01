from collections import deque

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import entity_actions as enta

from hunter_pkg.helpers import direction
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
        super().__init__(engine, x, y, "R", colors.white(), colors.light_gray(), RabbitAI(self), [stats.Stats.map()["rabbit"]["update-interval-start"], stats.Stats.map()["rabbit"]["update-interval-end"]], stats.Stats.map()["rabbit"]["update-interval-step"])
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
        pass


class RabbitAI():
    def __init__(self, rabbit):
        self.rabbit = rabbit
        self.action_queue = deque()

    def perform(self):
        if len(self.action_queue) > 0:
            action = self.action_queue.popleft()
            action.perform()
        else:
            actions = self.decide_what_to_do()
            for a in actions:
                self.action_queue.append(a)

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
            flog.debug("rabbit is sleepy")
            for action in pf.path_to_dest(self.rabbit, [self.rabbit.burrow.x, self.rabbit.burrow.y], MovementAction):
                self.rabbit.ai.action_queue.append(action)

            self.rabbit.ai.action_queue.append(SleepAction(self.rabbit))
        else:
            self.roam()
        
        return actions

    def roam(self):
        flog.debug("rabbit is roaming")
        dist = stats.Stats.map()["rabbit"]["roam-distance"]
        max_x = self.rabbit.engine.game_map.width - 1
        max_y = self.rabbit.engine.game_map.height - 1
        dest_x = math.clamp(rng.range_int(self.rabbit.x - dist, self.rabbit.x + dist + 1), 0, max_x)
        dest_y = math.clamp(rng.range_int(self.rabbit.y - dist, self.rabbit.y + dist + 1), 0, max_y)
        dest = self.rabbit.engine.game_map.tiles[dest_y][dest_x]

        for action in pf.path_to_dest(self.rabbit, [dest.x, dest.y], MovementAction):
            self.rabbit.ai.action_queue.append(action)


class MovementAction():
    def __init__(self, rabbit, dy, dx):
        self.rabbit = rabbit
        self.dx = dx
        self.dy = dy
    
    def perform(self):
        if self.rabbit.alive:
            self.rabbit.move(self.dx, self.dy)


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

            for action in pf.path_to_dest(self.rabbit, [dest.x, dest.y], MovementAction):
                self.rabbit.ai.action_queue.append(action)
            
            self.rabbit.ai.action_queue.append(GrazeAction(self.rabbit))
        else:
            self.rabbit.ai.roam()


class GrazeAction():
    def __init__(self, rabbit):
        self.rabbit = rabbit

    def perform(self):
        flog.debug("rabbit is grazing")


class SleepAction():
    def __init__(self, rabbit):
        self.rabbit = rabbit

    def perform(self):
        sleep_in = rng.rand() < stats.Stats.map()["rabbit"]["sleep-in-chance"]

        if self.rabbit.is_tired() or sleep_in:
            flog.debug("rabbit is sleeping")
            self.rabbit.asleep = True
            self.rabbit.hide()
            self.rabbit.ai.action_queue.append(SleepAction(self.rabbit))
        else:
            flog.debug("rabbit woke up")
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
