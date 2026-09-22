"""Regressioner for inputfejl, små restbeløb og bogføring gennem hele planen."""
import contextlib
import io
import random
import unittest
from decimal import Decimal
from unittest.mock import patch

from su_beregner import beloeb, maaned, main
from tilbagebetaling import tilbagebetal


class RobusthedTests(unittest.TestCase):
    def test_interest_half_cent_rounds_up(self):
        # 0.96 * 43.75 / 1200 = 0.035 kr.; round only after multiplication.
        plan = tilbagebetal('0.96', '2029-12', '43.75')
        self.assertEqual(plan['rows'][0]['renter'], Decimal('0.04'))

    def test_invalid_amounts_have_actionable_errors(self):
        for value in (None, True, [], {}, "", "NaN", "Infinity", "1e100", "0.001", -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                beloeb(value)

    def test_invalid_date_types_have_actionable_errors(self):
        for value in (None, True, 202601, [], "0000-01", "2026-00", "2026-13"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                maaned(value)

    def test_interval_requires_integer_months(self):
        for value in (True, False, 1.0, 2.0, "2", None, 0, 3):
            with self.subTest(value=value), self.assertRaises(ValueError):
                tilbagebetal(1000, "2029-06", 0, value)

    def test_cli_reserve_uses_actual_small_payment(self):
        output = io.StringIO()
        arguments = ["su_beregner.py", "--gaeld", "10", "--laan", "0",
                     "--start", "2026-01", "--slut", "2026-01", "--rente-efter", "0"]
        with patch("sys.argv", arguments), contextlib.redirect_stdout(output):
            main()
        # Study debt 10.03 + one fee 15, spread over two months.
        self.assertIn("Budget pr. måned:      12,52 kr.", output.getvalue())

    def test_random_plans_balance_every_month(self):
        rng = random.Random(42)
        for case in range(100):
            debt = Decimal(rng.randrange(1, 100_000_000)) / 100
            rate = Decimal(rng.randrange(0, 10001)) / 100
            interval = rng.choice((1, 2))
            plan = tilbagebetal(debt, f"2029-{rng.randrange(1, 13):02d}", rate, interval)
            with self.subTest(case=case, debt=debt, rate=rate, interval=interval):
                balance = debt
                payment_months = []
                for row in plan["rows"]:
                    balance += row["renter"] - row["betaling"]
                    self.assertEqual(row["gaeld"], balance)
                    self.assertGreaterEqual(balance, 0)
                    if row["betaling"]:
                        payment_months.append(maaned(row["maaned"]))
                        self.assertEqual(row["gebyr"], plan["gebyr"])
                    else:
                        self.assertEqual(row["gebyr"], 0)
                self.assertEqual(balance, 0)
                self.assertTrue(all(b - a == interval for a, b in zip(payment_months, payment_months[1:])))
                self.assertEqual(plan["samlet_betaling"], debt + plan["renter"] + plan["gebyrer"])


if __name__ == "__main__":
    unittest.main()
