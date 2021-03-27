from hunter_pkg import flogging
from hunter_pkg import log_level


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class CollisionLayer():
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