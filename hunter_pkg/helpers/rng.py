from numpy.random import randint as _randint
from random import randrange

def range(min, max, step=1):
    if min == max:
        return min
    else:
        return randrange(min, max, step)

def randint(integer):
    return _randint(integer)