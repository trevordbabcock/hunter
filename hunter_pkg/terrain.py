from typing import Tuple

#import numpy as np  # type: ignore

from hunter_pkg import colors

class Terrain():
    def __init__(self, walkable, character, fg_color, bg_color):
        self.walkable = walkable
        self.character = character
        self.fg_color = fg_color
        self.bg_color = bg_color
    
    def get_graphic_dt(self, time_of_day, character_override, fg_color_override, bg_color_override):
        return (
            character_override or self.character,
            fg_color_override or self.fg_color(time_of_day),
            bg_color_override or self.bg_color(time_of_day)
        )


class Grass(Terrain):
    def __init__(self):
        super().__init__(True, ord("G"), colors.green, colors.dark_gray)

class Water(Terrain):
    def __init__(self):
        super().__init__(False, ord("~"), colors.blue, colors.dark_gray)

class Forest(Terrain):
    def __init__(self):
        super().__init__(True, ord("F"), colors.orange, colors.dark_gray)

class Mountain(Terrain):
    def __init__(self):
        super().__init__(False, ord("^"), colors.red, colors.dark_gray)