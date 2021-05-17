from __future__ import annotations

from collections import deque
from datetime import timedelta
import json
from time import time

from hunter_pkg.entities import camp as cp
from hunter_pkg.entities import base_entity
from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import bow as bw
from hunter_pkg.entities import entity_actions as enta
from hunter_pkg.entities import rabbit as rbt
from hunter_pkg.entities import wolf as wlf

from hunter_pkg.helpers.coord import Coord
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
from hunter_pkg import vision_map as vsmap


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Hunter(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "H", colors.white(), colors.hunter_green(), HunterAI(self), "Hunter", "the")
        self.human_name = self.get_human_name()
        self.name = "Hunter"
        self.alive = True
        self.asleep = False
        self.hidden = False
        self.attacked = False
        self.max_hunger = stats.Stats.map()["hunter"]["max-hunger"]
        self.max_health = stats.Stats.map()["hunter"]["max-health"]
        self.max_energy = stats.Stats.map()["hunter"]["max-energy"]
        self.curr_hunger = stats.Stats.map()["hunter"]["starting-hunger"]
        self.curr_health = stats.Stats.map()["hunter"]["starting-health"]
        self.curr_energy = stats.Stats.map()["hunter"]["starting-energy"]
        self.vision_distance = stats.Stats.map()["hunter"]["vision-distance"]
        self.attk_dmg = stats.Stats.map()["hunter"]["attack-damage"]
        self.bandage_threshold = stats.Stats.map()["hunter"]["bandage-threshold"]
        self.bandage_heal_amount = stats.Stats.map()["hunter"]["bandage-heal-amount"]
        self.memory = HunterMemory()
        self.max_recent_actions = stats.Stats.map()["hunter"]["max-recent-actions"]
        self.min_recent_actions = stats.Stats.map()["hunter"]["min-recent-actions"]
        self.days_survived = 1
        self.rt_spawn_time = time()
        self.bow = bw.Bow()
        self.bed = None
        self.accuracy = stats.Stats.map()["hunter"]["accuracy"]
    
    def get_human_name(self):
        with open("resources/names.json") as file:
            flog.debug("opened a file")
            names = json.load(file)
            return names["names"][rng.randint(len(names["names"]))]

    def can_see(self, entity):
        vd = self.vision_distance[entity.engine.time_of_day]
        visible_x = (self.x - vd) < entity.x and entity.x < (self.x + vd)
        visible_y = (self.y - vd) < entity.y and entity.y < (self.y + vd)

        return visible_x and visible_y

    def eat(self, entity):
        flog.debug("hunter ate something")
        self.curr_hunger += entity.nutritional_value
        entity.consume()

    def is_hungry(self):
        return self.curr_hunger < stats.Stats.map()["hunter"]["hunger-threshold-low"]

    def is_still_hungry(self):
        return self.curr_hunger < stats.Stats.map()["hunter"]["hunger-threshold-high"]

    def is_tired(self):
        return self.curr_energy < stats.Stats.map()["hunter"]["tired-threshold"] or self.engine.time_of_day == tod.NIGHT
    
    def is_attacked(self):
        return self.attacked

    def should_bandage(self):
        # TODO change; it's weird to only prevent bandaging when starving
        return self.curr_health <= self.bandage_threshold and not self.is_affected_by(stfx.Starvation)

    def should_wake_up(self):
        if self.attacked:
            return True
        else:
            chance_to_wake_up = 0

            if self.bed == None:
                chance_to_wake_up += stats.Stats.map()["ground"]["wake-chance"]
            else:
                chance_to_wake_up += self.bed.wake_chance
            
            if self.is_affected_by(stfx.Starvation):
                chance_to_wake_up += self.rand_health_alert()

            roll = rng.rand()

            # flog.debug("---chance to wake up---")
            # flog.debug(f"health: {self.curr_health}")
            # flog.debug(f"chance: {chance_to_wake_up}")
            # flog.debug(f"roll: {roll})")
            # flog.debug(f"res: {chance_to_wake_up > roll}")

            return roll < chance_to_wake_up

    def wake_up(self):
        self.recent_actions.append("Hunter woke up.")
        self.asleep = False
        self.bed = None

    def rand_health_alert(self):
        return 1 - (self.curr_health / self.max_health)

    def harm(self, damage, attacker):
        super().harm(damage, attacker)
        self.recent_actions.append("Hunter was attacked!")

    def die(self):
        flog.debug("omg hunter died")
        self.recent_actions.append("Hunter has died!")

        self.alive = False
        self.char = "X"

    def progress(self):
        if self.alive:
            if self.is_affected_by(stfx.Starvation):
                self.curr_health -= stats.Stats.map()["hunter"]["starvation-health-loss"]
            if self.is_affected_by(stfx.SleepDeprivation):
                self.curr_health -= stats.Stats.map()["hunter"]["sleep-deprivation-health-loss"]
                chance_to_pass_out = self.rand_health_alert() * stats.Stats.map()["hunter"]["sleep-deprivation-chance-to-pass-out"]
                roll = rng.rand()

                # flog.debug("---chance to pass out---")
                # flog.debug(f"health: {self.curr_health}")
                # flog.debug(f"chance: {chance_to_pass_out}")
                # flog.debug(f"roll: {roll}")
                # flog.debug(f"res: {chance_to_pass_out > roll}")

                if chance_to_pass_out > roll and not self.asleep:
                    self.recent_actions.append("Hunter passed out from sleep deprivation!")
                    self.ai.clear_action_queue()
                    self.ai.action_queue.append(SleepAction(self, None))
            
            self.curr_hunger -= stats.Stats.map()["hunter"]["hunger-loss"]
            self.curr_energy -= stats.Stats.map()["hunter"]["energy-loss"]
            self.try_flush_recent_actions()

    def get_rt_time_alive(self):
        rt_time_alive = timedelta(seconds=round(time() - self.rt_spawn_time))
        flog.debug(f"time alive: {rt_time_alive}")

        return rt_time_alive

    def selection_info(self):
        info = [
            self.human_name,
            "The Hunter"
        ]

        if not self.alive:
            info.append("*Dead*")

        info.extend([
            f"Coord: ({self.x},{self.y})",
            {
                "Inventory": [
                    "Dagger",
                    "Bow",
                    "Arrows",
                ],
            }
        ])

        return info


