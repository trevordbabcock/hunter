from math import floor

from hunter_pkg import stats

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