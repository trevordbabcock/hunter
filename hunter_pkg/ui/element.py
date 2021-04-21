from math import floor, ceil

from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))


class Hoverable():
    def __init__(self, color, hovered_color):
        #self.hovered = False
        self.color = color
        self.hovered_color = hovered_color

    def is_hovered(self):
        return self.engine.hovered_ui_element != None and self.id == self.engine.hovered_ui_element.id

    def get_color(self):
        return self.hovered_color if self.is_hovered() else self.color


class Text():
    def __init__(self, text, color=colors.white()):
        self.text = text
        self.color = color

    def format_text(self, text, width, borderless_width):
        if len(text) <= (borderless_width):
            text = text.ljust(borderless_width, " ")
        else:
            text = text[0:borderless_width]

        return text

    def render(self, console, x, y, width, border):
        formatted_text = self.format_text(self.text, width, width - 2)

        # separate the text from the border in case there is a hovered text color
        console.print(x, y, border, colors.white())
        console.print(x + 1, y, formatted_text, self.color)
        console.print(x + 1 + len(formatted_text), y, border, colors.white())


class HeaderFooter():
    def __init__(self):
        pass

    def render(self, console, x, y, width, border):
        text = []

        for i in range(width):
            if (i % 2) == 0:
                text.append("-")
            else:
                text.append(".")

        Text("".join(text)).render(console, x, y, width, border)


class Divider():
    def __init__(self):
        pass

    def render(self, console, x, y, width, border):
        text = "-" * width
        Text(text).render(console, x, y, width, border)


class Break():
    def __init__(self, num=1):
        self.num = num
        self.height = num

    def render(self, console, x, y, width, border):
        for i in range(self.num):
            element_y = i + y
            Text("").render(console, x, element_y, width, border)


class PaddedText():
    def __init__(self, text, amount):
        self.text = text
        self.amount = amount
    
    def render(self, console, x, y, width, border):
        formatted_text = (" " * self.amount) + self.text
        Text(formatted_text).render(console, x, y, width, border)


class CenteredText():
    def __init__(self, text):
        self.text = text
    
    def render(self, console, x, y, width, border):
        formatted_text = " " * floor((width - 1 - len(self.text)) / 2) + self.text
        Text(formatted_text).render(console, x, y, width, border)


class Button(Hoverable):
    def __init__(self, id, text, width, panel_width, engine):
        self.id = id
        self.text = text
        self.width = width
        self.panel_width = panel_width
        self.engine = engine
        self.height = 4
        self.color = colors.white()

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

    def render(self, console, x, y, width, border):
        lines = []

        if self.is_hovered():
            lines.extend([
                self.header_footer(self.width),
                self.hoverify(self.middle(self.width)),
                self.hoverify(self.middle_text(self.width, self.text)),
                self.header_footer(self.width),
            ])
        else:
            lines.extend([
                self.header_footer(self.width),
                self.middle(self.width),
                self.middle_text(self.width, self.text),
                self.header_footer(self.width),
            ])

        for i in range(len(lines)):
            Text(self.center_line(self.panel_width , lines[i])).render(console, x, y + i, self.panel_width, border)

    def is_hovered(self):
        return self.engine.hovered_ui_element != None and self.id == self.engine.hovered_ui_element.id


class TextOnlyButton(Hoverable):
    def __init__(self, id, text, engine):
        super().__init__(colors.white(), colors.popcorn())
        self.id = id
        self.text = text
        self.engine = engine
        self.height = 1
        self.width = len(text)

    def render(self, console, x, y, width, border):
        color = self.hovered_color if self.is_hovered() else self.color
        return Text(self.text, color).render(console, x, y, width, border, color)


class ToggleableTextOnlyButton(TextOnlyButton):
    def __init__(self, id, text, engine, key, enabled=True):
        super().__init__(id, text, engine)
        self.width = self.width + 2 # to account for adding the checkbox and a space
        self.key = key

        if not self.id in self.engine.settings[self.key]:
            self.engine.settings[self.key][self.id] = enabled

    def toggle(self):
        self.engine.settings[self.key][self.id] = not self.engine.settings[self.key][self.id]

    def add_toggle(self, text):
        toggle_char = "X" if self.engine.settings[self.key][self.id] else "O"
        return toggle_char + text

    def render(self, console, x, y, width, border):
        color = self.hovered_color if self.is_hovered() else self.color
        formatted_text = self.add_toggle(self.text)
        Text(formatted_text, color).render(console, x, y, width, border)
