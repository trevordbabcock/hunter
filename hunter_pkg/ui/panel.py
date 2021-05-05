from math import floor

from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import camp as cp
from hunter_pkg.entities import deer as dr
from hunter_pkg.entities import hunter as htr
from hunter_pkg.entities import rabbit as rbt
from hunter_pkg.entities import wolf as wlf

from hunter_pkg.helpers import coord
from hunter_pkg.helpers import generic as gen
from hunter_pkg.helpers import math

from hunter_pkg.ui import element as ui_elem

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level

flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))


class Panel():
    def __init__(self, x, y, height, width, engine):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.engine = engine
        self.color = colors.dark_gray()

        self.top_left_coord = coord.Coord(self.x - 1, self.y - 1)
        self.bottom_right_coord = coord.Coord(self.x + self.width - 1, self.y + self.height - 1)

    def render(self, console):
        pass

    def base_render(self, console, elements, x, y, width):
        for i in range(len(elements)):
            element_y = y + self.get_cumulative_elements_height(elements, i)
            elements[i].render(console, x, element_y, width, ".")

    def get_cumulative_elements_height(self, elements, i):
        height = 0
        for j in range(len(elements[0:i])):
            if gen.has_member(elements[j], 'height'):
                height += elements[j].height
            else:
                height += 1

        return height

    def pad_elements_with_breaks(self, elements, height):
        for i in range(height - len(elements)):
            elements.append(ui_elem.Break())

        return elements
    
    def truncate_elements(self, elements, n=1):
        return elements[0:self.height-n]

    def create_hitboxes(self, elements):
        for i in range(len(elements)):
            e = elements[i]

            if(isinstance(e, ui_elem.Button) or isinstance(e, ui_elem.TextOnlyButton)):
                x = self.x + floor((self.width - e.width)/2)
                y = self.y + self.get_cumulative_elements_height(elements, i)

                e.x = x
                e.y = y

                self.engine.ui_collision_layer.create_hitbox(e, coord.Coord(e.x, e.y), coord.Coord(e.x + e.width, e.y + e.height))

    def show(self):
        self.hidden = False

    def hide(self):
        self.hidden = True
        self.engine.game_map.redraw_tiles(self.top_left_coord, self.bottom_right_coord)
        self.engine.ui_collision_layer.delete_all_hitboxes()


class StatsPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)

    def format_game_time(self, game_time):
        """
        Format game_time from int to str.
        Example: 20900 to "20:50"
        """
        day_time = math.get_decimal(game_time)
        time_str = "{:04.0f}".format(day_time * 10000)
        # this converts hour subdivisions from 100 to 60 (minutes)
        converted_minute_int = floor(int(time_str[2] + time_str[3])/100 * 60)
        minute_str = str(converted_minute_int)
        return "".join([time_str[0], time_str[1], ":", minute_str.zfill(2)])

    def render(self, console):
        console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

        elements = [
            ui_elem.HeaderFooter(),
            ui_elem.CenteredText(f"Day {self.engine.days_elapsed}"),
            ui_elem.CenteredText(self.engine.time_of_day.capitalize()),
            ui_elem.CenteredText(f"{self.format_game_time(self.engine.game_time)}"),
            ui_elem.Break(),
            ui_elem.Text(f"{self.engine.hunter.human_name}"),
            ui_elem.Text("The Hunter"),
            ui_elem.Break(),
            ui_elem.Text(f"Surv {self.engine.hunter.days_survived} days"),
            ui_elem.Break(),
            ui_elem.Text("Hlth {:02.0f}/{}".format(self.engine.hunter.curr_health, self.engine.hunter.max_health)),
            ui_elem.Text("Hngr {:02.0f}/{}".format(self.engine.hunter.curr_hunger, self.engine.hunter.max_hunger)),
            ui_elem.Text("Nrgy {:02.0f}/{}".format(self.engine.hunter.curr_energy, self.engine.hunter.max_energy)),
            ui_elem.Break(),
            ui_elem.Divider(),
            ui_elem.Divider(),
        ]
        
        self.base_render(console, elements, self.x, self.y, self.width)


class HoverPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)
        self.tile = None

    def render(self, console):
        console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

        elements = []

        if self.tile != None:
            if self.tile.explored or not self.engine.settings["show-fog"]:
                elements.extend([
                    ui_elem.Break(),
                    ui_elem.Text("Tile"),
                    ui_elem.Text("Coord: ({:02.0f},{:02.0f})".format(self.tile.x, self.tile.y)),
                    ui_elem.Text("Trrn: {}".format(self.tile.terrain.__class__.__name__)),
                ])

                if len(self.tile.entities) == 0:
                    elements.append(ui_elem.Text("Entities: None"))
                else:
                    elements.append(ui_elem.Text("Entities:"))

                    for entity in self.tile.entities:
                        if isinstance(entity, htr.Hunter):
                            elements.append(ui_elem.Text("~Hntr"))
                        elif isinstance(entity, rbt.Rabbit):
                            elements.append(ui_elem.Text("~Rbbt"))
                        elif isinstance(entity, wlf.Wolf):
                            elements.append(ui_elem.Text("~Wolf"))
                        elif isinstance(entity, rbt.Burrow):
                            elements.append(ui_elem.Text("~Brrw"))
                        elif isinstance(entity, bb.BerryBush):
                            elements.extend([
                                ui_elem.Text("~BrryBsh"),
                                ui_elem.Text(f" ~Berries: {entity.num_berries}"),
                            ])
                        elif isinstance(entity, cp.Camp):
                            elements.append(ui_elem.Text("~Camp"))
                            for component in entity.components:
                                elements.append(ui_elem.Text(f" ~{component.name()}"))
            else:
                elements.extend([
                    ui_elem.Break(),
                    ui_elem.Text("???"),
                ])
        
        elements = self.pad_elements_with_breaks(elements, self.height)
        elements = self.truncate_elements(elements, 2)
        elements.append(ui_elem.Divider())
        elements.append(ui_elem.Divider())

        self.base_render(console, elements, self.x, self.y, self.width)


class SelectionPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)
    
    def render(self, console):
        console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

        elements = []

        if self.engine.selected_entity != None:
            if hasattr(self.engine.selected_entity, "selection_info"):
                elements.extend([
                    ui_elem.Break(),
                    ui_elem.Text("Selected:"),
                ])

                for info in self.engine.selected_entity.selection_info():
                    if isinstance(info, str):
                        elements.append(ui_elem.PaddedText(info, 1))
                    elif isinstance(info, dict):
                        for key, val in info.items():
                            elements.append(ui_elem.PaddedText(key, 1))

                            if isinstance(val, list):
                                for subval in val:
                                    elements.append(ui_elem.PaddedText("~" + subval, 2))
            elif hasattr(self.engine.selected_entity, "name"):
                elements.extend([
                    ui_elem.Break(),
                    ui_elem.Text("Selected:"),
                    ui_elem.PaddedText(self.engine.selected_entity.name, 1),
                ])
            else:
                elements.extend([
                    ui_elem.Break(),
                    ui_elem.Text("Selected:"),
                    ui_elem.Text("None"),
                ])
        else:
            elements.extend([
                ui_elem.Break(),
                ui_elem.Text("Selected:"),
                ui_elem.Text("None"),
            ])
        
        elements = self.pad_elements_with_breaks(elements, self.height)
        elements = self.truncate_elements(elements)
        elements.append(ui_elem.HeaderFooter())

        self.base_render(console, elements, self.x, self.y, self.width)


class ActionLogPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)
        self.tile = None

    def render(self, console):
        elements = []

        console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

        action_log_target = self.engine.selected_entity

        if action_log_target == None or not gen.has_member(action_log_target, "recent_actions"):
            action_log_target = self.engine.hunter

        elements.extend([
            ui_elem.HeaderFooter(),
            ui_elem.Break(),
            ui_elem.Text(f"{action_log_target.entity_name} Action Log:"),
        ])

        num_actions_possible = self.height - 5
        recent_actions_subset = action_log_target.recent_actions[-num_actions_possible:]

        for action in recent_actions_subset:
            elements.append(ui_elem.PaddedText(action, 1))

        elements = self.pad_elements_with_breaks(elements, self.height)
        elements = self.truncate_elements(elements)
        elements.append(ui_elem.HeaderFooter())

        self.base_render(console, elements, self.x, self.y, self.width)


class GameMenuPanel(Panel):
    def __init__(self, x, y, height, width, button_width, engine):
        super().__init__(x, y, height, width, engine)
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.button_width = button_width
        self.engine = engine
        self.hidden = True

    def render(self, console):
        if not self.hidden:
            console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

            elements = [
                ui_elem.HeaderFooter(),
                ui_elem.Break(3),
                ui_elem.Button("open_ctrls_btn", "Controls", self.button_width, self.width, self.engine),
                ui_elem.Break(1),
                ui_elem.Button("save_btn", "Save Game", self.button_width, self.width, self.engine),
                ui_elem.Break(1),
                ui_elem.Button("load_btn", "Load Game", self.button_width, self.width, self.engine),
                ui_elem.Break(1),
                ui_elem.Button("exit_btn", "Exit", self.button_width, self.width, self.engine),
                ui_elem.Break(3),
                ui_elem.HeaderFooter()
            ]

            self.base_render(console, elements, self.x, self.y, self.width)
            self.create_hitboxes(elements) # TODO could maybe use decorator here


class ControlsPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.engine = engine
        self.hidden = True

    def render(self, console):
        if not self.hidden:
            console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

            elements = [
                ui_elem.HeaderFooter(),
                ui_elem.Break(3),
                ui_elem.Text("   Esc: show escape menu"),
                ui_elem.Text("     F: show/hide fog of war"),
                ui_elem.Text("     H: show/hide UI"),
                ui_elem.Text("     E: show/hide entity panel"),
                ui_elem.Text(" Spc/P: pause game"),
                ui_elem.Break(2),
                ui_elem.Button("close_ctrls_btn", "Close", 13, self.width, self.engine),
                ui_elem.Break(2),
                ui_elem.HeaderFooter(),
            ]

            self.base_render(console, elements, self.x, self.y, self.width)
            self.create_hitboxes(elements)


class EntityOverviewPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.engine = engine
        self.hidden = False

    def render(self, console):
        if not self.hidden:
            console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

            counts = self.engine.get_entity_counts()
            key = "entity-visibility"
            
            elements = [
                ui_elem.HeaderFooter(),
                ui_elem.CenteredText(f"Entities"),
                ui_elem.CenteredText(f"Show / Hide"),
                ui_elem.Break(2),
                ui_elem.ToggleableTextOnlyButton("entity-hunter-btn", f" {counts[htr.Hunter]} Hunter", self.engine, key),
                ui_elem.ToggleableTextOnlyButton("entity-rabbit-btn", f" {counts[rbt.Rabbit]} Rabbits", self.engine, key),
                ui_elem.ToggleableTextOnlyButton("entity-wolf-btn", f" {counts[wlf.Wolf]}  Wolves", self.engine, key),
                ui_elem.ToggleableTextOnlyButton("entity-deer-btn", f" {counts[dr.Deer]}  Deer", self.engine, key),
                ui_elem.ToggleableTextOnlyButton("entity-berry-bush-btn", f" {counts[bb.BerryBush]} Berry Bushes", self.engine, key),
            ]

            elements = self.pad_elements_with_breaks(elements, self.height)
            elements = self.truncate_elements(elements)
            elements.append(ui_elem.HeaderFooter())

            self.base_render(console, elements, self.x, self.y, self.width)
            self.create_hitboxes(elements)
