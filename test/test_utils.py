import unittest
import sys
sys.path.append('../')
from scripts.utils import pole2tile, tile2pole

class TestUtils(unittest.TestCase):
    # メソッド名は必ず「test」をプレフィックスに付ける
    def test_pole2tile(self):
        tile_lat, tile_lon = pole2tile(35.363, 138.731, 18)
        true_lon = 232092.83128888888
        true_lat = 103511.26429049604
        self.assertAlmostEqual(true_lon ,tile_lon)
        self.assertAlmostEqual(true_lat ,tile_lat)

    def test_tile2pole(self):
        lat, lon = tile2pole(103511.26429049604, 232092.83128888888, 18)
        true_lon = 138.731
        true_lat = 35.363
        self.assertAlmostEqual(true_lon ,lon)
        self.assertAlmostEqual(true_lat ,lat)

if __name__ == '__main__':
    unittest.main()