class HunterAI():
    def __init__(self, hunter):
        self.hunter = hunter
        self.action_queue = deque()
        self.default_cooldown = stats.Stats.map()["hunter"]["action-cooldowns"]["default"]

    # returns cooldown of AI action that was performed
    def perform(self):
        cooldown = self.default_cooldown

        if self.hunter.alive:
            if len(self.action_queue) > 0:
                action = self.action_queue.popleft()
                cooldown = action.cooldown if gen.has_member(action, 'cooldown') else self.default_cooldown
                action.perform()
            else:
                actions = self.decide_what_to_do()
                for a in actions:
                    self.action_queue.append(a)
        
        return cooldown
    
    def clear_action_queue(self):
        self.action_queue = deque()

    def decide_what_to_do(self):
        actions = []
        # Note: this doesn't work so great, but leaving it in for now
        # if self.hunter.is_affected_by(stfx.SleepDeprivation) and rng.rand() < self.hunter.rand_health_alert():
        #     flog.debug("hunter is SLEEP DEPRIVED and going to camp")
        #     self.hunter.recent_actions.append("Hunter is sleep deprived and going to camp!")

        #     for action in pf.path_to_dest_2(self.hunter, [self.hunter.memory.map["camp"]["x"], self.hunter.memory.map["camp"]["y"]], MovementAction):
        #         self.hunter.ai.action_queue.append(action)
            
        #     for component in self.hunter.engine.camp.components:
        #         if isinstance(component, cp.Bedroll):
        #             self.hunter.ai.action_queue.append(SleepAction(self.hunter, component))
        #             break
        if self.hunter.is_attacked():
            actions.append(SearchAreaAction(self.hunter, [wlf.Wolf]))
        elif self.hunter.should_bandage():
            flog.debug("hunter is WOUNDED")
            self.hunter.recent_actions.append("Hunter is wounded!")
            actions.append(BandageAction(self.hunter))
        elif self.hunter.is_hungry():
            flog.debug("hunter is HUNGRY")
            self.hunter.recent_actions.append("Hunter is hungry!")
            actions.append(SearchAreaAction(self.hunter, (bb.BerryBush, rbt.Rabbit)))
        elif self.hunter.is_tired():
            flog.debug("hunter is TIRED")
            self.hunter.recent_actions.append("Hunter is tired!")
            self.hunter.recent_actions.append("Hunter is going to camp.")

            sleep_action = None

            for component in self.hunter.engine.camp.components:
                if isinstance(component, cp.Bedroll):
                    sleep_action = SleepAction(self.hunter, component)
                    break

            actions.append(MovementAction(self.hunter, Coord(self.hunter.memory.map["camp"]["x"], self.hunter.memory.map["camp"]["y"]), None, sleep_action))
        else:
            flog.debug("hunter is NOT hungry or tired")
            self.hunter.recent_actions.append("Hunter is not hungry or tired.")
            actions = self.roam()

        return actions

    def roam(self):
        dist = stats.Stats.map()["hunter"]["roam-distance"]
        forbidden = [] # prevent retrying the same tiles

        while(True):
            candidates = []

            # get 3 candidate distinations
            while(len(candidates) < stats.Stats.map()["hunter"]["roam-candidates"]):
                unclamped_x = rng.range_int(self.hunter.x - dist, self.hunter.x + dist + 1)
                unclamped_y = rng.range_int(self.hunter.y - dist, self.hunter.y + dist + 1)
                dest = self.hunter.engine.game_map.clamp_coord(unclamped_x, unclamped_y)

                if [dest.x, dest.y] not in forbidden:
                    if self.hunter.engine.game_map.tiles[dest.y][dest.x].terrain.walkable:
                        explored = f"{dest.x},{dest.y}" in self.hunter.memory.map["explored-terrain"]
                        distance = math.get_distance(self.hunter.x, self.hunter.y, dest.x, dest.y)
                        candidates.append([dest.x, dest.y, explored, distance])
                    else:
                        forbidden.append([dest.x, dest.y])

            # sort by explored and distance
            candidates = sorted(candidates, key=lambda x: (-x[2], -x[3]))

            for dest in candidates:
                x = dest[0]
                y = dest[1]

                # prefer to take the first one that is in fog and farthest away
                # this way hunter will tend to travel longer distances and explore more fog
                path = deque(pf.get_path(self.hunter.engine.game_map.path_map, self.hunter.coord(), Coord(x, y)))

                if len(path) < stats.Stats.map()["hunter"]["max-path-distance"]:
                    return [MovementAction(self.hunter, Coord(x, y), path)]
                else:
                    forbidden.append([x, y])


