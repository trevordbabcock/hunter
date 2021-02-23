
def apply(vision_map, grid):
    for i in range(len(vision_map)):
        row = vision_map[i]
        for j in range(len(row)):
            if not vision_map[i] != None:
                if not vision_map[i][j].visible:
                    grid[i][j] = None

    return grid

def generate_vision_map(schematic):
    vmap = []

    for y, row in enumerate(schematic):
        vmap.append([])

        for x, cell in enumerate(row):
            vmap[y].append(VisionTile(x, y, cell == '1'))
    
    return vmap

# TODO refactor this to be more automated
def circle(radius):
    # used in vision schematics
    _ = '0'
    l = '1'
    X = '1'

    if radius == 1:
        schematic = [
            [l,l,l],
            [l,X,l],
            [l,l,l],
        ]

        return generate_vision_map(schematic)
    elif radius == 2:
        schematic = [
            [_,l,l,l,_],
            [l,l,l,l,l],
            [l,l,X,l,l],
            [l,l,l,l,l],
            [_,l,l,l,_],
        ] 

        return generate_vision_map(schematic)
    elif radius == 3:
        schematic = [
            [_,_,l,l,l,_,_],
            [_,l,l,l,l,l,_],
            [l,l,l,l,l,l,l],
            [l,l,l,X,l,l,l],
            [l,l,l,l,l,l,l],
            [_,l,l,l,l,l,_],
            [_,_,l,l,l,_,_],
        ]

        return generate_vision_map(schematic)
    elif radius == 4:
        schematic = [
            [_,_,_,l,l,l,_,_,_],
            [_,_,l,l,l,l,l,_,_],
            [_,l,l,l,l,l,l,l,_],
            [l,l,l,l,l,l,l,l,l],
            [l,l,l,l,X,l,l,l,l],
            [l,l,l,l,l,l,l,l,l],
            [_,l,l,l,l,l,l,l,_],
            [_,_,l,l,l,l,l,_,_],
            [_,_,_,l,l,l,_,_,_],
        ]

        return generate_vision_map(schematic)
    elif radius == 5:
        schematic = [
            [_,_,_,l,l,l,l,l,_,_,_],
            [_,_,l,l,l,l,l,l,l,_,_],
            [_,l,l,l,l,l,l,l,l,l,_],
            [l,l,l,l,l,l,l,l,l,l,l],
            [l,l,l,l,l,l,l,l,l,l,l],
            [l,l,l,l,l,X,l,l,l,l,l],
            [l,l,l,l,l,l,l,l,l,l,l],
            [l,l,l,l,l,l,l,l,l,l,l],
            [_,l,l,l,l,l,l,l,l,l,_],
            [_,_,l,l,l,l,l,l,l,_,_],
            [_,_,_,l,l,l,l,l,_,_,_],
        ]
        
        return generate_vision_map(schematic)
    else:
        raise NotImplementedError

def square(radius):
    # TODO automate this; literally just a 2D array of one's
    if radius == 1:
        # 1 1 1
        # 1 X 1
        # 1 1 1
        return [
            [VisionTile(0, 0, True), VisionTile(0, 1, True), VisionTile(0, 2, True)],
            [VisionTile(1, 0, True), VisionTile(1, 1, True), VisionTile(1, 2, True)],
            [VisionTile(2, 0, True), VisionTile(2, 1, True), VisionTile(2, 2, True)],
        ]
    elif radius == 2:
        # 1 1 1 1 1
        # 1 1 1 1 1
        # 1 1 X 1 1
        # 1 1 1 1 1
        # 1 1 1 1 1
        return [
            [VisionTile(0, 0, True),  VisionTile(0, 1, True),  VisionTile(0, 2, True),  VisionTile(0, 3, True), VisionTile(0, 4, True)],
            [VisionTile(1, 0, True),  VisionTile(1, 1, True),  VisionTile(1, 2, True),  VisionTile(1, 3, True), VisionTile(1, 4, True)],
            [VisionTile(2, 0, True),  VisionTile(2, 1, True),  VisionTile(2, 2, True),  VisionTile(2, 3, True), VisionTile(2, 4, True)],
            [VisionTile(3, 0, True),  VisionTile(3, 1, True),  VisionTile(3, 2, True),  VisionTile(3, 3, True), VisionTile(3, 4, True)],
            [VisionTile(4, 0, True),  VisionTile(4, 1, True),  VisionTile(4, 2, True),  VisionTile(4, 3, True), VisionTile(4, 4, True)],
        ]
    else:
        raise NotImplementedError


class VisionTile():
    def __init__(self, x, y, visible):
        self.x = x
        self.y = y
        self.visible = visible

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.visible == other.visible
