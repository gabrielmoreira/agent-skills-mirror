import unittest

from widgets.export import to_csv
from widgets.invoices import Invoice


class ToCsvTest(unittest.TestCase):
    def test_renders_header_and_rows(self):
        out = to_csv([Invoice("INV-1", "Bob", "12.5", "paid")])
        self.assertEqual(out, "number,customer,amount,status\nINV-1,Bob,12.50,paid\n")

    def test_skips_void_invoices(self):
        out = to_csv([Invoice("INV-1", "Bob", 1, "void"), Invoice("INV-2", "Ann", 2)])
        self.assertEqual(out.splitlines()[1:], ["INV-2,Ann,2.00,open"])


if __name__ == "__main__":
    unittest.main()
