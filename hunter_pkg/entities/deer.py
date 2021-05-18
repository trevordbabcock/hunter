from collections import deque

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import entity_actions as enta
from hunter_pkg.entities import hunter as htr
from hunter_pkg.entities import wolf as wlf

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

class Deer(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, self.char, colors.white(), colors.light_gray(), self.ai, "Deer")
        self.alive = True
        self.asleep = False
        self.max_health = stats.Stats.map()["deer"]["max-health"]
        self.curr_health = stats.Stats.map()["deer"]["starting-health"]
        self.nutritional_value = stats.Stats.map()["deer"]["nutritional-value"]
        self.vision_distance = stats.Stats.map()["deer"]["vision-distance"]
        self.roam_distance = stats.Stats.map()["deer"]["roam-distance"]
        self.attack_damage = stats.Stats.map()["deer"]["attack-damage"]
        self.attacked = None
        self.recent_actions = []
        self.hidden = False

    def is_hungry(self):
        return rng.rand() < stats.Stats.map()["deer"]["hunger-chance"]

    def is_tired(self):
        return self.engine.time_of_day == tod.NIGHT

    def harm(self, damage, attacker):
        super().harm(damage, attacker)
        self.recent_actions.append(f"{self.entity_name} was attacked!")

    def die(self):
        flog.debug("a deer died")
        self.alive = False
        self.char = "x"
    
    def is_attacked(self):
        return self.attacker != None
    
    def should_wake_up(self):
        return self.is_attacked()

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


class Buck(Deer):
    def __init__(self, engine, x, y):
        self.char = "D"
        self.ai = BuckAI(self)
        super().__init__(engine, x, y)
        self.herd = []
        self.entity_name = "Buck"
        self.entity_article = "the"
        self.aggro_chance = stats.Stats.map()["deer"]["aggro-chance"]
        self.herd_aggro_chance = stats.Stats.map()["deer"]["herd-aggro-chance"]
    
    def herd_is_attacked(self):
        for d in self.herd:
            if d.is_attacked():
                return True
    
    def get_herd_aggro_chance(self):
        n = 0
        for d in self.herd:
            if d.is_attacked():
                n += 1

        return math.calculate_muliplicative_chance(self.herd_aggro_chance, n)


class Doe(Deer):
    def __init__(self, engine, x, y, buck):
        self.char = "d"
        self.ai = DoeAI(self, buck)
        super().__init__(engine, x, y)
        self.entity_name = "Doe"
        self.entity_article = "a"
        self.roam_distance = stats.Stats.map()["doe"]["roam-distance"]
        self.attack_damage = stats.Stats.map()["doe"]["attack-damage"]
        self.aggro_chance = stats.Stats.map()["doe"]["aggro-chance"]


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

    def roam(self):
        flog.debug("deer is roaming")
        self.deer.recent_actions.append(f"{self.deer.entity_name} is roaming.")
        dist = self.deer.roam_distance
        unclamped_x = rng.range_int(self.deer.x - dist, self.deer.x + dist + 1)
        unclamped_y = rng.range_int(self.deer.y - dist, self.deer.y + dist + 1)

        self.deer.ai.action_queue.append(MovementAction(self.deer, self.deer.engine.game_map.clamp_coord(unclamped_x, unclamped_y)))


class BuckAI(DeerAI):
    def __init__(self, buck):
        self.buck = buck
        super().__init__(buck)
    
    def decide_what_to_do(self):
        actions = []
        
        if self.deer.is_attacked():
            if rng.rand() < self.deer.aggro_chance:
                self.action_queue.append(PursueAction(self.deer, self.deer.attacker))
            else:
                self.action_queue.append(FleeAction(self.deer, self.deer.attacker))
        elif self.deer.herd_is_attacked():
            if rng.rand() < self.deer.get_herd_aggro_chance():
                self.deer.recent_actions.append(f"{self.deer.entity_name} is defending his herd!")
                for d in self.deer.herd:
                    if d.is_attacked():
                        self.action_queue.append(PursueAction(self.deer, d.attacker))
                        break
            else:
                self.roam()
        elif self.deer.is_hungry():
            flog.debug("deer is hungry")
            self.action_queue.append(GrazeAction(self.deer))
        elif self.deer.is_tired():
            flog.debug("deer is tired")
            self.deer.recent_actions.append(f"{self.deer.entity_name} is laying down.")
            self.deer.ai.action_queue.append(SleepAction(self.deer))
        else:
            self.roam()
        
        return actions


