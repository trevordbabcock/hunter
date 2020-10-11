
def clamp(num, minimum, maximum):
    if minimum <= num <= maximum:
        return num
    elif minimum <= num >= maximum:
        return maximum
    else: # minimum > num < maximum:
        return minimum

def get_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)
