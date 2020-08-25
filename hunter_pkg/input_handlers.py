from typing import Optional

import tcod.event

from actions import Action, EscapeAction


class InputHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, input: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

    def ev_keydown(self, input: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key = input.sym

        if key == tcod.event.K_UP:
            pass
            #action = MovementAction(dx=0, dy=-1)
        elif key == tcod.event.K_DOWN:
            pass
            #action = MovementAction(dx=0, dy=1)
        elif key == tcod.event.K_LEFT:
            pass
            #action = MovementAction(dx=-1, dy=0)
        elif key == tcod.event.K_RIGHT:
            pass
            #action = MovementAction(dx=1, dy=0)
        elif key == tcod.event.K_h:
            pass
        elif key == tcod.event.K_ESCAPE:
            action = EscapeAction()

        # No valid key was pressed
        return action
