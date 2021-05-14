
class Coord():
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def to_tuple(self):
        return (self.x, self.y)

    def to_reverse_tuple(self):
        return (self.y, self.x)