class HunterMemory():
    def __init__(self):
        self.map = {
            "explored-terrain": {}
        }


class MovementAction():
    def __init__(self, hunter, dest, path=None, final_action=None):
        self.hunter = hunter
        self.dest = dest
        self.path = path
        self.final_action = final_action
        self.cooldown = stats.Stats.map()["hunter"]["action-cooldowns"]["movement-action"]

    def remember_terrain(self, hunter):
        vd = self.hunter.vision_distance[hunter.engine.time_of_day]
        vision_map = vsmap.circle(vd)
        x_start = self.hunter.x - vd
        x_end = self.hunter.x + vd
        y_start = self.hunter.y - vd
        y_end = self.hunter.y + vd

        for y in range(y_start, y_end+1):
            for x in range(x_start, x_end+1):
                # This is confusing. Basic idea is to apply the vision map to the hunter's memory and the game map, but only
                # set "explored" to True, never to False i.e. don't let the corners of a circular vision map "unexplore" tiles.
                # And clamp everything so we dont accidentally affect the opposite side of the map.
                clamp_width = self.hunter.engine.game_map.width-1
                clamp_height = self.hunter.engine.game_map.height-1
                rel_x = math.clamp(x - x_start, 0, clamp_width)
                rel_y = math.clamp(y - y_start, 0, clamp_height)
                clmp_x = math.clamp(x, 0, clamp_width)
                clmp_y = math.clamp(y, 0, clamp_height)
                prev_visible = f"{clmp_x},{clmp_y}" in self.hunter.memory.map["explored-terrain"].keys() and self.hunter.memory.map["explored-terrain"][f"{clmp_x},{clmp_y}"]
                curr_visible = vision_map[rel_y][rel_x].visible
                self.hunter.memory.map["explored-terrain"][f"{clmp_x},{clmp_y}"] = curr_visible or prev_visible

                if curr_visible or prev_visible:
                    self.hunter.engine.game_map.tiles[clmp_y][clmp_x].reveal()

    def perform(self):
        if self.hunter.alive:
            flog.debug("hunter is moving")

            if not self.path:
                self.path = deque(pf.get_path(self.hunter.engine.game_map.path_map, self.hunter.coord(), self.dest))

            if len(self.path) > 0:
                dest = self.path.popleft()
                self.hunter.move_to(dest)
                self.remember_terrain(self.hunter)

                if len(self.path) > 0:
                    self.hunter.ai.action_queue.append(MovementAction(self.hunter, dest, self.path, self.final_action))
                elif self.final_action:
                    self.hunter.ai.action_queue.append(self.final_action)
            elif self.final_action:
                self.hunter.ai.action_queue.append(self.final_action)


