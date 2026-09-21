import unittest
from decimal import Decimal
from tilbagebetaling import tilbagebetal, loebetid

class TilbagebetalingTests(unittest.TestCase):
    def test_boundaries(self):
        for value, years in [('39999.99',7),('40000',8),('59999.99',8),('60000',9),('179999.99',14),('180000',15)]:
            self.assertEqual(loebetid(value),years)

    def test_wait_and_start(self):
        plan=tilbagebetal(1200,'2029-12',12)
        self.assertEqual(plan['start'],'2031-01')
        self.assertEqual(len([r for r in plan['rows'] if r['maaned']<'2031-01']),12)
        self.assertEqual(plan['rows'][0]['renter'],Decimal('12.00'))
        self.assertEqual(plan['rows'][1]['renter'],Decimal('12.12'))
        self.assertEqual(len([r for r in tilbagebetal(1200,'2029-06',0)['rows'] if r['maaned']<'2031-01']),18)

    def test_zero_rate_minimum_and_final_payment(self):
        plan=tilbagebetal(450,'2029-06',0)
        self.assertEqual(plan['ydelse'],200)
        self.assertEqual(plan['slut'],'2031-05')
        paid=[r for r in plan['rows'] if r['betaling']]
        self.assertEqual([r['betaling'] for r in paid],[200,200,50])
        self.assertEqual(plan['gebyrer'],45)
        self.assertEqual(plan['samlet_betaling'],495)

    def test_no_debt(self):
        plan=tilbagebetal(0,'2029-06')
        self.assertIsNone(plan['start'])
        self.assertIsNone(plan['slut'])
        self.assertEqual(plan['samlet_betaling'],0)

    def test_balance_and_intervals(self):
        for interval in (1,2):
            for rate in (0,'2.85',12):
                plan=tilbagebetal('72116.10','2029-06',rate,interval)
                self.assertEqual(plan['rows'][-1]['gaeld'],0)
                self.assertEqual(plan['samlet_betaling'],Decimal('72116.10')+plan['renter']+plan['gebyrer'])
                self.assertLessEqual(len([r for r in plan['rows'] if r['betaling']]),plan['aar']*12//interval)

    def test_invalid(self):
        for rate in ('NaN',-1,101):
            with self.assertRaises(ValueError): tilbagebetal(1000,'2029-06',rate)
        with self.assertRaises(ValueError): tilbagebetal(1000,'2029-06',2,3)
