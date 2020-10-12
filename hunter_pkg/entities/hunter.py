from __future__ import annotations

from collections import deque
from datetime import timedelta
import json
from numpy.random import randint
from time import time

from hunter_pkg.entities import camp as cp
from hunter_pkg.entities import base_entity
from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import bow as bw
from hunter_pkg.entities import entity_actions as enta
from hunter_pkg.entities import rabbit as rbt

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
        super().__init__(engine, x, y, "H", colors.white(), colors.light_gray(), HunterAI(self), [stats.Stats.map()["hunter"]["update-interval-start"], stats.Stats.map()["hunter"]["update-interval-end"]], stats.Stats.map()["hunter"]["update-interval-step"])
        self.name = self.get_name()
        self.alive = True
        self.asleep = False
        self.hidden = False
        self.max_hunger = stats.Stats.map()["hunter"]["max-hunger"]
        self.max_health = stats.Stats.map()["hunter"]["max-health"]
        self.max_energy = stats.Stats.map()["hunter"]["max-energy"]
        self.curr_hunger = stats.Stats.map()["hunter"]["starting-hunger"]
        self.curr_health = stats.Stats.map()["hunter"]["starting-health"]
        self.curr_energy = stats.Stats.map()["hunter"]["starting-energy"]
        self.vision_distance = stats.Stats.map()["hunter"]["vision-distance"]
        self.memory = HunterMemory()
        self.recent_actions = []
        self.max_recent_actions = 100
        self.min_recent_actions = 30
        self.days_survived = 0
        self.rt_spawn_time = time()
        self.bow = bw.Bow()
        self.bed = None
        self.accuracy = stats.Stats.map()["hunter"]["accuracy"]
    
    def get_name(self):
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

    def should_wake_up(self):
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

    def rand_health_alert(self):
        return 1 - (self.curr_health / self.max_health)

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
    
    def try_flush_recent_actions(self):
        #flog.debug(f"hunter recent_actions: {len(self.recent_actions)}")

        if len(self.recent_actions) > self.max_recent_actions:
            self.recent_actions = self.recent_actions[self.max_recent_actions-self.min_recent_actions:]
            flog.debug("flushed hunter recent_actions")

    def get_rt_time_alive(self):
        rt_time_alive = timedelta(seconds=round(time() - self.rt_spawn_time))
        flog.debug(f"time alive: {rt_time_alive}")

        return rt_time_alive


class HunterAI():
    def __init__(self, hunter):
        self.hunter = hunter
        self.action_queue = deque()

    def perform(self):
        if len(self.action_queue) > 0:
            action = self.action_queue.popleft()
            action.perform()
        else:
            actions = self.decide_what_to_do()
            for a in actions:
                self.action_queue.append(a)
    
    def clear_action_queue(self):
        self.action_queue = deque()

    def decide_what_to_do(self):
        actions = []
        # Note: this doesn't work so great, but leaving it in for now
        # if self.hunter.is_affected_by(stfx.SleepDeprivation) and rng.rand() < self.hunter.rand_health_alert():
        #     flog.debug("hunter is SLEEP DEPRIVED and going to camp")
        #     self.hunter.recent_actions.append("Hunter is sleep deprived and going to camp!")

        #     for action in pf.path_to(self.hunter, [self.hunter.memory.map["camp"]["x"], self.hunter.memory.map["camp"]["y"]], MovementAction):
        #         self.hunter.ai.action_queue.append(action)
            
        #     for component in self.hunter.engine.camp.components:
        #         if isinstance(component, cp.Bedroll):
        #             self.hunter.ai.action_queue.append(SleepAction(self.hunter, component))
        #             break
        if self.hunter.is_hungry():
            flog.debug("hunter is HUNGRY")
            self.hunter.recent_actions.append("Hunter is hungry!")
            actions.append(SearchAreaAction(self.hunter, (bb.BerryBush, rbt.Rabbit)))
        elif self.hunter.is_tired():
            flog.debug("hunter is TIRED")
            self.hunter.recent_actions.append("Hunter is tired!")
            self.hunter.recent_actions.append("Hunter is going to camp.")

            for action in pf.path_to(self.hunter, [self.hunter.memory.map["camp"]["x"], self.hunter.memory.map["camp"]["y"]], MovementAction):
                self.hunter.ai.action_queue.append(action)
            
            for component in self.hunter.engine.camp.components:
                if isinstance(component, cp.Bedroll):
                    self.hunter.ai.action_queue.append(SleepAction(self.hunter, component))
                    break
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
                dest_x = math.clamp(rng.range(self.hunter.x - dist, self.hunter.x + dist), 0, self.hunter.engine.game_map.width - 1)
                dest_y = math.clamp(rng.range(self.hunter.y - dist, self.hunter.y + dist), 0, self.hunter.engine.game_map.height - 1)

                if [dest_x, dest_y] not in forbidden:
                    if self.hunter.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
                        explored = f"{dest_x},{dest_y}" in self.hunter.memory.map["explored-terrain"]
                        distance = math.get_distance(self.hunter.x, self.hunter.y, dest_x, dest_y)
                        candidates.append([dest_x, dest_y, explored, distance])
                    else:
                        forbidden.append([dest_x, dest_y])

            # sort by explored and distance
            candidates = sorted(candidates, key=lambda x: (-x[2], -x[3]))

            for dest in candidates:
                # prefer to take the first one that is in fog and farthest away
                # this way hunter will tend to travel longer distances and explore more fog
                actions = pf.path_to(self.hunter, [dest_x, dest_y], MovementAction)

                if len(actions) < stats.Stats.map()["hunter"]["max-path-distance"]:
                    return actions
                else:
                    forbidden.append([dest_x, dest_y])


