import unittest

from laboratory import perlin_noise as pn


class PerlinNoiseTestCase(unittest.TestCase):
    def test_normalize_to_range(self):
        self.assertEqual(pn.normalize_to_range(5, 0, 10, 0, 1), 0.5)
        self.assertEqual(pn.normalize_to_range(2, 0, 10, 0, 1), 0.2)
        self.assertEqual(pn.normalize_to_range(80, 10, 110, 0, 1), 0.7)
    
    def test_normalize_noise_map(self):
        noise_map = [[ 3,10, 4],
                     [ 5, 5, 6],
                     [ 9, 0, 9]]
        expected =  [[ 0.3, 1.0, 0.4],
                     [ 0.5, 0.5, 0.6],
                     [ 0.9, 0.0, 0.9]]

        self.assertEqual(pn.normalize_noise_map(noise_map), expected)


if __name__ == '__main__':
    unittest.main()