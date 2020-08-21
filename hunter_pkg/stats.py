import json


class Stats():
    map = {}

    @classmethod
    def load(cls, file_name="hunter_pkg/config/stats.json"):
        with open(file_name) as file:
            Stats.map = json.load(file)