class HunterMemory():
    def __init__(self):
        self.map = {
            "explored-terrain": {}
        }


class MovementAction():
    def __init__(self, hunter, dy, dx):
        self.hunter = hunter
        self.dx = dx
        self.dy = dy

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
                self.hunter.engine.game_map.tiles[clmp_y][clmp_x].explored = curr_visible or prev_visible

    def perform(self):
        flog.debug("hunter is moving")

        dest_x = self.hunter.x + self.dx
        dest_y = self.hunter.y + self.dy

        if not self.hunter.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not self.hunter.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return  # Destination is blocked by a tile.

        # remove reference from origin tile
        orig_tile = self.hunter.engine.game_map.tiles[self.hunter.y][self.hunter.x]
        for entity in orig_tile.entities:
            if entity == self.hunter:
                orig_tile.entities.remove(entity)
        
        # add reference to destination tile
        self.hunter.engine.game_map.tiles[dest_y][dest_x].entities.append(self.hunter)

        self.hunter.move(self.dx, self.dy)
        self.remember_terrain(self.hunter)


class SearchAreaAction(enta.SearchAreaActionBase):
    def __init__(self, hunter, search_for_classes):
        self.hunter = hunter
        self.search_radius = self.hunter.vision_distance[hunter.engine.time_of_day]
        self.search_for_classes = [c.__name__ for c in search_for_classes]

    def perform(self):
        flog.debug("hunter is searching area")
        self.hunter.recent_actions.append("Hunter is searching area.")

        search_area = self.get_search_area(self.hunter, self.search_radius, vsmap.circle)
        found_entities = self.find_entities(search_area, self.search_for_classes)

        if len(found_entities) > 0:
            self.hunter.recent_actions.append(f"Hunter found something to eat.")
        else:
            self.hunter.recent_actions.append(f"Hunter couldn't find anything to eat.")

        nearest_entity = self.get_nearest_entity(self.hunter, found_entities)

        if nearest_entity != None:
            if isinstance(nearest_entity, bb.BerryBush):
                for action in pf.path_to(self.hunter, [nearest_entity.x, nearest_entity.y], MovementAction):
                    self.hunter.ai.action_queue.append(action)
                
                self.hunter.ai.action_queue.append(PickAndEatAction(self.hunter, nearest_entity))
            else: # rbt.Rabbit
                if nearest_entity.alive:
                    self.hunter.ai.action_queue.append(ShootBowAction(self.hunter, self.hunter.bow, nearest_entity))
                else:
                    self.hunter.recent_actions.append("Hunter is walking to rabbit carcass.")
                    for action in pf.path_to(self.hunter, [nearest_entity.x, nearest_entity.y], MovementAction):
                        self.hunter.ai.action_queue.append(action)

                    self.hunter.ai.action_queue.append(EatRabbitAction(self.hunter, nearest_entity))
        else:
            for action in self.hunter.ai.roam():
                self.hunter.ai.action_queue.append(action)


class PickAndEatAction():
    def __init__(self, hunter, static_entity):
        self.hunter = hunter
        self.static_entity = static_entity

    def perform(self):
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
        self.hunter.recent_actions.append("Hunter ate a rabbit!")
        self.hunter.eat(self.rabbit)


class SleepAction():
    def __init__(self, hunter, bed):
        self.hunter = hunter
        self.bed = bed
        self.hunter.bed = bed

    def perform(self):
        if (self.hunter.curr_energy >= (self.hunter.max_energy - stats.Stats.map()["hunter"]["energy-loss"]) and self.hunter.engine.time_of_day != tod.NIGHT) or self.hunter.should_wake_up():
            # wake up
            self.hunter.recent_actions.append("Hunter woke up.")
            self.hunter.asleep = False
            self.hunter.bed = None
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


class ShootBowAction():
    def __init__(self, hunter, bow, target):
        self.hunter = hunter
        self.bow = bow
        self.target = target

    def perform(self):
        if self.bow.shoot(self.hunter, self.target):
            self.hunter.recent_actions.append("Hunter shot the bow and hit!")
            self.hunter.recent_actions.append("Hunter is walking to rabbit carcass.")

            for action in pf.path_to(self.hunter, [self.target.x, self.target.y], MovementAction):
                self.hunter.ai.action_queue.append(action)

            self.hunter.ai.action_queue.append(EatRabbitAction(self.hunter, self.target))
        else:
            self.hunter.recent_actions.append("Hunter shot the bow and missed!")
        