from numpy.random import randint

from .. import flogging
from .. import log_level


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class RabbitAI():
    def __init__(self, rabbit):
        self.rabbit = rabbit

    def perform(self):
        num = randint(4)

        if(num == 0):
            MovementAction(self.rabbit, -1, 0).perform()
        elif(num == 1):
            MovementAction(self.rabbit, 1, 0).perform()
        elif(num == 2):
            MovementAction(self.rabbit, 0, -1).perform()
        elif(num == 3):
            MovementAction(self.rabbit, 0, 1).perform()


# duplicating this for now
class MovementAction():
    def __init__(self, entity, dy, dx):
        super().__init__()

        self.entity = entity
        self.dx = dx
        self.dy = dy

    def perform(self):
        dest_x = self.entity.x + self.dx
        dest_y = self.entity.y + self.dy

        if not self.entity.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not self.entity.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return  # Destination is blocked by a tile.

        self.entity.move(self.dx, self.dy)