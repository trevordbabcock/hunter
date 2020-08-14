from __future__ import annotations

from typing import TYPE_CHECKING

import entity
import static_entity


class Action:
    def perform(self, entity):
        """Perform this action with the objects needed to determine its scope.

        `entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self, entity):
        raise SystemExit()


class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()

        self.dx = dx
        self.dy = dy

    def perform(self, entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if not entity.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not entity.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return  # Destination is blocked by a tile.

        entity.move(self.dx, self.dy)


class SearchAreaAction(Action):
    def __init__(self, game_map, x, y, search_radius, search_for_class):
        self.game_map = game_map
        self.x = x
        self.y = y
        self.search_radius = search_radius
        self.search_for_class = search_for_class

    def perform(self, entity):
        search_area = self.get_search_area()
        i = 0
        for y in range(len(search_area)):
            row = search_area[y]
            for x in range(len(row)):
                tile = row[x]
                for e in tile.entities:
                    if isinstance(e, static_entity.BerryBush):
                        i += 1
                        print ("{}. FOUND A BERRY BUSH - ({},{})".format(i, x, y))
                        break

    def get_search_area(self):
        search_area = [None] * (self.search_radius * 2)
        y_range_start = self.y - self.search_radius
        y_range_end = self.y + self.search_radius
        x_range_start = self.x - self.search_radius
        x_range_end = self.x + self.search_radius
        tmp_map = self.game_map.tiles[y_range_start:y_range_end]

        for y in range(len(tmp_map)):
            search_area[y] = tmp_map[y][x_range_start:x_range_end]

        return search_area
