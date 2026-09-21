import unittest
from decimal import Decimal
from su_beregner import beregn


class BeregnerTests(unittest.TestCase):
    def test_one_month_manual_calculation(self):
        row = beregn("1200", "300", "2026-12", "2026-12")[0]
        self.assertEqual(row["renter"], Decimal("5.00"))
        self.assertEqual(row["gaeld"], Decimal("1505.00"))

    def test_year_boundary_and_compounding(self):
        rows = beregn("1200", "0", "2026-12", "2027-01")
        self.assertEqual([r["maaned"] for r in rows], ["2026-12", "2027-01"])
        self.assertEqual(rows[-1]["gaeld"], Decimal("1208.01"))

    def test_accounting_identity_and_lower_borrowing(self):
        rows = beregn("5000", "1500", "2026-09", "2029-06")
        total = Decimal("5000") + sum(r["nyt_laan"] + r["renter"] for r in rows)
        self.assertEqual(rows[-1]["gaeld"], total)
        lower = beregn("5000", "1000", "2026-09", "2029-06")
        self.assertLess(lower[-1]["gaeld"], total)

    def test_zero(self):
        self.assertEqual(beregn(0, 0, "2026-01", "2026-12")[-1]["gaeld"], 0)

    def test_invalid_inputs(self):
        for debt, loan, start, end in [
            (-1, 0, "2026-01", "2026-02"),
            (0, "NaN", "2026-01", "2026-02"),
            (0, "Infinity", "2026-01", "2026-02"),
            (0, 3800, "2026-01", "2026-02"),
            (0, "1.001", "2026-01", "2026-02"),
            (0, 0, "2026-13", "2027-01"),
            (0, 0, "2026-02", "2026-01"),
        ]:
            with self.subTest(loan=loan, start=start):
                with self.assertRaises(ValueError):
                    beregn(debt, loan, start, end)


if __name__ == "__main__":
    unittest.main()
