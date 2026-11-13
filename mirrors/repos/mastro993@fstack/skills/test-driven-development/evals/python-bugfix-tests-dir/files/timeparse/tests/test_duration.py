import unittest

from timeparse import parse_duration


class ParseDurationTest(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(parse_duration("45s"), 45)

    def test_minutes(self):
        self.assertEqual(parse_duration("15m"), 900)

    def test_minutes_with_spaces(self):
        self.assertEqual(parse_duration("  15m "), 900)

    def test_hours(self):
        self.assertEqual(parse_duration("2h"), 7200)

    def test_two_hours_fifteen(self):
        self.assertEqual(parse_duration("2h15m"), 900)

    def test_uppercase(self):
        self.assertEqual(parse_duration("15M"), 900)

    def test_rejects_garbage(self):
        with self.assertRaises(ValueError):
            parse_duration("soon")


if __name__ == "__main__":
    unittest.main()
