import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/analytics')))
from ratios import (
    compute_debt_to_equity,
    compute_interest_coverage_ratio,
    compute_net_debt,
    compute_asset_turnover
)

class TestLeverageEngine(unittest.TestCase):
    
    def test_de_debt_free_returns_zero(self):
        """Verify D/E returns 0 if borrowings are zero."""
        de, flag = compute_debt_to_equity(0, 100, 50)
        self.assertEqual(de, 0.0)
        self.assertFalse(flag)
        
    def test_de_high_leverage_non_financial(self):
        """Verify high leverage flag triggers for non-financial companies if D/E > 5."""
        de, flag = compute_debt_to_equity(600, 50, 50, sector="Technology")
        self.assertTrue(flag)
        
    def test_de_high_leverage_financial_suppressed(self):
        """Ensure high leverage flag is suppressed for Financials sector."""
        de, flag = compute_debt_to_equity(600, 50, 50, sector="Financials")
        self.assertFalse(flag)
        
    def test_icr_interest_zero_debt_free(self):
        """Verify interest=0 returns None and 'Debt Free' label."""
        icr, label, warning = compute_interest_coverage_ratio(100, 20, 0)
        self.assertIsNone(icr)
        self.assertEqual(label, "Debt Free")
        self.assertFalse(warning)
        
    def test_icr_warning_trigger(self):
        """Verify warning flag triggers if ICR is less than 1.5."""
        icr, label, warning = compute_interest_coverage_ratio(10, 2, 10)
        self.assertTrue(warning)
        
    def test_net_debt_normal(self):
        """Test net debt calculation logic."""
        self.assertEqual(compute_net_debt(500, 200), 300.0)
        
    def test_asset_turnover_normal(self):
        """Test typical asset turnover values."""
        self.assertAlmostEqual(compute_asset_turnover(200, 100), 2.0)
        
    def test_asset_turnover_zero_denominator(self):
        """Ensure asset turnover handles zero assets smoothly."""
        self.assertIsNone(compute_asset_turnover(100, 0))

if __name__ == "__main__":
    unittest.main()