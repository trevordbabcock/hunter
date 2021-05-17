
import unittest

from hunter_pkg.helpers import coord as c
from hunter_pkg.helpers import math


class GetOppositeCoordTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_opposite_coord(self):
        coord = math.get_opposite_coord(c.Coord(1, 1), c.Coord(3, 2))
        assert coord.x == -1
        assert coord.y == 0

        coord = math.get_opposite_coord(c.Coord(1, -1), c.Coord(-1, -4))
        assert coord.x == 3
        assert coord.y == 2

        coord = math.get_opposite_coord(c.Coord(-1, -4), c.Coord(1, -1))
        assert coord.x == -3
        assert coord.y == -7

        coord = math.get_opposite_coord(c.Coord(-2, -1), c.Coord(-2, -3))
        assert coord.x == -2
        assert coord.y == 1

        coord = math.get_opposite_coord(c.Coord(-2, -3), c.Coord(-2, -1))
        assert coord.x == -2
        assert coord.y == -5

class CalculateMuliplicativeChanceTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_opposite_coord(self):
        chance = math.calculate_muliplicative_chance(0.3, 1)
        assert chance == 0.3

        chance = math.calculate_muliplicative_chance(0.3, 2)
        assert chance == 0.51

        chance = math.calculate_muliplicative_chance(0.3, 3)
        assert chance == 0.657

        chance = math.calculate_muliplicative_chance(0.3, 4)
        assert chance == 0.7599

        chance = math.calculate_muliplicative_chance(0.3, 100)
        assert chance == 0.9999999999999997


if __name__ == '__main__':
    unittest.main()