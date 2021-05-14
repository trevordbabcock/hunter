import tcod.path

from hunter_pkg.helpers.coord import Coord

def get_path(path_map, start, finish):
    graph = tcod.path.SimpleGraph(cost=path_map, cardinal=1, diagonal=0)
    pf = tcod.path.Pathfinder(graph)
    pf.add_root(start.to_reverse_tuple())
    path = pf.path_to(finish.to_reverse_tuple())[1:].tolist()
    path_coords = [Coord(i[1], i[0]) for i in path]

    return path_coords

def path_to_dest(entity, finish, movement_action_class):
    actions = []
    start = coord.Coord(entity.x, entity.y)
    path = get_path(entity.engine.game_map.path_map, start, finish)
    previous_position = start

    for i in range(len(path)):
        actions.append(movement_action_class(entity, (path[i][0] - previous_position.y), (path[i][1] - previous_position.x)))
        previous_position = coord.Coord(path[i][1], path[i][0])

    return actions

def path_to_target(entity, target):
    path = get_path(entity.engine.game_map.path_map, Coord(entity.x, entity.y), Coord(target.x, target.y))

    if len(path) == 0:
        return Coord(0, 0)
    else:
        first_step = path[0]

    return Coord(first_step.x - entity.x, first_step.y - entity.y)
