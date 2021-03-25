from math import floor, ceil

from hunter_pkg.entities import berry_bush as bb
from hunter_pkg.entities import camp as cp
from hunter_pkg.entities import hunter as htr
from hunter_pkg.entities import rabbit as rbt
from hunter_pkg.entities import wolf as wlf

from hunter_pkg.helpers import coord
from hunter_pkg.helpers import math

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class UIPanel():
    def __init__(self, x, y, height, width, engine):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.engine = engine
        self.color = colors.dark_gray()
    
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
            WindowTextLine(lines[i], width).render(console, x, line_y, ".")

    def pad_window_text_lines(self, lines, height):
        for i in range(height - len(lines)):
            lines.append("")

        return lines


class StatsPanel(UIPanel):
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


class ActionLogPanel(UIPanel):
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


class GameMenuPanel(UIPanel):
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
                UIHeaderFooter(self.width),
                UIBreak(3),
                UIButton("controls_btn", "Controls", 17, self.width, self.engine),
                UIBreak(1),
                UIButton("save_btn", "Save Game", 17, self.width, self.engine),
                UIBreak(1),
                UIButton("load_btn", "Load Game", 17, self.width, self.engine),
                UIBreak(1),
                UIButton("exit_btn", "Exit", 17, self.width, self.engine),
                UIBreak(3),
                UIHeaderFooter(self.width)
            ]

            lines = self.render_elements(elements)
            self.render_window_text_lines(console, lines, self.x, self.y, self.width)

    def render_elements(self, elements):
        lines = []

        for e in elements:
            rendered = e.render()

            if(isinstance(e, UIButton)):
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


class WindowTextLine():
    def __init__(self, text, width, color=colors.white()):
        self.text = self.format_text(text, width, width - 2)
        self.color = color

    def format_text(self, text, width, borderless_width):
        if len(text) <= (borderless_width):
            text = text.ljust(borderless_width, " ")
        else:
            text = text[0:borderless_width]

        return text

    def render(self, console, x, y, border, button=None):
        console.print(x, y, border + self.text + border, self.color)


class UIHeaderFooter():
    def __init__(self, width):
        self.width = width

    def render(self):
        chars = []

        for i in range(self.width):
            if (i % 2) == 0:
                chars.append("-")
            else:
                chars.append(".")

        return "".join(chars)


class UIBreak():
    def __init__(self, num=1):
        self.num = num

    def render(self):
        lines = []

        for n in range(self.num):
            lines.append("")

        return lines


class UIButton():
    def __init__(self, id, text, width, panel_width, engine):
        self.id = id
        self.text = text
        self.width = width
        self.panel_width  = panel_width
        self.engine = engine
        self.height = 4
        self.hovered = False

        self.hovered_appearance = [
            self.header_footer(self.width),
            self.hoverify(self.middle(self.width)),
            self.hoverify(self.middle_text(self.width, text)),
            self.header_footer(self.width),
        ]
        self.appearance = [
            self.header_footer(self.width),
            self.middle(self.width),
            self.middle_text(self.width, text),
            self.header_footer(self.width),
        ]

    def center_line(self, width, line):
        return " " * floor((width - 2 - len(line))/2) + line

    def header_footer(self, width):
        return "-" * (width - 2)

    def middle(self, width):
        return "|" + (" " * (width - 2)) + "|"

    def middle_text(self, width, text):
        left = True
        while(len(text) < width-2):
            if left:
                text = " " + text
                left = False
            else: #right
                text = text + " "
                left = True

        return "|" + text + "|"
    
    def hoverify(self, middle):
        return "|" + middle + "|"

    def render(self):
        lines = []

        if self.is_hovered():
            lines.extend(self.hovered_appearance)
        else:
            lines.extend(self.appearance)

        for i in range(len(lines)):
            lines[i] = self.center_line(self.panel_width , lines[i])

        return lines

    def is_hovered(self):
        return self.engine.hovered_ui_element != None and self.id == self.engine.hovered_ui_element.id


class UICollisionLayer():
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.tiles = self.init_tiles(height, width)

    def init_tiles(self, height, width):
        tiles = []

        for y in range(height):
            tiles.append([])

            for x in range(width):
                tiles[y].append(None)

        return tiles

    def create_hitbox(self, hittable, top_left_coord, bottom_right_coord):
        for y in range(top_left_coord.y, bottom_right_coord.y + 1):
            for x in range(top_left_coord.x, bottom_right_coord.x + 1):
                self.tiles[y][x] = hittable

    # def delete_hitbox(self, hittable, top_left_coord, bottom_right_coord):
    #     hitbox_height = bottom_right_coord.y - top_left_coord.y
    #     hitbox_width = bottom_right_coord.x - top_left_coord.x

    #     for y in range(hitbox_height):
    #         for x in range(hitbox_width):
    #             self.tiles[y][x] = None

    def delete_all_hitboxes(self):
        self.tiles = self.init_tiles(self.height, self.width)
