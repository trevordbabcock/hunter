from bisect import insort
from collections import deque
from math import floor
from time import time
from typing import Set, Iterable, Any

import numpy.random as nprand
from tcod.context import Context
from tcod.console import Console

from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import rabbit as rbt
from hunter_pkg.entities import wolf as wlf

from hunter_pkg.helpers import math
from hunter_pkg.helpers import rng
from hunter_pkg.helpers import time_of_day as tod

from hunter_pkg import colors
from hunter_pkg import event as ev
from hunter_pkg import flogging
from hunter_pkg import game_map
from hunter_pkg import input_handlers
from hunter_pkg import log_level
from hunter_pkg import stats
from hunter_pkg import terrain
from hunter_pkg import ui_panel
from hunter_pkg import vision_map as vsmap


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Engine:
    def __init__(self, intelligent_entities, static_entities, input_handler, game_map):
        self.settings = stats.Stats.map()["settings"]
        self.game_speed = self.settings["game-speed"]
        self.game_time = self.settings["game-time"]["initial"]
        self.intelligent_entities = intelligent_entities
        self.static_entities = static_entities
        self.input_handler = input_handler
        self.game_map = game_map
        self.event_queue = deque()
        self.hunter = None
        self.camp = None
        self.hovered_tile = None
        self.time_of_day = tod.MORNING # init this to morning for now
        self.days_elapsed = 1

    def handle_inputs(self, inputs: Iterable[Any]) -> None:
        for input in inputs:
            action = self.input_handler.dispatch(input)

            if action is None:
                continue

            action.perform(self)

    def init_event_queue(self, entities):
        for entity in entities:
            self.event_queue.append(ev.Event(entity))

        self.event_queue = deque(sorted(self.event_queue))

    def advance_game_time(self):
        prev_time = self.game_time
        prev_time_of_day = self.get_time_of_day(prev_time)
        factor = self.settings["game-time"]["factors"][prev_time_of_day]
        new_time = self.game_time + (factor * self.game_speed)
        new_time_of_day = self.time_of_day = self.get_time_of_day(new_time)

        if new_time_of_day != prev_time_of_day:
            flog.debug(f"it's now {new_time_of_day}")
            self.game_map.redraw_all_transition()

        if math.get_decimal(new_time) >= self.settings["game-time"]["thresholds"]["max"]:
            flog.debug("it's a new day!")
            self.days_elapsed += 1

            if self.hunter.alive:
                self.hunter.days_survived += 1

        self.game_time = math.round_game_time(new_time)
    
    def get_time_of_day(self, full_time):
        day_time = full_time - floor(full_time)

        if day_time > self.settings["game-time"]["thresholds"]["night"]:
            return tod.NIGHT
        elif day_time > self.settings["game-time"]["thresholds"]["evening"]:
            return tod.EVENING
        elif day_time > self.settings["game-time"]["thresholds"]["afternoon"]:
            return tod.AFTERNOON
        elif day_time > self.settings["game-time"]["thresholds"]["morning"]:
            return tod.MORNING
        else:
            return tod.NIGHT

    def process_events(self):
        flog.debug(f"event_queue len: {len(self.event_queue)}")
        while(len(self.event_queue) > 0):
            event = self.event_queue[0]

            if event.time < self.game_time:
                event.process()
                self.event_queue.popleft()
                if event.entity.requeue():
                    insort(self.event_queue, ev.Event(event.entity))
            else:
                break

    def spawn_entities(self):
        intelligent_entities = []
        static_entities = []

        # wolf = wlf.Wolf(self, 20, 20)
        # self.game_map.tiles[20][20].entities.append(wolf)
        # intelligent_entities.append(wolf)

        for y, row in enumerate(self.game_map.tiles):
            for x, tile in enumerate(row):
                if tile.terrain.walkable:
                    if rng.rand() < stats.Stats.map()["rabbit"]["spawn"]:
                        burrow = rbt.Burrow(x, y)
                        rabbit = rbt.Rabbit(self, x, y)
                        rabbit.burrow = burrow
                        self.game_map.tiles[y][x].add_entities([burrow, rabbit])
                        intelligent_entities.append(rabbit)
                    if rng.rand() < stats.Stats.map()["wolf"]["spawn"]:
                        wolf = wlf.Wolf(self, x, y)
                        self.game_map.tiles[y][x].entities.append(wolf)
                        intelligent_entities.append(wolf)
                if isinstance(tile.terrain, terrain.Grass) or isinstance(tile.terrain, terrain.Forest):
                    if rng.rand() < stats.Stats.map()["berry-bush"]["spawn"]:
                        berry_bush = bb.BerryBush(self, x, y)
                        self.game_map.tiles[y][x].entities.append(berry_bush)
                        static_entities.append(berry_bush)

        return intelligent_entities, static_entities

    def init_stats_panel(self):
        margin = 2
        self.stats_panel = ui_panel.StatsPanel(x=1, y=1, height=self.game_map.height - margin, width=17, engine=self)

    def init_action_log_panel(self):
        x = 20
        height = 13
        margin = 2
        self.action_log_panel = ui_panel.ActionLogPanel(x=x, y=self.game_map.height - height - 1, height=height, width=self.game_map.width - x - margin, engine=self)

    # TODO dedup this (duplicated in hunter.py)
    def init_fog_reveal(self):
        vd = self.hunter.vision_distance[self.time_of_day]
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

    def find_hunter_spawn_point(self):
        camp_x_min = round(self.game_map.width * 0.25)
        camp_x_max = round(self.game_map.width * 0.75)
        camp_y_min = round(self.game_map.height * 0.25)
        camp_y_max = round(self.game_map.height * 0.75)
        found = False

        # TODO make this smarter
        while(not found):
            x = rng.range_int(camp_x_min, camp_x_max)
            y = rng.range_int(camp_y_min, camp_y_max)

            if self.game_map.tiles[y][x].terrain.walkable:
                return [x, y]

    def render(self, console: Console, context: Context) -> None:
        self.game_map.progress_redraw_all_transition()
        self.game_map.render(console, self.time_of_day)

        for entity in self.intelligent_entities:
            if self.game_map.tiles[entity.y][entity.x].explored or not self.settings["show-fog"]:
                if (isinstance(entity, rbt.Rabbit) and not entity.asleep) or not isinstance(entity, rbt.Rabbit):
                    console.print(entity.x, entity.y, entity.char, fg=entity.color, bg=entity.bg_color)

        if self.settings["show-ui"]:
            self.stats_panel.render(console)
            self.action_log_panel.render(console)

        context.present(console)
