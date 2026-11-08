import unittest

from widgets.pricing import line_total


class LineTotalTest(unittest.TestCase):
    def test_multiplies_quantity_by_price(self):
        self.assertEqual(line_total(3, 2.5), 7.5)

    def test_rounds_half_up(self):
        self.assertEqual(line_total(1, 0.125), 0.13)


if __name__ == "__main__":
    unittest.main()
