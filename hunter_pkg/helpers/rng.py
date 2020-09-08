from random import randrange

def range(min, max, step=1):
    if min == max:
        return min
    else:
        return randrange(min, max, step)