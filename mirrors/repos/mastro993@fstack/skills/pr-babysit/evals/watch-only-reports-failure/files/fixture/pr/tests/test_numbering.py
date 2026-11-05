import unittest

from widgets.numbering import format_invoice_number


class FormatInvoiceNumberTest(unittest.TestCase):
    def test_pads_sequence_to_four_digits(self):
        self.assertEqual(format_invoice_number(2026, 42), "INV-2026-0042")

    def test_keeps_long_sequences(self):
        self.assertEqual(format_invoice_number(2026, 12345), "INV-2026-12345")


if __name__ == "__main__":
    unittest.main()
