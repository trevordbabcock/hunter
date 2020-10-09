from hunter_pkg import vision_map as vsmap


class SearchAreaActionBase(): 
    def get_search_area(self, entity, search_radius, vision_map_func):
        search_area = [None] * ((search_radius * 2) + 1)
        y_range_start = max(0, entity.y - search_radius)
        y_range_end = min(entity.engine.game_map.height, entity.y + search_radius + 1) # +1 because [n:m] is actually not inclusive
        x_range_start = max(0, entity.x - search_radius)
        x_range_end = min(entity.engine.game_map.width, entity.x + search_radius + 1)
        tmp_map = entity.engine.game_map.tiles[y_range_start:y_range_end]

        for y in range(len(tmp_map)):
            search_area[y] = tmp_map[y][x_range_start:x_range_end]

        vision_map = vision_map_func(search_radius)
        search_area = vsmap.apply(vision_map, search_area)

        return search_area

    def find_entities(self, search_area, search_for_classes):
        found_entities = []
        i = 0

        for y in range(len(search_area)):
            row = search_area[y]
            if row != None:
                for x in range(len(row)):
                    tile = row[x]
                    if tile != None:
                        for e in tile.entities:
                            if not hasattr(e, "hidden") or not e.hidden:
                                if e.__class__.__name__ in search_for_classes:
                                    i += 1
                                    found_entities.append(e)

        return found_entities

    def find_terrain(self, search_area, search_for_classes):
        found_terrain = []
        i = 0

        for y in range(len(search_area)):
            row = search_area[y]
            if row != None:
                for x in range(len(row)):
                    tile = row[x]
                    if tile.terrain.__class__.__name__ in search_for_classes:
                        i += 1
                        found_terrain.append(tile)

        return found_terrain

    def get_nearest_entity(self, entity, found_entities):
        nearest_entity = None
        nearest_entity_distance = None
        for fe in found_entities:
            if nearest_entity == None:
                nearest_entity = fe
                nearest_entity_distance = self.get_distance(entity, fe)
            else:
                distance = self.get_distance(entity, fe)

                if (distance < nearest_entity_distance):
                    nearest_entity = fe
                    nearest_entity_distance = distance

        return nearest_entity

    def get_distance(self, entity1, entity2):
        return abs(entity1.x - entity2.x) + abs(entity1.y - entity2.y)
