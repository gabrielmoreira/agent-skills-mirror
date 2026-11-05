import unittest

from widgets.currency import format_eur


class FormatEurTest(unittest.TestCase):
    def test_two_decimals_and_separators(self):
        self.assertEqual(format_eur(1234.5), "€1,234.50")

    def test_zero(self):
        self.assertEqual(format_eur(0), "€0.00")


if __name__ == "__main__":
    unittest.main()
