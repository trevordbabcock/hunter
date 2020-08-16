import tcod.path


def get_path(path_map, start, finish):
    graph = tcod.path.SimpleGraph(cost=path_map, cardinal=1, diagonal=0)
    pf = tcod.path.Pathfinder(graph)
    pf.add_root(start)

    return pf.path_to(finish).tolist()