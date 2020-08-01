from bisect import insort
from collections import deque
from time import time
from typing import Set, Iterable, Any

from numpy.random import randint
from tcod.context import Context
from tcod.console import Console

from entity import Entity, IntelligentEntity, Rabbit
from event import Event
from game_map import GameMap
from input_handlers import InputHandler


class Engine:
    def __init__(self, entities: Set[Entity], input_handler: InputHandler, game_map: GameMap, player: Entity):
        self.entities = entities
        self.input_handler = input_handler
        self.game_map = game_map
        self.event_queue = deque()
        self.player = player

    def handle_inputs(self, inputs: Iterable[Any]) -> None:
        for input in inputs:
            action = self.input_handler.dispatch(input)

            if action is None:
                continue

            action.perform(self, self.player)

    def init_event_queue(self, entities):
        for entity in entities:
            self.event_queue.append(Event(entity))

        sorted(self.event_queue)

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
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                if self.game_map.tiles["walkable"][x, y]:
                    if randint(100) < 1:
                        entities.append(Rabbit(self, x, y))

        return entities

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        for entity in self.entities:
            console.print(entity.x, entity.y, entity.char, fg=entity.color, bg=entity.bg_color)

        console.print(self.player.x, self.player.y, self.player.char, fg=self.player.color, bg=self.player.bg_color)

        context.present(console)

        console.clear()
