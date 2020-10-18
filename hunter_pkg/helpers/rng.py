import numpy.random as nprnd
import random as rnd

mem_range = []
mem_rand = []
mem_randint = []
mem_pick_rand = []

def set_seed(seed):
    nprnd.seed(seed)
    rnd.seed(seed)

def range_float(min, max, step=1):
    if min == max:
        return min
    else:
        return rnd.uniform(min, max)

def range_int(min, max, step=1):
    if min == max:
        return min
    else:
        return rnd.randrange(min, max, step)

def rand():
    """
    Random percentage
    """
    return nprnd.rand()

def randint(integer):
    return nprnd.randint(integer)

def pick_rand(list):
    return list[range_int(0, len(list) - 1)]
    