import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BLENDER_DIR = ROOT_DIR / "src" / "blender"
sys.path.insert(0, str(BLENDER_DIR))

from plate_geometry import CORNER_CUT, plate_outline_points


class PlateGeometryTests(unittest.TestCase):
    def test_right_cut_is_on_the_lower_right_corner(self):
        points = plate_outline_points(180, "RIGHT")

        self.assertEqual(points[2], (100.0, -90.0 + CORNER_CUT))
        self.assertEqual(points[3], (100.0 - CORNER_CUT, -90.0))

    def test_left_cut_mirrors_the_lower_right_cut(self):
        points = plate_outline_points(180, "LEFT")

        self.assertEqual(points[3], (-100.0 + CORNER_CUT, -90.0))
        self.assertEqual(points[4], (-100.0, -90.0 + CORNER_CUT))

    def test_left_cut_keeps_the_same_proportions_on_reduced_plate(self):
        points = plate_outline_points(128, "LEFT")

        self.assertEqual(points[3], (-100.0 + CORNER_CUT, -64.0))
        self.assertEqual(points[4], (-100.0, -64.0 + CORNER_CUT))


if __name__ == "__main__":
    unittest.main()
