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
        self.tile = None
    
    def get_header_footer_line(self, width):
        chars = []

        for i in range(width):
            if (i % 2) == 0:
                chars.append("-")
            else:
                chars.append(".")
        
        return WindowTextLine("".join(chars), width)
    
    def get_divider_line(self, width):
        chars = []

        for i in range(width):
            chars.append("-")
        
        return WindowTextLine("".join(chars), width)

    def render(self, console):
        window_text_lines = []

        console.draw_rect(x=self.x, y=self.y, height=48, width=17, ch=1, bg=self.color)

        window_text_lines.append(self.get_header_footer_line(self.width))
        window_text_lines.append(WindowTextLine("", self.width))
        window_text_lines.append(WindowTextLine("Entity: Hunter", self.width))
        window_text_lines.append(WindowTextLine(f"Hlth {self.engine.hunter.curr_health}/{self.engine.hunter.max_health}", self.width))
        window_text_lines.append(WindowTextLine("Hngr {:02.0f}/{}".format(self.engine.hunter.curr_hunger, self.engine.hunter.max_hunger), self.width))
        window_text_lines.append(WindowTextLine(f"Nrgy {self.engine.hunter.curr_energy}/{self.engine.hunter.max_energy}", self.width))

        for i in range(12):
            window_text_lines.append(WindowTextLine("", self.width))

        window_text_lines.append(self.get_divider_line(self.width))
        window_text_lines.append(self.get_divider_line(self.width))

        if self.tile != None:
            if self.tile.explored or not self.engine.settings["show-fog"]:
                window_text_lines.append(WindowTextLine(f"", self.width))
                window_text_lines.append(WindowTextLine("Tile", self.width))
                window_text_lines.append(WindowTextLine("Coord: ({:02.0f},{:02.0f})".format(self.tile.x, self.tile.y), self.width))
                window_text_lines.append(WindowTextLine("Trrn: {}".format(self.tile.terrain.__class__.__name__), self.width))

                if len(self.tile.entities) == 0:
                    window_text_lines.append(WindowTextLine("Entities: None", self.width))
                else:
                    window_text_lines.append(WindowTextLine("Entities:", self.width))

                    for entity in self.tile.entities:
                        if isinstance(entity, htr.Hunter):
                            window_text_lines.append(WindowTextLine("~Hntr", self.width))
                        elif isinstance(entity, rbt.Rabbit):
                            window_text_lines.append(WindowTextLine("~Rbbt", self.width))
                        elif isinstance(entity, bb.BerryBush):
                            window_text_lines.append(WindowTextLine("~BrryBsh", self.width))
                            window_text_lines.append(WindowTextLine(f" ~Berries: {entity.num_berries}", self.width))
            else:
                window_text_lines.append(WindowTextLine(f"", self.width))
                window_text_lines.append(WindowTextLine("???", self.width))

        for i in range(self.height - len(window_text_lines)):
            window_text_lines.append(WindowTextLine("", self.width))

        window_text_lines = window_text_lines[0:self.height-1]
        window_text_lines.append(self.get_header_footer_line(self.width))

        for i in range(len(window_text_lines)):
            line_y = i + 1
            window_text_lines[i].render(console, self.x, line_y, ".")


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