class SearchAreaAction(enta.SearchAreaActionBase):
    def __init__(self, hunter, search_for_classes):
        self.hunter = hunter
        self.search_radius = self.hunter.vision_distance[hunter.engine.time_of_day]
        self.search_for_classes = [c.__name__ for c in search_for_classes]
        self.cooldown = stats.Stats.map()["hunter"]["action-cooldowns"]["search-area-action"]

    def perform(self):
        flog.debug("hunter is searching area")
        self.hunter.recent_actions.append("Hunter is searching area.")

        search_area = self.get_search_area(self.hunter, self.search_radius, vsmap.circle)
        found_entities = self.find_entities(search_area, self.search_for_classes)
        nearest_entity = self.get_nearest_entity(self.hunter, found_entities)

        if nearest_entity != None:
            if isinstance(nearest_entity, bb.BerryBush):
                self.hunter.ai.action_queue.append(MovementAction(self.hunter, nearest_entity.coord(), None, PickAndEatAction(self.hunter, nearest_entity)))
            elif isinstance(nearest_entity, wlf.Wolf):
                self.hunter.ai.action_queue.append(PursueAction(self.hunter, nearest_entity))
            else: # rbt.Rabbit
                if nearest_entity.alive:
                    self.hunter.ai.action_queue.append(ShootBowAction(self.hunter, self.hunter.bow, nearest_entity))
                else:
                    self.hunter.recent_actions.append("Hunter is walking to rabbit carcass.")
                    self.hunter.ai.action_queue.append(MovementAction(self.hunter, nearest_entity.coord(), None, EatRabbitAction(self.hunter, nearest_entity)))
        else:
            # couldn't find threat, so assume no longer attacked
            self.hunter.attacked = False

            for action in self.hunter.ai.roam():
                self.hunter.ai.action_queue.append(action)


