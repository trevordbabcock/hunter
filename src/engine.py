from bisect import insort
from collections import deque
from time import time
from typing import Set, Iterable, Any

import numpy.random as nprand
from tcod.context import Context
from tcod.console import Console

import colors
import entity
from event import Event
from game_map import GameMap
from input_handlers import InputHandler
import terrain


class Engine:
    def __init__(self, intelligent_entities: Set[entity.Entity], static_entities, input_handler: InputHandler, game_map: GameMap, hunter: entity.Entity):
        self.game_speed = 1.0
        self.intelligent_entities = intelligent_entities
        self.static_entities = static_entities
        self.input_handler = input_handler
        self.game_map = game_map
        self.event_queue = deque()
        self.hunter = hunter

    def handle_inputs(self, inputs: Iterable[Any]) -> None:
        for input in inputs:
            action = self.input_handler.dispatch(input)

            if action is None:
                continue

            action.perform(self.hunter) # shouldnt need to do this anymore

    def init_event_queue(self, entities):
        for entity in entities:
            self.event_queue.append(Event(entity))

        self.event_queue = deque(sorted(self.event_queue))

    def process_events(self):
        while(len(self.event_queue) > 0):
            event = self.event_queue[0]

            if event.time < time():
                event.process()
                self.event_queue.popleft()
                if event.entity.requeue():
                    insort(self.event_queue, Event(event.entity))
            else:
                break

    def spawn_entities(self):
        entities = []

        for y, row in enumerate(self.game_map.tiles):
            for x, tile in enumerate(row):
                if tile.terrain.walkable:
                    if nprand.randint(100) < 1:
                        entities.append(entity.Rabbit(self, x, y))
                if isinstance(tile.terrain, terrain.Ground) or isinstance(tile.terrain, terrain.Forest):
                    if nprand.randint(100) < 1:
                        berry_bush = entity.BerryBush(self)
                        self.game_map.tiles[y][x].entities.append(berry_bush)

        return entities

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        for entity in self.intelligent_entities:
            console.print(entity.x, entity.y, entity.char, fg=entity.color, bg=entity.bg_color)

        #console.print(self.hunter.x, self.hunter.y, self.player.char, fg=self.player.color, bg=self.player.bg_color)
        context.present(console)
        console.clear()
