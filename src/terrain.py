from typing import Tuple

#import numpy as np  # type: ignore

import colors

class Terrain():
    def __init__(self, walkable, character, fg_color, bg_color):
        self.walkable = walkable   # bool
        self.character = character # int
        self.fg_color = fg_color   # 3-byte sequence
        self.bg_color = bg_color   # 3-byte sequence
    
    def graphic_dt(self):
        return (self.character, self.fg_color, self.bg_color) # cache this?

class Ground(Terrain):
    def __init__(self):
        super().__init__(True, ord("G"), colors.green(), colors.dark_gray())

class Water(Terrain):
    def __init__(self):
        super().__init__(False, ord("~"), colors.blue(), colors.dark_gray())

class Forest(Terrain):
    def __init__(self):
        super().__init__(True, ord("F"), colors.orange(), colors.dark_gray())

class Mountain(Terrain):
    def __init__(self):
        super().__init__(False, ord("^"), colors.red(), colors.dark_gray())
