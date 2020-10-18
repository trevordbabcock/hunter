#!/bin/env python

import time
import math

# print(time.perf_counter())
# time.sleep(1)
# print(time.perf_counter())

def round_game_time(game_time):
    max_time = 23999
    game_time = str(game_time)
    
    split_str = game_time.split(".")
    num_days = int(split_str[0])
    day_time = int(split_str[1].ljust(5, '0'))
    num_additional_days = round(day_time / max_time)
    remainder = str(round(day_time % max_time)).rjust(5, '0')

    num_days += num_additional_days

    return f"{num_days}.{remainder}"


def round_game_time_2(game_time):
    max_time = 0.24000
    
    num_days = math.floor(game_time)
    day_time = round(game_time - num_days, 6)
    num_additional_days = round(day_time / max_time)
    remainder = round(day_time % max_time, 6)

    num_days += num_additional_days

    return num_days + remainder


#print(round_game_time(0.24000))
print(round_game_time_2(0.24000))
print(round_game_time_2(2.25050))
print(round_game_time_2(1.23999))
print(round_game_time_2(1.47998))
print(round_game_time_2(1.24000))
print(round_game_time_2(1.48000))
print(round_game_time_2(500.24000))
print(round_game_time_2(500.12))

print(float("1.12001"))
