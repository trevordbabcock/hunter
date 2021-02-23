import unittest

from hunter_pkg import vision_map as vsmap


class VisionMapTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_circle(self):
        actual = vsmap.circle(1)
        expected = [
            [vsmap.VisionTile(0, 0, True), vsmap.VisionTile(1, 0, True), vsmap.VisionTile(2, 0, True)],
            [vsmap.VisionTile(0, 1, True), vsmap.VisionTile(1, 1, True), vsmap.VisionTile(2, 1, True)],
            [vsmap.VisionTile(0, 2, True), vsmap.VisionTile(1, 2, True), vsmap.VisionTile(2, 2, True)],
        ]
        assertListsEqual(self, expected, actual)

        actual = vsmap.circle(2)
        expected = [
            [vsmap.VisionTile(0, 0, False), vsmap.VisionTile(1, 0, True), vsmap.VisionTile(2, 0, True), vsmap.VisionTile(3, 0, True), vsmap.VisionTile(4, 0, False)],
            [vsmap.VisionTile(0, 1, True),  vsmap.VisionTile(1, 1, True), vsmap.VisionTile(2, 1, True), vsmap.VisionTile(3, 1, True), vsmap.VisionTile(4, 1, True)],
            [vsmap.VisionTile(0, 2, True),  vsmap.VisionTile(1, 2, True), vsmap.VisionTile(2, 2, True), vsmap.VisionTile(3, 2, True), vsmap.VisionTile(4, 2, True)],
            [vsmap.VisionTile(0, 3, True),  vsmap.VisionTile(1, 3, True), vsmap.VisionTile(2, 3, True), vsmap.VisionTile(3, 3, True), vsmap.VisionTile(4, 3, True)],
            [vsmap.VisionTile(0, 4, False), vsmap.VisionTile(1, 4, True), vsmap.VisionTile(2, 4, True), vsmap.VisionTile(3, 4, True), vsmap.VisionTile(4, 4, False)],
        ]
        assertListsEqual(self, expected, actual)

        actual = vsmap.circle(3)
        expected = [
            [vsmap.VisionTile(0, 0, False), vsmap.VisionTile(1, 0, False), vsmap.VisionTile(2, 0, True), vsmap.VisionTile(3, 0, True), vsmap.VisionTile(4, 0, True), vsmap.VisionTile(5, 0, False), vsmap.VisionTile(6, 0, False)],
            [vsmap.VisionTile(0, 1, False), vsmap.VisionTile(1, 1, True),  vsmap.VisionTile(2, 1, True), vsmap.VisionTile(3, 1, True), vsmap.VisionTile(4, 1, True), vsmap.VisionTile(5, 1, True),  vsmap.VisionTile(6, 1, False)],
            [vsmap.VisionTile(0, 2, True),  vsmap.VisionTile(1, 2, True),  vsmap.VisionTile(2, 2, True), vsmap.VisionTile(3, 2, True), vsmap.VisionTile(4, 2, True), vsmap.VisionTile(5, 2, True),  vsmap.VisionTile(6, 2, True)],
            [vsmap.VisionTile(0, 3, True),  vsmap.VisionTile(1, 3, True),  vsmap.VisionTile(2, 3, True), vsmap.VisionTile(3, 3, True), vsmap.VisionTile(4, 3, True), vsmap.VisionTile(5, 3, True),  vsmap.VisionTile(6, 3, True)],
            [vsmap.VisionTile(0, 4, True),  vsmap.VisionTile(1, 4, True),  vsmap.VisionTile(2, 4, True), vsmap.VisionTile(3, 4, True), vsmap.VisionTile(4, 4, True), vsmap.VisionTile(5, 4, True),  vsmap.VisionTile(6, 4, True)],
            [vsmap.VisionTile(0, 5, False), vsmap.VisionTile(1, 5, True),  vsmap.VisionTile(2, 5, True), vsmap.VisionTile(3, 5, True), vsmap.VisionTile(4, 5, True), vsmap.VisionTile(5, 5, True),  vsmap.VisionTile(6, 5, False)],
            [vsmap.VisionTile(0, 6, False), vsmap.VisionTile(1, 6, False), vsmap.VisionTile(2, 6, True), vsmap.VisionTile(3, 6, True), vsmap.VisionTile(4, 6, True), vsmap.VisionTile(5, 6, False), vsmap.VisionTile(6, 6, False)],
        ]
        assertListsEqual(self, expected, actual)

        actual = vsmap.circle(4)
        expected = [
            [vsmap.VisionTile(0, 0, False), vsmap.VisionTile(1, 0, False), vsmap.VisionTile(2, 0, False), vsmap.VisionTile(3, 0, True), vsmap.VisionTile(4, 0, True), vsmap.VisionTile(5, 0, True), vsmap.VisionTile(6, 0, False), vsmap.VisionTile(7, 0, False), vsmap.VisionTile(8, 0, False)],
            [vsmap.VisionTile(0, 1, False), vsmap.VisionTile(1, 1, False), vsmap.VisionTile(2, 1, True),  vsmap.VisionTile(3, 1, True), vsmap.VisionTile(4, 1, True), vsmap.VisionTile(5, 1, True), vsmap.VisionTile(6, 1, True),  vsmap.VisionTile(7, 1, False), vsmap.VisionTile(8, 1, False)],
            [vsmap.VisionTile(0, 2, False), vsmap.VisionTile(1, 2, True),  vsmap.VisionTile(2, 2, True),  vsmap.VisionTile(3, 2, True), vsmap.VisionTile(4, 2, True), vsmap.VisionTile(5, 2, True), vsmap.VisionTile(6, 2, True),  vsmap.VisionTile(7, 2, True),  vsmap.VisionTile(8, 2, False)],
            [vsmap.VisionTile(0, 3, True),  vsmap.VisionTile(1, 3, True),  vsmap.VisionTile(2, 3, True),  vsmap.VisionTile(3, 3, True), vsmap.VisionTile(4, 3, True), vsmap.VisionTile(5, 3, True), vsmap.VisionTile(6, 3, True),  vsmap.VisionTile(7, 3, True),  vsmap.VisionTile(8, 3, True)],
            [vsmap.VisionTile(0, 4, True),  vsmap.VisionTile(1, 4, True),  vsmap.VisionTile(2, 4, True),  vsmap.VisionTile(3, 4, True), vsmap.VisionTile(4, 4, True), vsmap.VisionTile(5, 4, True), vsmap.VisionTile(6, 4, True),  vsmap.VisionTile(7, 4, True),  vsmap.VisionTile(8, 4, True)],
            [vsmap.VisionTile(0, 5, True),  vsmap.VisionTile(1, 5, True),  vsmap.VisionTile(2, 5, True),  vsmap.VisionTile(3, 5, True), vsmap.VisionTile(4, 5, True), vsmap.VisionTile(5, 5, True), vsmap.VisionTile(6, 5, True),  vsmap.VisionTile(7, 5, True),  vsmap.VisionTile(8, 5, True)],
            [vsmap.VisionTile(0, 6, False), vsmap.VisionTile(1, 6, True),  vsmap.VisionTile(2, 6, True),  vsmap.VisionTile(3, 6, True), vsmap.VisionTile(4, 6, True), vsmap.VisionTile(5, 6, True), vsmap.VisionTile(6, 6, True),  vsmap.VisionTile(7, 6, True),  vsmap.VisionTile(8, 6, False)],
            [vsmap.VisionTile(0, 7, False), vsmap.VisionTile(1, 7, False), vsmap.VisionTile(2, 7, True),  vsmap.VisionTile(3, 7, True), vsmap.VisionTile(4, 7, True), vsmap.VisionTile(5, 7, True), vsmap.VisionTile(6, 7, True),  vsmap.VisionTile(7, 7, False), vsmap.VisionTile(8, 7, False)],
            [vsmap.VisionTile(0, 8, False), vsmap.VisionTile(1, 8, False), vsmap.VisionTile(2, 8, False), vsmap.VisionTile(3, 8, True), vsmap.VisionTile(4, 8, True), vsmap.VisionTile(5, 8, True), vsmap.VisionTile(6, 8, False), vsmap.VisionTile(7, 8, False), vsmap.VisionTile(8, 8, False)],
        ]
        assertListsEqual(self, expected, actual)


def assertListsEqual(t, list_a, list_b):
    t.assertEqual(len(list_a), len(list_b))
    equal = True

    for i in range(len(list_a)):
        equal = (list_a[i] == list_b[i]) and equal

    t.assertTrue(equal)

if __name__ == '__main__':
    unittest.main()