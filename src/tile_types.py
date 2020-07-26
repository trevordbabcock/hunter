from typing import Tuple

import numpy as np  # type: ignore

import colors

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark), dtype=tile_dt)

ground = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("G"), colors.green(), colors.dark_gray()),
    #light=(ord("G"), (255, 255, 255), (156, 222, 41)),
)
water = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord("~"), colors.blue(), colors.dark_gray()),
    #light=(ord("~"), (255, 255, 255), (164, 118, 255)),
)
forest = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("F"), colors.orange(), colors.dark_gray()),
    #light=(ord("F"), (255, 255, 255), (253, 140, 29)),
)
mountain = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord("^"), colors.red(), colors.dark_gray()),
    #light=(ord("^"), (255, 255, 255), (248, 37, 103)),
)
