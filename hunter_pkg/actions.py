from __future__ import annotations

from hunter_pkg import flogging
from hunter_pkg import log_level
from hunter_pkg import pathfinder
from hunter_pkg import static_entity


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class Action:
    def perform(self):
        raise NotImplementedError()


class EscapeAction(Action):
    def perform(self):
        raise SystemExit()
