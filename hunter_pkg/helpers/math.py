
def clamp(num, minimum, maximum):
    if minimum <= num <= maximum:
        return num
    elif minimum <= num >= maximum:
        return maximum
    else: # minimum > num < maximum:
        return minimum