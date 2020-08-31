#!/usr/bin/env python3

from bisect import insort
import sys
import time
import tcod

from hunter_pkg.entities import hunter as htr

from hunter_pkg import colors
from hunter_pkg import engine as eng
from hunter_pkg import event
from hunter_pkg import flogging
from hunter_pkg import game_map as gm
from hunter_pkg import input_handlers
from hunter_pkg import stats


flog = flogging.Flogging.get(__file__, flogging.INFO)

def main() -> None:
    stats.Stats.map(sys.argv[1])
    seconds_per_frame = 0.016
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "resources/img/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    input_handler = input_handlers.InputHandler()
    game_map = gm.GameMap(map_width, map_height)
    engine = eng.Engine(intelligent_entities=[], static_entities=[], input_handler=input_handler, game_map=game_map)

    hunter = htr.Hunter(engine, int(map_width / 2) - 5, int(map_height / 2) - 5)
    engine.intelligent_entities, engine.static_entities = engine.spawn_entities()
    engine.hunter = hunter
    engine.intelligent_entities.append(hunter)
    
    for row in game_map.tiles:
        for tile in row:
            for e in tile.entities:
                insort(engine.event_queue, event.Event(e))

    engine.init_stats_panel()

    # this is weird
    engine.init_event_queue(engine.intelligent_entities)
    engine.init_event_queue(engine.static_entities)

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
