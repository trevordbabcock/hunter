from __future__ import annotations

from math import floor

from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder
from hunter_pkg import ui_panel as ui


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class PlayerAction:
    def perform(self, engine):
        raise NotImplementedError()


class EscapePlayerAction(PlayerAction):
    def perform(self, engine):
        panel = engine.game_menu_panel
        panel.hidden = not panel.hidden

        if panel.hidden:
            x1 = panel.x - 1
            y1 = panel.y - 1
            x2 = panel.x + panel.width - 1
            y2 = panel.y + panel.height - 1
            engine.game_map.redraw_tiles([x1, y1], [x2, y2])
            engine.ui_collision_layer.delete_all_hitboxes()


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
                engine.game_map.redraw_tile(prev_tile.x, prev_tile.y)

            curr_tile.hovered = True
            engine.game_map.redraw_tile(curr_tile.x, curr_tile.y)
            engine.hovered_tile = curr_tile
            engine.stats_panel.tile = curr_tile

        hovered_element = engine.ui_collision_layer.tiles[self.y][self.x]
        if hovered_element != None:
            flog.debug(f"hit {hovered_element} on ({self.x},{self.y})")
            engine.hovered_ui_element = hovered_element
        else:
            engine.hovered_ui_element = None


class MouseUpPlayerAction(PlayerAction):
    def perform(self, engine):
        if engine.hovered_ui_element and isinstance(engine.hovered_ui_element, ui.UIButton) and engine.hovered_ui_element.id == "exit_btn":
            raise SystemExit


class ToggleVisionPlayerAction(PlayerAction):
    def perform(self, engine):
        if engine.game_map.next_redraw_column == None:
            new_setting = not engine.settings["show-fog"]
            engine.settings["show-fog"] = new_setting
            engine.game_map.show_fog = new_setting        
            engine.game_map.redraw_all_transition()


class ToggleUIPlayerAction(PlayerAction):
    def perform(self, engine):
        engine.settings["show-ui"] = not engine.settings["show-ui"]
        engine.game_map.redraw_all()
        