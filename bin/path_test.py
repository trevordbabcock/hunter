#!/bin/env python

#import numpy
import tcod

map = [
    [1,1,0,1,1],
    [1,1,0,1,1],
    [0,1,0,1,1],
    [1,1,0,1,1],
    [1,1,1,1,1],
]

# map = numpy.ones((5,5), dtype=numpy.int8, order="F")
# map[0,2] = 0
# map[2,0] = 0
# map[2,1] = 0
# map[2,2] = 0
# map[2,3] = 0

graph = tcod.path.SimpleGraph(cost=map, cardinal=1, diagonal=0)
pf = tcod.path.Pathfinder(graph)
pf.add_root((0,0))
path = pf.path_to((4,4)).tolist()

print(path)