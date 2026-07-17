import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/analytics')))
from cashflow_kpis import compute_free_cash_flow, classify_capital_allocation, compute_capex_intensity

class TestCashFlowEngine(unittest.TestCase):
    
    def test_free_cash_flow_calculation(self):
        """Verify normal FCF summation including negative boundaries."""
        self.assertEqual(compute_free_cash_flow(500, -300), 200.0)
        
    def test_pattern_reinvestor(self):
        """Test pattern (+, -, -) with low CFO/PAT ratio maps to Reinvestor."""
        label = classify_capital_allocation(100, -50, -20, cfo_pat_ratio=0.5)
        self.assertEqual(label, "Reinvestor")
        
    def test_pattern_shareholder_returns(self):
        """Test pattern (+, -, -) with high CFO/PAT ratio maps to Shareholder Returns."""
        label = classify_capital_allocation(100, -50, -20, cfo_pat_ratio=1.5)
        self.assertEqual(label, "Shareholder Returns")
        
    def test_pattern_distress_signal(self):
        """Test pattern (-, +, +) maps to Distress Signal."""
        label = classify_capital_allocation(-100, 50, 20)
        self.assertEqual(label, "Distress Signal")
        
    def test_pattern_growth_debt(self):
        """Test pattern (-, -, +) maps to Growth Funded by Debt."""
        label = classify_capital_allocation(-100, -50, 20)
        self.assertEqual(label, "Growth Funded by Debt")
        
    def test_capex_intensity_asset_light(self):
        """Verify CapEx intensity evaluation boundary under < 3%."""
        val, label = compute_capex_intensity(-2, 100)
        self.assertEqual(label, "Asset Light")

if __name__ == "__main__":
    unittest.main()