#!/usr/bin/env python3

import time
import tcod

import colors
from engine import Engine
import entity
from game_map import GameMap
from input_handlers import InputHandler


def main() -> None:
    seconds_per_frame = 0.016
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "resources/img/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    input_handler = InputHandler()
    game_map = GameMap(map_width, map_height)
    engine = Engine(intelligent_entities=[], input_handler=input_handler, game_map=game_map, player=None)

    player = entity.Hunter(engine, int(map_width / 2), int(map_height / 2))
    intelligent_entities = engine.spawn_entities()

    engine.player = player
    engine.intelligent_entities = intelligent_entities

    engine.init_event_queue(intelligent_entities)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Hunter",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        while True:
            current = time.time()
            
            inputs = tcod.event.get()
            engine.handle_inputs(inputs)
            engine.process_events()
            engine.render(console=root_console, context=context)

            previous = current
            current = time.time()
            elapsed_time = current - previous
            sleep_time = seconds_per_frame - elapsed_time

            if(sleep_time > 0):
                time.sleep(sleep_time)


if __name__ == "__main__":
    main()
