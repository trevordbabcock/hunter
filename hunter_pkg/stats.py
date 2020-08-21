import functools
import json

from hunter_pkg import flogging
from hunter_pkg import log_level


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Stats():
    _map = None

    @classmethod
    def map(cls, file_name="hunter_pkg/config/stats.json"):
        if(cls._map is None):
            with open(file_name) as file:
                flog.debug("opened a file")
                cls._map = json.load(file)
                return cls._map

        return cls._map
