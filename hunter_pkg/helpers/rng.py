import numpy.random as random
from random import randrange

def range(min, max, step=1):
    if min == max:
        return min
    else:
        return randrange(min, max, step)

def rand():
    """
    Random percentage
    """
    return random.rand()

def randint(integer):
    return random.randint(integer)

def pick_rand(list):
    return list[range(0, len(list) - 1)]
    