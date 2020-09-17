from hunter_pkg.helpers import rng

from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import stats


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Bow():
    def __init__(self):
        self.accuracy = stats.Stats.map()["bow"]["accuracy"]
        self.damage = stats.Stats.map()["bow"]["damage"]

    def shoot(self, user, target):
        hit = (self.accuracy * user.accuracy) > rng.rand()

        if hit:
            target.curr_health -= self.damage
        else:
            flog.debug("arrow shot missed!")

        return hit
            