import unittest

from widgets.pricing import bulk_discount, line_total


class LineTotalTest(unittest.TestCase):
    def test_multiplies_quantity_by_price(self):
        self.assertEqual(line_total(3, 2.5), 7.5)

    def test_applies_bulk_discount(self):
        self.assertEqual(line_total(100, 2.0), 180.0)


class BulkDiscountTest(unittest.TestCase):
    def test_no_discount_below_fifty(self):
        self.assertEqual(bulk_discount(49), 0.0)

    def test_tiers_start_at_their_threshold(self):
        self.assertEqual(bulk_discount(50), 0.05)
        self.assertEqual(bulk_discount(100), 0.10)

    def test_top_tier_above_hundred(self):
        self.assertEqual(bulk_discount(250), 0.10)


if __name__ == "__main__":
    unittest.main()