class DoeAI(DeerAI):
    def __init__(self, doe, buck):
        self.doe = doe
        self.buck = buck
        self.leash = stats.Stats.map()["doe"]["leash"]
        super().__init__(doe)
    
    def decide_what_to_do(self):
        actions = []
        
        if self.is_too_far_from_buck():
            self.doe.ai.action_queue.append(PursueAction(self.doe, self.buck))
        elif self.doe.is_hungry():
            flog.debug("doe is hungry")
            self.action_queue.append(GrazeAction(self.doe))
        elif self.doe.is_tired():
            flog.debug("doe is tired")
            self.doe.recent_actions.append("Doe is laying down.")
            self.doe.ai.action_queue.append(SleepAction(self.doe))
        else:
            self.roam()
        
        return actions

    def is_too_far_from_buck(self):
        dist_x = abs(self.doe.x - self.buck.x)
        dist_y = abs(self.doe.y - self.buck.y)

        return (dist_x + dist_y) > self.leash


class MovementAction():
    def __init__(self, deer, dest, path=None):
        self.deer = deer
        self.dest = dest
        self.path = path
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["movement-action"]

    def perform(self):
        if self.deer.alive:
            if not self.path:
                self.path = deque(pf.get_path(self.deer.engine.game_map.path_map, self.deer.coord(), self.dest))

            if len(self.path) > 0:
                dest = self.path.popleft()
                self.deer.move_to(dest)
                self.deer.ai.action_queue.append(ScanForThreatsAction(self.deer, self.path))


class PursueAction():
    def __init__(self, deer, target):
        self.deer = deer
        self.target = target
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["pursue-action"]

    def perform(self):
        flog.debug("deer is pursuing")
        self.deer.recent_actions.append(f"{self.deer.entity_name} is pursuing {self.target.entity_article} {self.target.entity_name.lower()}.")

        if self.deer.alive:
            dest = pf.path_to_target(self.deer, self.target)
            self.deer.move(dest.x, dest.y)

            if self.deer.is_target_in_range(self.target):
                if isinstance(self.target, Buck):
                    self.deer.recent_actions.append(f"{self.deer.entity_name} has caught up with {self.target.entity_article} {self.target.entity_name.lower()}.")
                    self.deer.ai.action_queue.append(ScanForThreatsAction(self.deer))
                else:
                    if self.target.alive:
                        self.deer.ai.action_queue.append(AttackAction(self.deer, self.target))
                        self.deer.ai.action_queue.append(FleeAction(self.deer, self.target))
            else:
                if self.target.alive:
                    self.deer.ai.action_queue.append(PursueAction(self.deer, self.target))


