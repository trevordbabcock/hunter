from collections import deque

from hunter_pkg.entities import base_entity
from hunter_pkg.entities import deer as dr
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
from hunter_pkg import status_effects as stfx
from hunter_pkg import terrain as trrn
from hunter_pkg import vision_map as vsmap


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Wolf(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "W", colors.white(), colors.brown(), WolfAI(self), "Wolf")
        self.alive = True
        self.asleep = False
        self.max_hunger = stats.Stats.map()["wolf"]["max-hunger"]
        self.max_health = stats.Stats.map()["wolf"]["max-health"]
        self.max_energy = stats.Stats.map()["wolf"]["max-energy"]
        self.curr_hunger = stats.Stats.map()["wolf"]["starting-hunger"]
        self.curr_health = stats.Stats.map()["wolf"]["starting-health"]
        self.curr_energy = stats.Stats.map()["wolf"]["starting-energy"]
        self.curr_health = stats.Stats.map()["wolf"]["starting-health"]
        self.hunger_loss = stats.Stats.map()["wolf"]["hunger-loss"]
        self.energy_loss = stats.Stats.map()["wolf"]["energy-loss"]
        self.vision_distance = stats.Stats.map()["wolf"]["vision-distance"]
        self.attk_dmg = stats.Stats.map()["wolf"]["attack-damage"]
        self.hunger_threshold = stats.Stats.map()["wolf"]["hunger-threshold"]
        self.tired_threshold = stats.Stats.map()["wolf"]["tired-threshold"]
        self.need_a_snack_chance = stats.Stats.map()["wolf"]["need-a-snack-chance"]
        self.attacker = None
        self.recent_actions = []
        self.hidden = False

    def eat(self, entity):
        flog.debug("wolf ate something")
        self.curr_hunger += entity.nutritional_value
        entity.consume()

    def is_hungry(self):
        return self.curr_hunger < stats.Stats.map()["wolf"]["hunger-threshold"] or rng.rand() < self.need_a_snack_chance

    def is_tired(self):
        return self.curr_energy < stats.Stats.map()["wolf"]["tired-threshold"]

    def should_wake_up(self):
        if self.is_attacked():
            return True
        else:
            chance_to_wake_up = 0

            if self.is_affected_by(stfx.Starvation):
                chance_to_wake_up += self.rand_health_alert()

            roll = rng.rand()

            # flog.debug("---chance to wake up---")
            # flog.debug(f"health: {self.curr_health}")
            # flog.debug(f"chance: {chance_to_wake_up}")
            # flog.debug(f"roll: {roll})")
            # flog.debug(f"res: {chance_to_wake_up > roll}")

            return roll < chance_to_wake_up

    def is_attacked(self):
        return self.attacker != None

    def rand_health_alert(self):
        return 1 - (self.curr_health / self.max_health)

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
            "Hlth {:02.0f}/{}".format(self.curr_health, self.max_health),
            "Hngr {:02.0f}/{}".format(self.curr_hunger, self.max_hunger),
            "Nrgy {:02.0f}/{}".format(self.curr_energy, self.max_energy),
        ])

        return info

    def progress(self):
        if self.alive:
            if self.is_affected_by(stfx.Starvation):
                self.curr_health -= stats.Stats.map()["wolf"]["starvation-health-loss"]
                if not self.alive:
                    self.recent_actions.append("Wolf died of starvation!")
            if self.is_affected_by(stfx.SleepDeprivation):
                self.curr_health -= stats.Stats.map()["wolf"]["sleep-deprivation-health-loss"]
                chance_to_pass_out = self.rand_health_alert() * stats.Stats.map()["wolf"]["sleep-deprivation-chance-to-pass-out"]
                roll = rng.rand()

                # flog.debug("---chance to pass out---")
                # flog.debug(f"health: {self.curr_health}")
                # flog.debug(f"chance: {chance_to_pass_out}")
                # flog.debug(f"roll: {roll}")
                # flog.debug(f"res: {chance_to_pass_out > roll}")

                if chance_to_pass_out > roll and not self.asleep:
                    self.recent_actions.append("Wolf passed out from sleep deprivation!")
                    self.ai.clear_action_queue()
                    self.ai.action_queue.append(SleepAction(self))

            self.curr_hunger -= stats.Stats.map()["wolf"]["hunger-loss"]
            self.curr_energy -= stats.Stats.map()["wolf"]["energy-loss"]
            self.try_flush_recent_actions()


class WolfAI():
    def __init__(self, wolf):
        self.wolf = wolf
        self.action_queue = deque()
        self.default_cooldown = stats.Stats.map()["wolf"]["action-cooldowns"]["default"]

    def clear_action_queue(self):
        self.action_queue = deque()

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
            self.action_queue.append(SearchAreaAction(self.wolf, [rbt.Rabbit, dr.Doe, dr.Buck]))
        elif self.wolf.is_tired():
            flog.debug("wolf is tired")
            self.action_queue.append(SleepAction(self.wolf))
        else:
            if rng.rand() < stats.Stats.map()["wolf"]["nap-chance"]:
                flog.debug("wolf is napping")
                self.wolf.recent_actions.append(f"Wolf is laying down for a nap.")
                self.action_queue.append(SleepAction(self.wolf))
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
            self.target.harm(self.wolf.attk_dmg, self.wolf)

            if not self.target.alive:
                if isinstance(self.target, rbt.Rabbit):
                    self.wolf.ai.action_queue.append(EatAction(self.wolf, self.target))
        else:
            flog.debug("wolf can't attack hidden target")

# DO NOT MERGE fix eat action
class EatAction():
    def __init__(self, wolf, entity):
        self.wolf = wolf
        self.entity = entity

    def perform(self):
        flog.debug(f"wolf is eating a {self.entity.entity_name}")
        self.wolf.recent_actions.append(f"Wolf is eating a {self.entity.entity_name}.")
        self.wolf.eat(self.entity)


class SleepAction():
    def __init__(self, wolf):
        self.wolf = wolf

    def perform(self):
        self.wolf.curr_energy += stats.Stats.map()["wolf"]["sleep-energy-gain"]
        self.wolf.curr_health += stats.Stats.map()["wolf"]["sleep-health-gain"]
        sleep_in = rng.rand() < stats.Stats.map()["wolf"]["sleep-in-chance"]

        if self.wolf.should_wake_up():
            flog.debug("wolf woke up after being attacked")
            self.wolf.recent_actions.append(f"{self.wolf.entity_name} woke up.")
            self.wolf.asleep = False
        elif self.wolf.curr_energy < (self.wolf.max_energy - stats.Stats.map()["wolf"]["energy-loss"]):
            flog.debug("wolf is sleeping")
            self.wolf.recent_actions.append(f"{self.wolf.entity_name} is asleep.")
            self.wolf.asleep = True
            self.wolf.ai.action_queue.append(SleepAction(self.wolf))
        else:
            flog.debug("wolf woke up")
            self.wolf.recent_actions.append(f"{self.wolf.entity_name} woke up.")
            self.wolf.asleep = False