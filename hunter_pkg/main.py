#!/usr/bin/env python3

from bisect import insort
import sys
import time
import tcod

from hunter_pkg.entities import camp as cp
from hunter_pkg.entities import hunter as htr

from hunter_pkg import colors
from hunter_pkg import engine as eng
from hunter_pkg import event
from hunter_pkg import flogging
from hunter_pkg import game_map as gm
from hunter_pkg import input_handlers
from hunter_pkg import log_level
from hunter_pkg import stats


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

def main() -> None:
    stats_file = sys.argv[1] if len(sys.argv) == 2 else "hunter_pkg/config/stats.json"
    stats.Stats.map(stats_file)
    seconds_per_frame = 0.016
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "resources/img/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    input_handler = input_handlers.InputHandler()
    game_map = gm.GameMap(map_width, map_height, stats.Stats.map()["settings"]["show-fog"])
    engine = eng.Engine(intelligent_entities=[], static_entities=[], input_handler=input_handler, game_map=game_map)

    hunter = htr.Hunter(engine, stats.Stats.map()["hunter"]["x-spawn"], stats.Stats.map()["hunter"]["y-spawn"])
    camp = cp.Camp(engine, stats.Stats.map()["hunter"]["camp"]["x-spawn"], stats.Stats.map()["hunter"]["camp"]["y-spawn"])
    game_map.tiles[camp.y][camp.x].entities.append(camp)
    # hard-coding knowledge of camp for now
    hunter.memory.map["camp"] = {
        "x": camp.x,
        "y": camp.y
    }

    engine.intelligent_entities, engine.static_entities = engine.spawn_entities()
    engine.hunter = hunter
    engine.camp = camp
    engine.intelligent_entities.append(hunter)

    engine.init_stats_panel()
    engine.init_action_log_panel()
    engine.init_fog_reveal()

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
            engine.advance_game_time()
            engine.process_events()
            engine.render(console=root_console, context=context)

            previous = current
            current = time.time()
            elapsed_time = current - previous
            sleep_time = seconds_per_frame - elapsed_time
            #flog.debug(elapsed_time)
            #flog.debug(sleep_time)

            if(sleep_time > 0):
                time.sleep(sleep_time)


if __name__ == "__main__":
    main()