class FleeAction():
    def __init__(self, deer, threat, path=None):
        self.deer = deer
        self.threat = threat
        self.path = path
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["flee-action"]
        self.flee_search_attempts = stats.Stats.map()["deer"]["flee-search-attempts"]
        self.flee_jitter_multiplier = stats.Stats.map()["deer"]["flee-jitter-multiplier"]
    
    def find_pathable_destination(self, deer, threat):
        path = []
        opp_coord = math.get_opposite_coord(deer.coord(), threat.coord())

        for i in range(self.flee_search_attempts):
            jitter_muliplier = self.flee_jitter_multiplier
            jitter_max = i * jitter_muliplier
            jitter_min = -(i * jitter_muliplier)
            x_jitter = rng.range_int(jitter_min, jitter_max)
            y_jitter = rng.range_int(jitter_min, jitter_max)
            dest_x = opp_coord.x + x_jitter
            dest_y = opp_coord.y + y_jitter

            tile = self.deer.engine.game_map.get_tile(opp_coord.x + x_jitter, opp_coord.y + y_jitter)

            if tile != None:
                if tile.terrain.walkable:
                    path = deque(pf.get_path(self.deer.engine.game_map.path_map, self.deer.coord(), Coord(dest_x, dest_y)))

                if len(path) > 0:
                    break

        return path

    def perform(self):
        flog.debug("deer is fleeing")
        self.deer.recent_actions.append(f"{self.deer.entity_name} is fleeing from {self.threat.entity_article} {self.threat.entity_name.lower()}.")

        if self.deer.alive:
            if not self.path:
                self.path = self.find_pathable_destination(self.deer, self.threat)

            if len(self.path) > 0:
                dest = self.path.popleft()
                self.deer.move_to(dest)

                if len(self.path) > 0:
                    self.deer.ai.action_queue.append(FleeAction(self.deer, self.threat, self.path))
                else:
                    self.deer.ai.action_queue.append(ScanForThreatsAction(self.deer))
            else:
                self.deer.recent_actions.append(f"{self.deer.entity_name} feels trapped and is turning to fight {self.threat.entity_article} {self.threat.entity_name.lower()}!")
                self.deer.ai.action_queue.append(PursueAction(self.deer, self.threat))


class ScanForThreatsAction(enta.SearchAreaActionBase):
    def __init__(self, deer, path=None):
        self.deer = deer
        self.path = path
        self.search_radius = self.deer.vision_distance[self.deer.engine.time_of_day]
        self.threat_classes = [wlf.Wolf.__name__, htr.Hunter.__name__]
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["scan-for-threats-action"]

    def perform(self):
        search_area = self.get_search_area(self.deer, self.search_radius, vsmap.circle)
        found_entities = self.find_entities(search_area, self.threat_classes)
        living_entities = [entity for entity in found_entities if entity.alive]

        if len(living_entities) > 0:
            for e in living_entities:
                if e.alive and e.__class__.__name__ in self.threat_classes:
                    self.deer.ai.action_queue.append(FleeAction(self.deer, e))
                    return

                self.deer.recent_actions.append(f"{self.deer.entity_name} scanned for threats and found none.")

        self.deer.attacker = None

        if self.path != None and len(self.path) > 0:
            self.deer.ai.action_queue.append(MovementAction(self.deer, None, self.path)) # dest None is a little dirty


class AttackAction():
    def __init__(self, deer, target):
        self.deer = deer
        self.target = target
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["attack-action"]

    def perform(self):
        flog.debug("deer is attacking")
        self.deer.recent_actions.append(f"{self.deer.entity_name} is attacking {self.target.entity_article} {self.target.entity_name.lower()}.")
        self.target.harm(self.deer.attack_damage, self.deer)

        if not self.target.alive:
            self.deer.recent_actions.append(f"{self.deer.entity_name} killed {self.target.entity_article} {self.target.entity_name.lower()}!")
            self.deer.attacked = False


class GrazeAction():
    def __init__(self, deer):
        self.deer = deer
        self.cooldown = stats.Stats.map()["deer"]["action-cooldowns"]["graze-action"]

    def perform(self):
        flog.debug("deer is grazing")
        self.deer.recent_actions.append(f"{self.deer.entity_name} is grazing.")
        self.deer.ai.action_queue.append(ScanForThreatsAction(self.deer))


class SleepAction():
    def __init__(self, deer):
        self.deer = deer

    def perform(self):
        sleep_in = rng.rand() < stats.Stats.map()["deer"]["sleep-in-chance"]

        if self.deer.should_wake_up():
            flog.debug("deer woke up after being attacked")
            self.deer.recent_actions.append(f"{self.deer.entity_name} woke up.")
            self.deer.asleep = False
        elif self.deer.is_tired():
            flog.debug("deer is sleeping")
            self.deer.recent_actions.append(f"{self.deer.entity_name} is asleep.")
            self.deer.asleep = True
            self.deer.ai.action_queue.append(SleepAction(self.deer))
        else:
            flog.debug("deer woke up")
            self.deer.recent_actions.append(f"{self.deer.entity_name} woke up.")
            self.deer.asleep = False
