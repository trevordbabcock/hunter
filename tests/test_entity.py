import unittest

from hunter_pkg.stats import Stats

class HunterTestCase(unittest.TestCase):
    def setUp(self):
        Stats.load()

    def tearDown(self):
        pass

    def test_can_see(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()