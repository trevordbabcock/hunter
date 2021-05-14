from collections import deque

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import entity_actions as enta
from hunter_pkg.entities import hunter as htr
from hunter_pkg.entities import rabbit as rbt

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

class Wolf(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "W", colors.white(), colors.brown(), WolfAI(self), "Wolf")
        self.alive = True
        self.asleep = False
        self.max_health = stats.Stats.map()["wolf"]["max-health"]
        self.curr_health = stats.Stats.map()["wolf"]["starting-health"]
        self.vision_distance = stats.Stats.map()["wolf"]["vision-distance"]
        self.attk_dmg = stats.Stats.map()["wolf"]["attack-damage"]
        self.recent_actions = []
        self.hidden = False

    def is_hungry(self):
        return True

    def die(self):
        flog.debug("a wolf died")
        self.alive = False
        self.char = "x"
    
    def selection_info(self):
        info = [self.name]

        if not self.alive:
            info.append("*Dead*")
        
        info.extend([
            f"Coord: ({self.x},{self.y})",
            f"Hlth: {self.curr_health}/{self.max_health}",
        ])

        return info

    def progress(self):
        self.try_flush_recent_actions()


class WolfAI():
    def __init__(self, wolf):
        self.wolf = wolf
        self.action_queue = deque()
        self.default_cooldown = stats.Stats.map()["wolf"]["action-cooldowns"]["default"]

    def perform(self):
        cooldown = self.default_cooldown

        if self.wolf.alive:
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
        
        if self.wolf.is_hungry():
            flog.debug("wolf is hungry")
            self.action_queue.append(SearchAreaAction(self.wolf, [rbt.Rabbit, htr.Hunter]))
        else:
            self.roam()
        
        return actions

    def roam(self):
        flog.debug("wolf is roaming")
        dist = stats.Stats.map()["wolf"]["roam-distance"]
        unclamped_x = rng.range_int(self.wolf.x - dist, self.wolf.x + dist + 1)
        unclamped_y = rng.range_int(self.wolf.y - dist, self.wolf.y + dist + 1)

        self.wolf.ai.action_queue.append(MovementAction(self.wolf, self.wolf.engine.game_map.clamp_coord(unclamped_x, unclamped_y)))


class MovementAction():
    def __init__(self, wolf, dest, path=None, final_action=None):
        self.wolf = wolf
        self.dest = dest
        self.path = path
        self.final_action = final_action
        self.cooldown = stats.Stats.map()["wolf"]["action-cooldowns"]["movement-action"]
    
    def perform(self):
        if self.wolf.alive:
            if not self.path:
                self.path = deque(pf.get_path(self.wolf.engine.game_map.path_map, self.wolf.coord(), self.dest))

            if len(self.path) > 0:
                dest = self.path.popleft()
                self.wolf.move_to(dest)

                if len(self.path) > 0:
                    self.wolf.ai.action_queue.append(MovementAction(self.wolf, dest, self.path, self.final_action))
                elif self.final_action:
                    self.wolf.ai.action_queue.append(self.final_action)
            elif self.final_action:
                self.wolf.ai.action_queue.append(self.final_action)


class SearchAreaAction(enta.SearchAreaActionBase):
    def __init__(self, wolf, search_for_classes):
        self.wolf = wolf
        self.search_radius = self.wolf.vision_distance[self.wolf.engine.time_of_day]
        self.search_for_classes = [c.__name__ for c in search_for_classes]
        self.cooldown = stats.Stats.map()["wolf"]["action-cooldowns"]["search-area-action"]
    
    def perform(self):
        flog.debug("wolf is roaming")
        self.wolf.recent_actions.append(f"Wolf is roaming.")
        search_area = self.get_search_area(self.wolf, self.search_radius, vsmap.circle)
        found_entities = self.find_entities(search_area, self.search_for_classes)
        living_entities = [entity for entity in found_entities if entity.alive]

        if len(living_entities) > 0:
            target = rng.pick_rand(living_entities) # TODO should find nearest
            self.wolf.ai.action_queue.append(PursueAction(self.wolf, target))
        else:
            self.wolf.ai.roam()


class PursueAction():
    def __init__(self, wolf, target):
        self.wolf = wolf
        self.target = target
        self.cooldown = stats.Stats.map()["wolf"]["action-cooldowns"]["pursue-action"]

    def perform(self):
        flog.debug("wolf is pursuing")
        self.wolf.recent_actions.append(f"Wolf is pursuing {self.target.entity_article} {self.target.entity_name.lower()}.")

        if self.wolf.alive:
            dest = pf.path_to_target(self.wolf, self.target)
            self.wolf.move(dest.x, dest.y)

            if self.wolf.is_target_in_range(self.target):
                self.wolf.ai.action_queue.append(AttackAction(self.wolf, self.target))
            else:
                self.wolf.ai.action_queue.append(PursueAction(self.wolf, self.target))


class AttackAction():
    def __init__(self, wolf, target):
        self.wolf = wolf
        self.target = target

    def perform(self):
        if not self.target.hidden:
            flog.debug("wolf is attacking")
            self.wolf.recent_actions.append(f"Wolf is attacking {self.target.entity_article} {self.target.entity_name.lower()}.")
            self.target.harm(self.wolf.attk_dmg)

            if not self.target.alive:
                if isinstance(self.target, rbt.Rabbit):
                    self.wolf.ai.action_queue.append(EatRabbitAction(self.wolf, self.target))
        else:
            flog.debug("wolf can't attack hidden target")


class EatRabbitAction():
    def __init__(self, wolf, rabbit):
        self.wolf = wolf
        self.rabbit = rabbit

    def perform(self):
        flog.debug("wolf is eating a rabbit")
        self.wolf.recent_actions.append(f"Wolf is eating a rabbit.")
        self.rabbit.consume()
            