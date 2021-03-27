from math import floor, ceil

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

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


class HeaderFooter():
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


class Break():
    def __init__(self, num=1):
        self.num = num

    def render(self):
        lines = []

        for n in range(self.num):
            lines.append("")

        return lines


class Button():
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