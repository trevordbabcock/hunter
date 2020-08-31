from bisect import insort
from collections import deque
from time import time
from typing import Set, Iterable, Any

import numpy.random as nprand
from tcod.context import Context
from tcod.console import Console


from hunter_pkg.entities import rabbit as rbt
from hunter_pkg.entities import berry_bush as bb

from hunter_pkg import colors
from hunter_pkg import event as ev
from hunter_pkg import flogging
from hunter_pkg import game_map
from hunter_pkg import input_handlers
from hunter_pkg import log_level
from hunter_pkg import stats
from hunter_pkg import terrain
from hunter_pkg import ui_panel


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Engine:
    def __init__(self, intelligent_entities, static_entities, input_handler, game_map):
        self.game_speed = 1.0
        self.intelligent_entities = intelligent_entities
        self.static_entities = static_entities
        self.input_handler = input_handler
        self.game_map = game_map
        self.event_queue = deque()
        self.hunter = None
        self.hovered_tile = None

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

    def process_events(self):
        while(len(self.event_queue) > 0):
            event = self.event_queue[0]

            if event.time < time():
                event.process()
                self.event_queue.popleft()
                if event.entity.requeue():
                    insort(self.event_queue, ev.Event(event.entity))
            else:
                break

    def spawn_entities(self):
        intelligent_entities = []
        static_entities = []

        for y, row in enumerate(self.game_map.tiles):
            for x, tile in enumerate(row):
                if tile.terrain.walkable:
                    if nprand.rand() < stats.Stats.map()["rabbit"]["spawn"]:
                        rabbit = rbt.Rabbit(self, x, y)
                        self.game_map.tiles[y][x].entities.append(rabbit)
                        intelligent_entities.append(rabbit)
                if isinstance(tile.terrain, terrain.Grass) or isinstance(tile.terrain, terrain.Forest):
                    if nprand.rand() < stats.Stats.map()["berry-bush"]["spawn"]:
                        berry_bush = bb.BerryBush(self, x, y)
                        self.game_map.tiles[y][x].entities.append(berry_bush)
                        static_entities.append(berry_bush)

        return intelligent_entities, static_entities

    def init_stats_panel(self):
        self.stats_panel = ui_panel.UIPanel(1, 1, 48, 17, self)

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        for entity in self.intelligent_entities:
            console.print(entity.x, entity.y, entity.char, fg=entity.color, bg=entity.bg_color)

        # TODO make this hideable
        if True:
            self.stats_panel.render(console)

        #console.print(self.hunter.x, self.hunter.y, self.player.char, fg=self.player.color, bg=self.player.bg_color)
        context.present(console)
        console.clear()
