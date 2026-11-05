import unittest

from widgets.pricing import line_total


class LineTotalTest(unittest.TestCase):
    def test_multiplies_quantity_by_price(self):
        self.assertEqual(line_total(3, 2.5), 7.5)

    def test_rejects_quantities_below_one(self):
        with self.assertRaises(ValueError):
            line_total(0, 2.5)


if __name__ == "__main__":
    unittest.main()
