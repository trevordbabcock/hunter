import json


class Stats():
    map = {}

    @classmethod
    def load(cls, file_name):
        with open(file_name) as file:
            Stats.map = json.load(file)
