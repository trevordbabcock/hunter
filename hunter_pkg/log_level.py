import json
from os.path import basename


config_file = "hunter_pkg/config/log_level.json"

class LogLevel():
    _map = None

    @classmethod
    def map(cls):
        if(cls._map is None):
            with open(config_file) as file:
                cls._map = json.load(file)
                return cls._map

        return cls._map

    @classmethod
    def get(cls, file_name):
        try:
            return cls.map()["overrides"][basename(file_name)]
        except(KeyError):
            return cls.map()["default"]
