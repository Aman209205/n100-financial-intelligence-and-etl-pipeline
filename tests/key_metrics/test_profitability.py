import sys
import os
import unittest

# Import routing fix for core engine execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/analytics')))
from ratios import (
    compute_net_profit_margin,
    compute_operating_profit_margin,
    compute_return_on_equity,
    compute_return_on_capital_employed,
    compute_return_on_assets
)

class TestProfitabilityEngine(unittest.TestCase):
    
    def test_normal_case_npm(self):
        """Test standard operating values for NPM conversion."""
        self.assertAlmostEqual(compute_net_profit_margin(15, 100), 15.0)
        
    def test_zero_denominator_npm(self):
        """Verify NPM handling when corporate sales boundary collapses to zero."""
        self.assertIsNone(compute_net_profit_margin(10, 0))
        
    def test_opm_crosscheck_normal(self):
        """Verify perfect convergence checks with reported metrics."""
        opm, mismatch = compute_operating_profit_margin(20, 100, 20)
        self.assertAlmostEqual(opm, 20.0)
        self.assertFalse(mismatch)
        
    def test_opm_mismatch_anomaly(self):
        """Verify validation trigger when reported metrics deviate over > 1%."""
        opm, mismatch = compute_operating_profit_margin(25, 100, 10)
        self.assertTrue(mismatch)
        
    def test_roe_negative_equity_boundary(self):
        """Ensure ROE isolates broken financial structures (Equity + Reserves <= 0)."""
        self.assertIsNone(compute_return_on_equity(50, -100, 50))
        
    def test_roce_financials_sector_carveout(self):
        """Confirm relative benchmark logs activate seamlessly for banking/financial firms."""
        roce, log_msg = compute_return_on_capital_employed(30, 100, 200, 50, sector="Financials")
        self.assertEqual(log_msg, "Sector-Relative Evaluation Active")
        
    def test_roce_standard_threshold(self):
        """Confirm ordinary logging applies to generic non-financial sector segments."""
        roce, log_msg = compute_return_on_capital_employed(30, 100, 200, 50, sector="Technology")
        self.assertEqual(log_msg, "Standard Threshold Applied")
        
    def test_roa_zero_assets_condition(self):
        """Ensure system returns None smoothly if total asset valuation is marked zero."""
        self.assertIsNone(compute_return_on_assets(25, 0))

if __name__ == "__main__":
    unittest.main()