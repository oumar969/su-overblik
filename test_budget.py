import unittest
from decimal import Decimal
from budget import beregn_budget
from tilbagebetaling import tilbagebetal


class BudgetTests(unittest.TestCase):
    def test_cashflow_and_reserve(self):
        plan = tilbagebetal(450, '2029-06', 0)
        result = beregn_budget(20000, 15000, plan)
        self.assertEqual(result['stoerste_opkraevning'], 215)
        self.assertEqual(result['maanedlig_reserve'], Decimal('107.50'))
        self.assertEqual(result['efter_reserve'], Decimal('4892.50'))
        self.assertEqual(result['efter_opkraevning'], 4785)

    def test_no_debt_has_no_fee(self):
        result = beregn_budget(0, 100, tilbagebetal(0, '2029-06'))
        self.assertEqual(result['maanedlig_reserve'], 0)
        self.assertEqual(result['efter_reserve'], -100)
        self.assertIsNone(result['andel_af_netto'])

    def test_small_final_payment(self):
        result = beregn_budget(1000, 800, tilbagebetal(10, '2029-06', 0, 1))
        self.assertEqual(result['maanedlig_reserve'], 25)

    def test_invalid_amounts(self):
        plan = tilbagebetal(0, '2029-06')
        for income, expenses in [(-1, 0), (0, -1), ('NaN', 0), (0, 'Infinity')]:
            with self.assertRaises(ValueError):
                beregn_budget(income, expenses, plan)