class PickAndEatAction():
    def __init__(self, hunter, static_entity):
        self.hunter = hunter
        self.static_entity = static_entity

    def perform(self):
        if self.hunter.attacked:
            flog.debug("skipping PickAndEatAction due to being attacked")
        else:
            flog.debug("hunter is picking and eating")
            self.hunter.recent_actions.append("Hunter is picking and eating a berry.")

            berry = self.static_entity.pick_berry()

            if berry != None:
                self.hunter.eat(berry)
                
                if self.hunter.is_still_hungry():
                    flog.debug("hunter is still hungry {}/{}".format(self.hunter.curr_hunger, self.hunter.max_hunger))
                    if self.static_entity.num_berries > 0:
                        self.hunter.ai.action_queue.append(PickAndEatAction(self.hunter, self.static_entity))
                    else:
                        self.hunter.ai.action_queue.append(SearchAreaAction(self.hunter, (bb.BerryBush, rbt.Rabbit)))
                else:
                    self.hunter.recent_actions.append("Hunter is full!")
            else:
                for action in self.hunter.ai.roam():
                    self.hunter.ai.action_queue.append(action)


# TODO refactor EatRabbitAction and PickAndEatAction
class EatRabbitAction():
    def __init__(self, hunter, rabbit):
        self.hunter = hunter
        self.rabbit = rabbit

    def perform(self):
        if self.hunter.attacked:
            flog.debug("skipping EatRabbitAction due to being attacked")
        else:
            self.hunter.recent_actions.append("Hunter ate a rabbit!")
            self.hunter.eat(self.rabbit)


class SleepAction():
    def __init__(self, hunter, bed):
        self.hunter = hunter
        self.bed = bed
        self.hunter.bed = bed

    def perform(self):
        if (self.hunter.curr_energy >= (self.hunter.max_energy - stats.Stats.map()["hunter"]["energy-loss"]) and self.hunter.engine.time_of_day != tod.NIGHT) or self.hunter.should_wake_up():
            self.hunter.wake_up()
            # grab a brush and put a little makeup

            if self.bed != None:
                self.bed.occupied = False
        else:
            self.hunter.recent_actions.append("Hunter is sleeping.")
            self.hunter.asleep = True

            if self.bed != None:
                self.bed.occupied = True
                comfort = self.bed.comfort
            else:
                comfort = stats.Stats.map()["ground"]["sleep-comfort"]

            self.hunter.curr_energy += comfort
            self.hunter.curr_health += stats.Stats.map()["hunter"]["sleep-health-gain"] if not self.bed == None else stats.Stats.map()["ground"]["sleep-health-gain"]

            self.hunter.ai.action_queue.append(SleepAction(self.hunter, self.bed))


class PursueAction():
    def __init__(self, hunter, target):
        self.hunter = hunter
        self.target = target

    def perform(self):
        flog.debug("hunter is pursuing")
        if self.hunter.alive:
            dest = pf.path_to_target(self.hunter, self.target)
            self.hunter.move(dest.x, dest.y)

            if self.target.alive:
                if self.hunter.is_target_in_range(self.target):
                    self.hunter.ai.action_queue.append(Action(self.hunter, self.target))
                else:
                    self.hunter.ai.action_queue.append(PursueAction(self.hunter, self.target))


class AttackAction():
    def __init__(self, hunter, target):
        self.hunter = hunter
        self.target = target

    def perform(self):
        flog.debug("hunter is attacking")
        self.hunter.recent_actions.append("Hunter attacked a wolf.")
        self.target.harm(self.hunter.attk_dmg, self.hunter)

        if not self.target.alive:
            self.hunter.recent_actions.append("Hunter killed a wolf!")
            self.hunter.attacked = False


class ShootBowAction():
    def __init__(self, hunter, bow, target):
        self.hunter = hunter
        self.bow = bow
        self.target = target

    def perform(self):
        if self.bow.shoot(self.hunter, self.target):
            self.hunter.recent_actions.append("Hunter shot the bow and hit!")
            self.hunter.recent_actions.append("Hunter is walking to rabbit carcass.")
            self.hunter.ai.action_queue.append(MovementAction(self.hunter, self.target.coord(), None, EatRabbitAction(self.hunter, self.target)))
        else:
            self.hunter.recent_actions.append("Hunter shot the bow and missed!")


class BandageAction():
    def __init__(self, hunter):
        self.hunter = hunter

    def perform(self):
        self.hunter.recent_actions.append("Hunter bandaged.")
        self.hunter.heal(self.hunter.bandage_heal_amount)
