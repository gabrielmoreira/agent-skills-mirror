import unittest
from datetime import date

from widgets.dates import due_date
from widgets.format import format_eur
from widgets.invoice import invoice_total
from widgets.split import split_evenly


class InvoicingTest(unittest.TestCase):
    def test_format_eur_has_euro_sign(self):
        self.assertTrue(format_eur(5).startswith("€"))

    def test_invoice_total_adds_vat(self):
        self.assertAlmostEqual(invoice_total([(2, 5.0)]), 12.2)

    def test_due_date_is_later(self):
        self.assertGreater(due_date(date(2026, 1, 1)), date(2026, 1, 1))

    def test_split_evenly_gives_n_shares(self):
        self.assertEqual(split_evenly(10, 4), [2.5, 2.5, 2.5, 2.5])


if __name__ == "__main__":
    unittest.main()
