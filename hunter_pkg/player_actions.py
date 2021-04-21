from __future__ import annotations

from math import floor

from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder

from hunter_pkg.helpers import coord
from hunter_pkg.helpers import generic as gen

from hunter_pkg.ui import element as ui_elem


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class PlayerAction:
    def perform(self, engine):
        raise NotImplementedError()


class EscapePlayerAction(PlayerAction):
    def perform(self, engine):
        if engine.settings["show-ui"]:
            if not engine.controls_panel.hidden:
                engine.controls_panel.hide()
            elif engine.game_menu_panel.hidden:
                engine.game_menu_panel.show()
            else:
                engine.game_menu_panel.hide()
        else:
            engine.settings["show-ui"] = True
            engine.game_map.redraw_all()


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
            engine.hover_panel.tile = curr_tile

        hovered_element = engine.ui_collision_layer.tiles[self.y][self.x]
        if hovered_element != None:
            flog.debug(f"hit {hovered_element.id} on ({self.x},{self.y})")
            engine.hovered_ui_element = hovered_element
        else:
            engine.hovered_ui_element = None


class MouseUpPlayerAction(PlayerAction):
    def perform(self, engine):
        if engine.hovered_ui_element != None:
            if isinstance(engine.hovered_ui_element, ui_elem.Button):
                if engine.hovered_ui_element.id == "exit_btn":
                    raise SystemExit
                elif engine.hovered_ui_element.id == "open_ctrls_btn":
                    engine.game_menu_panel.hide()
                    engine.controls_panel.show()
                elif engine.hovered_ui_element.id == "close_ctrls_btn":
                    engine.controls_panel.hide()
            elif isinstance(engine.hovered_ui_element, ui_elem.TextOnlyButton):
                if gen.has_method(engine.hovered_ui_element, "toggle"):
                    engine.hovered_ui_element.toggle()

                    if engine.hovered_ui_element.id in ["entity-hunter-btn", "entity-rabbit-btn", "entity-wolf-btn", "entity-berry-bush-btn"]:
                        # if engine.selected_entity:
                        #     engine.selected_entity.deselect()
                        #     engine.selected_entity = None
                        
                        engine.game_map.redraw_all()

                        
        elif engine.hovered_tile:
            engine.hovered_tile.select_next_entity(engine)


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


class ToggleEntityOverviewAction(PlayerAction):
    def perform(self, engine):
        engine.settings["show-entity-overview"] = not engine.settings["show-entity-overview"]
        engine.game_map.redraw_all()


class TogglePausePlayerAction(PlayerAction):
    def perform(self, engine):
        engine.paused = not engine.paused
        