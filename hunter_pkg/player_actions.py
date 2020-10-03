from __future__ import annotations

from math import floor

from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class PlayerAction:
    def perform(self, engine):
        raise NotImplementedError()


class EscapePlayerAction(PlayerAction):
    def perform(self, engine):
        raise SystemExit()


class MouseMovementPlayerAction(PlayerAction):
    def __init__(self, px_x, px_y):
        self.x = floor(px_x/10)
        self.y = floor(px_y/10)

    def perform(self, engine):
        prev_tile = engine.hovered_tile
        curr_tile = engine.game_map.tiles[self.y][self.x]

        if curr_tile != prev_tile:
            if prev_tile != None:
                prev_tile.hovered = False

            curr_tile.hovered = True
            engine.hovered_tile = curr_tile
            engine.stats_panel.tile = curr_tile


class ToggleVisionPlayerAction(PlayerAction):
    def perform(self, engine):
        new_setting = not engine.settings["show-fog"]
        engine.settings["show-fog"] = new_setting
        engine.game_map.show_fog = new_setting


class ToggleUIPlayerAction(PlayerAction):
    def perform(self, engine):
        engine.settings["show-ui"] = not engine.settings["show-ui"]
        