import unittest

from hunter_pkg import entity
from hunter_pkg import static_entity

class HunterTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_can_see(self):
        hunter = entity.Hunter(None, 20, 20)
        berry_bush = static_entity.BerryBush(None, 22, 22)
        actual = hunter.can_see(berry_bush)
        self.assertEqual(True, actual)

if __name__ == '__main__':
    unittest.main()