from hunter_pkg import colors
from hunter_pkg.entities import hunter as htr
from hunter_pkg.entities import rabbit as rbt
from hunter_pkg.entities import berry_bush as bb


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

    def render(self, console):
        console.draw_rect(x=self.x, y=self.y, height=self.height, width=self.width, ch=1, bg=self.color)

        lines = [
            self.get_header_footer_line(self.width),
            "",
            "Entity: Hunter",
            f"Hlth {self.engine.hunter.curr_health}/{self.engine.hunter.max_health}",
            "Hngr {:02.0f}/{}".format(self.engine.hunter.curr_hunger, self.engine.hunter.max_hunger),
            f"Nrgy {self.engine.hunter.curr_energy}/{self.engine.hunter.max_energy}",
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
                        elif isinstance(entity, bb.BerryBush):
                            lines.append("~BrryBsh")
                            lines.append(f" ~Berries: {entity.num_berries}")
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

    def render(self, console, x, y, border):
        console.print(x, y, border + self.text + border, self.color)