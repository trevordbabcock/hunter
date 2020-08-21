from __future__ import annotations

from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder
from hunter_pkg import static_entity


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Action:
    def perform(self):
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self):
        raise SystemExit()


class MovementAction(Action):
    def __init__(self, entity, dy, dx):
        super().__init__()

        self.entity = entity
        self.dx = dx
        self.dy = dy

    def perform(self):
        if type(self.entity).__name__ == "Hunter":
            flog.debug("hunter is moving")
        dest_x = self.entity.x + self.dx
        dest_y = self.entity.y + self.dy

        if not self.entity.engine.game_map.in_bounds(dest_x, dest_y):
            return  # Destination is out of bounds.
        if not self.entity.engine.game_map.tiles[dest_y][dest_x].terrain.walkable:
            return  # Destination is blocked by a tile.

        self.entity.move(self.dx, self.dy)


class SearchAreaAction(Action):
    def __init__(self, entity, game_map, search_radius, search_for_class, plan_b):
        self.entity = entity
        self.game_map = game_map
        self.search_radius = search_radius
        self.search_for_class = search_for_class
        self.plan_b = plan_b

    def perform(self):
        flog.debug("hunter is searching area")
        search_area = self.get_search_area()
        found_entities = []
        i = 0
        for y in range(len(search_area)):
            row = search_area[y]
            if row != None:
                for x in range(len(row)):
                    tile = row[x]
                    for e in tile.entities:
                        if e.__class__.__name__ == self.search_for_class:
                            i += 1
                            found_entities.append(e)
                            flog.debug("- found an entity: ({},{})".format(e.x, e.y))
                            break

        nearest_entity = None
        nearest_entity_distance = None
        for e in found_entities:
            if nearest_entity == None:
                nearest_entity = e
                nearest_entity_distance = self.get_distance(self.entity, e)
            else:
                distance = self.get_distance(self.entity, e)

                if (distance < nearest_entity_distance):
                    nearest_entity = e
                    nearest_entity_distance = distance

        if nearest_entity != None:
            path = pathfinder.get_path(self.game_map.path_map, (self.entity.y, self.entity.x), (nearest_entity.y, nearest_entity.x))
            previous_position = (self.entity.y, self.entity.x)

            for i in range(1, len(path)):
                self.entity.ai.action_queue.append(MovementAction(self.entity, (path[i][0] - previous_position[0]), (path[i][1] - previous_position[1])))
                previous_position = (path[i][0], path[i][1])

            self.entity.ai.action_queue.append(PickAndEatAction(self.entity, nearest_entity))
        else:
            for action in self.plan_b:
                self.entity.ai.action_queue.append(action)

    def get_distance(self, entity1, entity2):
        return abs(entity1.x - entity2.x) + abs(entity1.y - entity2.y)

    def get_search_area(self):
        search_area = [None] * (self.search_radius * 2)
        y_range_start = max(0, self.entity.y - self.search_radius)
        y_range_end = min(self.game_map.height - 1, self.entity.y + self.search_radius)
        x_range_start = max(0, self.entity.x - self.search_radius)
        x_range_end = min(self.game_map.width - 1, self.entity.x + self.search_radius)
        tmp_map = self.game_map.tiles[y_range_start:y_range_end]

        for y in range(len(tmp_map)):
            search_area[y] = tmp_map[y][x_range_start:x_range_end]

        return search_area


class PickAndEatAction(Action):
    def __init__(self, intelligent_entity, static_entity):
        self.intelligent_entity = intelligent_entity
        self.static_entity = static_entity

    def perform(self):
        flog.debug("hunter is picking and eating")
        berry = self.static_entity.pick_berry()
        self.intelligent_entity.eat(berry)
