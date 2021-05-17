from math import floor

from hunter_pkg import stats

from hunter_pkg.helpers import coord

def clamp(num, minimum, maximum):
    if minimum <= num <= maximum:
        return num
    elif minimum <= num >= maximum:
        return maximum
    else: # minimum > num < maximum:
        return minimum

def get_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def round_game_time(game_time):
    max_time = stats.Stats.map()["settings"]["game-time"]["thresholds"]["max"]

    num_days = floor(game_time)
    day_time = round(game_time - num_days, 6)
    num_additional_days = floor(day_time / max_time)
    remainder = round(day_time % max_time, 6)
    num_days += num_additional_days

    return num_days + remainder

def get_decimal(num):
    return num - floor(num)

def get_opposite_coord(coord1, coord2):
    dx = coord2.x - coord1.x
    dy = coord2.y - coord1.y

    return coord.Coord(coord1.x - dx, coord1.y - dy)

# as n gets higher total_chance will approach 1 asymptocally
def calculate_muliplicative_chance(base_chance, n):
    total_chance = base_chance
    shrinker_chance = 1 - total_chance

    for i in range(n - 1):    
        adder_chance = shrinker_chance * base_chance
        total_chance = total_chance + adder_chance
        shrinker_chance = 1 - total_chance
    
    return total_chance