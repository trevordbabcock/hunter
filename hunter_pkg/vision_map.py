
def normal():
    # Circle - distance 4
    #- - - 1 1 1 - - -
    #- - 1 1 1 1 1 - -
    #- 1 1 1 1 1 1 1 -
    #1 1 1 1 1 1 1 1 1
    #1 1 1 1 X 1 1 1 1
    #1 1 1 1 1 1 1 1 1
    #- 1 1 1 1 1 1 1 -
    #- - 1 1 1 1 1 - -
    #- - - 1 1 1 - - -
    return [
        [VisionTile(0, 0, False), VisionTile(0, 1, False), VisionTile(0, 2, False), VisionTile(0, 3, True), VisionTile(0, 4, True), VisionTile(0, 5, True), VisionTile(0, 6, False), VisionTile(0, 7, False), VisionTile(0, 8, False)],
        [VisionTile(1, 0, False), VisionTile(1, 1, False), VisionTile(1, 2, True),  VisionTile(1, 3, True), VisionTile(1, 4, True), VisionTile(1, 5, True), VisionTile(1, 6, True),  VisionTile(1, 7, False), VisionTile(1, 8, False)],
        [VisionTile(2, 0, False), VisionTile(2, 1, True),  VisionTile(2, 2, True),  VisionTile(2, 3, True), VisionTile(2, 4, True), VisionTile(2, 5, True), VisionTile(2, 6, True),  VisionTile(2, 7, True),  VisionTile(2, 8, False)],
        [VisionTile(3, 0, True),  VisionTile(3, 1, True),  VisionTile(3, 2, True),  VisionTile(3, 3, True), VisionTile(3, 4, True), VisionTile(3, 5, True), VisionTile(3, 6, True),  VisionTile(3, 7, True),  VisionTile(3, 8, True)],
        [VisionTile(4, 0, True),  VisionTile(4, 1, True),  VisionTile(4, 2, True),  VisionTile(4, 3, True), VisionTile(4, 4, True), VisionTile(4, 5, True), VisionTile(4, 6, True),  VisionTile(4, 7, True),  VisionTile(4, 8, True)],
        [VisionTile(5, 0, True),  VisionTile(5, 1, True),  VisionTile(5, 2, True),  VisionTile(5, 3, True), VisionTile(5, 4, True), VisionTile(5, 5, True), VisionTile(5, 6, True),  VisionTile(5, 7, True),  VisionTile(5, 8, True)],
        [VisionTile(6, 0, False), VisionTile(6, 1, True),  VisionTile(6, 2, True),  VisionTile(6, 3, True), VisionTile(6, 4, True), VisionTile(6, 5, True), VisionTile(6, 6, True),  VisionTile(6, 7, True),  VisionTile(6, 8, False)],
        [VisionTile(7, 0, False), VisionTile(7, 1, False), VisionTile(7, 2, True),  VisionTile(7, 3, True), VisionTile(7, 4, True), VisionTile(7, 5, True), VisionTile(7, 6, True),  VisionTile(7, 7, False),  VisionTile(7, 8, False)],
        [VisionTile(8, 0, False), VisionTile(8, 1, False), VisionTile(8, 2, False), VisionTile(8, 3, True), VisionTile(8, 4, True), VisionTile(8, 5, True), VisionTile(8, 6, False),  VisionTile(8, 7, False), VisionTile(8, 8, False)],
    ]

def test():
    # Square - distance 2
    # 1 1 1 1 1
    # 1 1 1 1 1
    # 1 1 1 1 1
    # 1 1 1 1 1
    # 1 1 1 1 1
    return [
        [VisionTile(0, 0, True),  VisionTile(0, 1, True),  VisionTile(0, 2, True),  VisionTile(0, 3, True), VisionTile(0, 4, True)],
        [VisionTile(1, 0, True),  VisionTile(1, 1, True),  VisionTile(1, 2, True),  VisionTile(1, 3, True), VisionTile(1, 4, True)],
        [VisionTile(2, 0, True),  VisionTile(2, 1, True),  VisionTile(2, 2, True),  VisionTile(2, 3, True), VisionTile(2, 4, True)],
        [VisionTile(3, 0, True),  VisionTile(3, 1, True),  VisionTile(3, 2, True),  VisionTile(3, 3, True), VisionTile(3, 4, True)],
        [VisionTile(4, 0, True),  VisionTile(4, 1, True),  VisionTile(4, 2, True),  VisionTile(4, 3, True), VisionTile(4, 4, True)],
    ]

class VisionTile():
    def __init__(self, x, y, visible):
        self.x = x
        self.y = y
        self.visible = visible
