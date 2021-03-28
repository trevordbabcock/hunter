from math import floor

from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import camp as cp
from hunter_pkg.entities import hunter as htr
from hunter_pkg.entities import rabbit as rbt
from hunter_pkg.entities import wolf as wlf

from hunter_pkg.helpers import coord
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
    
    def get_header_footer_line(self, width):
        chars = []

        for i in range(width):
            if (i % 2) == 0:
                chars.append("-")
            else:
                chars.append(".")
        
        return "".join(chars)
    
    def get_divider_line(self, width):
        chars = []

        for i in range(width):
            chars.append("-")
        
        return "".join(chars)
    
    def center_line(self, width, line):
        return " " * floor((width - 2 - len(line))/2) + line

    def render(self, console):
        pass

    def render_window_text_lines(self, console, lines, x, y, width):
        for i in range(len(lines)):
            line_y = i + y
            ui_elem.WindowTextLine(lines[i], width).render(console, x, line_y, ".")

    def render_elements(self, elements):
        lines = []

        for e in elements:
            if(isinstance(e, str)):
                lines.append(e)
            else:
                rendered = e.render()

                if(isinstance(e, ui_elem.Button)):
                    # calculate button x and y since this is the only opportunity
                    x = self.x + floor((self.width - 2 - e.width)/2) + 1
                    y = self.y + len(lines)

                    e.x = x
                    e.y = y

                    self.engine.ui_collision_layer.create_hitbox(e, coord.Coord(e.x, e.y), coord.Coord(e.x + e.width, e.y + e.height))

                if(isinstance(rendered, list)):
                    lines.extend(rendered)
                else:
                    lines.append(rendered)

        return lines

    def pad_window_text_lines(self, lines, height):
        for i in range(height - len(lines)):
            lines.append("")

        return lines

    def show(self):
        self.hidden = False

    def hide(self):
        self.hidden = True
        self.engine.game_map.redraw_tiles(self.top_left_coord, self.bottom_right_coord)
        self.engine.ui_collision_layer.delete_all_hitboxes()


class StatsPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)
        self.tile = None

    def format_game_time(self, game_time):
        """
        Format game_time from int to str.
        Example: 20900 to "20:50"
        """
        day_time = math.get_decimal(game_time)
        time_str = "{:04.0f}".format(day_time*10000)
        # this converts hour subdivisions from 100 to 60 (minutes)
        converted_minute_int = floor(int(time_str[2] + time_str[3])/100 * 60)
        minute_str = str(converted_minute_int)
        return "".join([time_str[0], time_str[1], ":", minute_str.zfill(2)])

    def render(self, console):
        console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

        lines = [
            self.get_header_footer_line(self.width),
            self.center_line(self.width, f"Day {self.engine.days_elapsed}"),
            self.center_line(self.width, self.engine.time_of_day.capitalize()),
            self.center_line(self.width, f"{self.format_game_time(self.engine.game_time)}"),
            "",
            f"{self.engine.hunter.name}",
            "The Hunter",
            "",
            f"Surv {self.engine.hunter.days_survived} days",
            ""
            "Hlth {:02.0f}/{}".format(self.engine.hunter.curr_health, self.engine.hunter.max_health),
            "Hngr {:02.0f}/{}".format(self.engine.hunter.curr_hunger, self.engine.hunter.max_hunger),
            "Nrgy {:02.0f}/{}".format(self.engine.hunter.curr_energy, self.engine.hunter.max_energy),
        ]        

        for i in range(12):
            lines.append("")

        lines.append(self.get_divider_line(self.width))
        lines.append(self.get_divider_line(self.width))

        if self.tile != None:
            if self.tile.explored or not self.engine.settings["show-fog"]:
                lines.append(f"")
                lines.append("Tile")
                lines.append("Coord: ({:02.0f},{:02.0f})".format(self.tile.x, self.tile.y))
                lines.append("Trrn: {}".format(self.tile.terrain.__class__.__name__))

                if len(self.tile.entities) == 0:
                    lines.append("Entities: None")
                else:
                    lines.append("Entities:")

                    for entity in self.tile.entities:
                        if isinstance(entity, htr.Hunter):
                            lines.append("~Hntr")
                        elif isinstance(entity, rbt.Rabbit):
                            lines.append("~Rbbt")
                        elif isinstance(entity, wlf.Wolf):
                            lines.append("~Wolf")
                        elif isinstance(entity, rbt.Burrow):
                            lines.append("~Brrw")
                        elif isinstance(entity, bb.BerryBush):
                            lines.append("~BrryBsh")
                            lines.append(f" ~Berries: {entity.num_berries}")
                        elif isinstance(entity, cp.Camp):
                            lines.append("~Camp")
                            for component in entity.components:
                                lines.append(f" ~{component.name()}")
            else:
                lines.append(f"")
                lines.append("???")

        lines = self.pad_window_text_lines(lines, self.height)
        lines = lines[0:self.height-1]
        lines.append(self.get_header_footer_line(self.width))

        self.render_window_text_lines(console, lines, self.x, self.y, self.width)


class ActionLogPanel(Panel):
    def __init__(self, x, y, height, width, engine):
        super().__init__(x, y, height, width, engine)
        self.tile = None

    def render(self, console):
        lines = []

        console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

        lines.append(self.get_header_footer_line(self.width))
        lines.append("")
        lines.append("Hunter Action Log:")

        num_lines_possible = self.height - 5
        recent_actions_subset = self.engine.hunter.recent_actions[-num_lines_possible:]

        for line in recent_actions_subset:
            lines.append("".join([" ", line]))

        lines = self.pad_window_text_lines(lines, self.height) 
        lines = lines[0:self.height-1]
        lines.append(self.get_header_footer_line(self.width))

        self.render_window_text_lines(console, lines, self.x, self.y, self.width)


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
                ui_elem.HeaderFooter(self.width),
                ui_elem.Break(3),
                ui_elem.Button("open_ctrls_btn", "Controls", self.button_width, self.width, self.engine),
                ui_elem.Break(1),
                ui_elem.Button("save_btn", "Save Game", self.button_width, self.width, self.engine),
                ui_elem.Break(1),
                ui_elem.Button("load_btn", "Load Game", self.button_width, self.width, self.engine),
                ui_elem.Break(1),
                ui_elem.Button("exit_btn", "Exit", self.button_width, self.width, self.engine),
                ui_elem.Break(3),
                ui_elem.HeaderFooter(self.width)
            ]

            lines = self.render_elements(elements)
            self.render_window_text_lines(console, lines, self.x, self.y, self.width)


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
                ui_elem.HeaderFooter(self.width),
                ui_elem.Break(3),
                "   Esc: show escape menu",
                "     F: show/hide fog of war",
                "     H: show/hide ",
                " Spc/P: pause game",
                ui_elem.Break(3),
                ui_elem.Button("close_ctrls_btn", "Close", 13, self.width, self.engine),
                ui_elem.Break(2),
                ui_elem.HeaderFooter(self.width)
            ]

            lines = self.render_elements(elements)
            self.render_window_text_lines(console, lines, self.x, self.y, self.width)
