
def black():
    return (20,20,20)

def light_gray():
    return (75,75,75)


def dark_gray(time_of_day=None):
    if time_of_day == None:
        return dark_gray_morning()
    elif time_of_day == "morning":
        return dark_gray_morning()
    elif time_of_day == "afternoon":
        return dark_gray_afternoon()
    elif time_of_day == "evening":
        return dark_gray_evening()
    elif time_of_day == "night":
        return dark_gray_night()
    else:
        raise("no color for time of day {}".format(time_of_day))

def white(time_of_day=None):
    if time_of_day == None:
        return white_morning()
    elif time_of_day == "morning":
        return white_morning()
    elif time_of_day == "afternoon":
        return white_afternoon()
    elif time_of_day == "evening":
        return white_evening()
    elif time_of_day == "night":
        return white_night
    else:
        raise("no color for time of day {}".format(time_of_day))

def red(time_of_day):
    if time_of_day == "morning":
        return red_morning()
    elif time_of_day == "afternoon":
        return red_afternoon()
    elif time_of_day == "evening":
        return red_evening()
    elif time_of_day == "night":
        return red_night()
    else:
        raise("no color for time of day {}".format(time_of_day))

def blue(time_of_day):
    if time_of_day == "morning":
        return blue_morning()
    elif time_of_day == "afternoon":
        return blue_afternoon()
    elif time_of_day == "evening":
        return blue_evening()
    elif time_of_day == "night":
        return blue_night()
    else:
        raise("no color for time of day {}".format(time_of_day))

def green(time_of_day):
    if time_of_day == "morning":
        return green_morning()
    elif time_of_day == "afternoon":
        return green_afternoon()
    elif time_of_day == "evening":
        return green_evening()
    elif time_of_day == "night":
        return green_night()
    else:
        raise("no color for time of day {}".format(time_of_day))

def dark_green(time_of_day):
    if time_of_day == "morning":
        return dark_green_morning()
    elif time_of_day == "afternoon":
        return dark_green_afternoon()
    elif time_of_day == "evening":
        return dark_green_evening()
    elif time_of_day == "night":
        return dark_green_night()
    else:
        raise("no color for time of day {}".format(time_of_day))
        
def orange(time_of_day):
    if time_of_day == "morning":
        return orange_morning()
    elif time_of_day == "afternoon":
        return orange_afternoon()
    elif time_of_day == "evening":
        return orange_evening()
    elif time_of_day == "night":
        return orange_night()
    else:
        raise("no color for time of day {}".format(time_of_day))


def dark_gray_morning():
    return (31,31,31)

def white_morning():
    return (201, 200, 186)

def red_morning():
    return (248, 37, 103)

def blue_morning():
    return (164, 118, 255)

def green_morning():
    return (156, 222, 41)

def dark_green_morning():
    return (31, 57, 31)
        
def orange_morning():
    return (253, 140, 29)


def dark_gray_night():
    return(28,32,51)

def white_night():
    return (188,204,204)

def red_night():
    return (116,83,147)

def blue_night():
    return (111,115,155)

def green_night():
    return (160,189,160)

def orange_night():
    return (139,131,117)

def dark_green_night():
    return (42,51,59)


def dark_gray_afternoon():
    return(31,25,13)

def white_afternoon():
    return (255,252,200)

def red_afternoon():
    return (255,0,70)

def blue_afternoon():
    return (188,112,212)

def green_afternoon():
    return (171,222,0)

def orange_afternoon():
    return (255,132,0)

def dark_green_afternoon():
    return (29,54,5)


def dark_gray_evening():
    return(50,27,5)

def white_evening():
    return (255,231,97)

def red_evening():
    return (255,76,39)

def blue_evening():
    return (228,114,85)

def green_evening():
    return (252,196,45)

def orange_evening():
    return (255,137,37)

def dark_green_evening():
    return (61,49,8)