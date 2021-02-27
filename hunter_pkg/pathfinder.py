import tcod.path


def get_path(path_map, start, finish):
    graph = tcod.path.SimpleGraph(cost=path_map, cardinal=1, diagonal=0)
    pf = tcod.path.Pathfinder(graph)
    pf.add_root(start)

    return pf.path_to(finish).tolist()

def path_to_dest(entity, dest_x_y, movement_action_class):
    actions = []
    path = get_path(entity.engine.game_map.path_map, (entity.y, entity.x), (dest_x_y[1], dest_x_y[0]))
    previous_position = (entity.y, entity.x)

    for i in range(1, len(path)):
        actions.append(movement_action_class(entity, (path[i][0] - previous_position[0]), (path[i][1] - previous_position[1])))
        previous_position = (path[i][0], path[i][1])

    return actions

def path_to_target(entity, target):
    path = get_path(entity.engine.game_map.path_map, (entity.y, entity.x), (target.y, target.x))

    # kind weird workaround
    if len(path) > 1:
        first_step = path[1]
    else:
        first_step = path[0]

    return first_step[0] - entity.y, first_step[1] - entity.x
