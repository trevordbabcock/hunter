from typing import Optional

from math import floor

import tcod.event

from hunter_pkg import actions as act
from hunter_pkg import flogging
from hunter_pkg import log_level


flog = flogging.Flogging.get(__file__, log_level.LogLevel.get(__file__))

class InputHandler(tcod.event.EventDispatch[act.Action]):
    def ev_quit(self, input: tcod.event.Quit) -> Optional[act.Action]:
        raise SystemExit()

    def ev_keydown(self, input: tcod.event.KeyDown) -> Optional[act.Action]:
        action: Optional[act.Action] = None

        key = input.sym

        if key == tcod.event.K_UP:
            pass
        elif key == tcod.event.K_DOWN:
            pass
        elif key == tcod.event.K_LEFT:
            pass
        elif key == tcod.event.K_RIGHT:
            pass
        elif key == tcod.event.K_h:
            pass
        elif key == tcod.event.K_ESCAPE:
            action = act.EscapeAction()

        return action

    def ev_mousemotion(self, input: tcod.event.MouseMotion):
        x = input.pixel[0]
        y = input.pixel[1]

        return act.MouseMovementAction(x, y)