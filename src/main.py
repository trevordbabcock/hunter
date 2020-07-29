#!/usr/bin/env python3
import time
import tcod

import colors
from engine import Engine
import entity
from game_map import GameMap
from input_handlers import EventHandler


def main() -> None:
    seconds_per_frame = 0.016
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "resources/img/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    player = entity.Hunter(int(map_width / 2), int(map_height / 2))
    rabbit = entity.Rabbit(int(map_width / 2) - 2, int(map_height / 2) - 2)
    entities = {player, rabbit}

    game_map = GameMap(map_width, map_height)

    engine = Engine(entities=entities, event_handler=event_handler, game_map=game_map, player=player)

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
            
            events = tcod.event.get()
            engine.handle_events(events)
            engine.perform_ai()
            engine.render(console=root_console, context=context)

            previous = current
            current = time.time()
            elapsed_time = current - previous
            sleep_time = seconds_per_frame - elapsed_time
            # print("elapsed_time: {}".format(elapsed_time))
            # print("sleep time: {}".format(sleep_time))
            if(sleep_time < 0):
                sleep_time = 0
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()
