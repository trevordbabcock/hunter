from numpy.random import randint

from hunter_pkg.entities import base_entity
from hunter_pkg import colors
from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import stats


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Rabbit(base_entity.IntelligentEntity):
    def __init__(self, engine, x: int, y: int):
        super().__init__(engine, x, y, "R", colors.white(), colors.light_gray(), RabbitAI(self), [stats.Stats.map()["rabbit"]["update-interval-start"], stats.Stats.map()["rabbit"]["update-interval-end"]], stats.Stats.map()["rabbit"]["update-interval-step"])
    
    def progress(self):
        pass


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
    def __init__(self, rabbit, dy, dx):
        super().__init__()

        self.rabbit = rabbit
        self.dx = dx
        self.dy = dy

    def perform(self):
        dest_x = self.rabbit.x + self.dx
        dest_y = self.rabbit.y + self.dy

        if not self.rabbit.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not self.rabbit.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return  # Destination is blocked by a tile.

        # remove reference from origin tile
        orig_tile = self.rabbit.engine.game_map.tiles[self.rabbit.y][self.rabbit.x]
        for entity in orig_tile.entities:
            if entity == self.rabbit:
                orig_tile.entities.remove(entity)
        
        # add reference to destination tile
        self.rabbit.engine.game_map.tiles[dest_y][dest_x].entities.append(self.rabbit)

        self.rabbit.move(self.dx, self.dy)