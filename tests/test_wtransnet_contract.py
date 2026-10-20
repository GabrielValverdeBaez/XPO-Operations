"""Contract tests using only synthetic data. Run: python3 -m unittest discover -s tests -v"""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("validator", Path(__file__).resolve().parents[1] / "scripts" / "validate_wtransnet.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def row():
    x = [""] * 26
    x[0:13] = ["TEST-001", "20/10/2026", "España", "28909", "Getafe", "Portugal", "2675", "Odivelas", "Tráilers Completos", "Trailer", "Carga General", "15", "13,6"]
    x[20] = "S"
    x[23] = "Carga: 20/10/2026 de 10:00 a 16:00. Descarga: 21/10/2026 de 12:00 a 13:00."
    return x


class ContractTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual([], validator.errors_for_row(row(), 1))

    def test_exact_column_count(self):
        self.assertTrue(validator.errors_for_row(row()[:-1], 1))

    def test_price_never_in_tsv(self):
        x = row(); x[24] = "850"
        self.assertTrue(any("Precio" in e for e in validator.errors_for_row(x, 1)))

    def test_adr_missing_not_negative(self):
        self.assertEqual("", row()[13])
        x = row(); x[13] = "NO"
        self.assertTrue(validator.errors_for_row(x, 1))

    def test_portugal_postcode(self):
        x = row(); x[6] = "2675-076"
        self.assertTrue(validator.errors_for_row(x, 1))
        x[6] = "0410"
        self.assertFalse(validator.errors_for_row(x, 1))

    def test_nonexistent_date(self):
        x = row(); x[1] = "31/02/2026"
        self.assertTrue(validator.errors_for_row(x, 1))

    def test_comment_length(self):
        x = row(); x[23] = "X" * 501
        self.assertTrue(validator.errors_for_row(x, 1))

    def test_unsupported_bolsa(self):
        x = row(); x[8] = "FTL"
        self.assertTrue(validator.errors_for_row(x, 1))

    def test_decimal_with_comma(self):
        x = row(); x[11] = "15.5"
        self.assertTrue(validator.errors_for_row(x, 1))

    def test_tabs_preserve_last_columns(self):
        self.assertEqual(26, len("\t".join(row()).split("\t")))


if __name__ == "__main__":
    unittest.main()
