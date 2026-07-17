import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/analytics')))
from cagr import compute_cagr

class TestCAGREngine(unittest.TestCase):
    
    def test_normal_cagr(self):
        """Test normal positive to positive growth scenario."""
        cagr, flag = compute_cagr(100, 144, 2, 2)
        self.assertAlmostEqual(cagr, 20.0)
        self.assertEqual(flag, "NORMAL")
        
    def test_decline_to_loss(self):
        """Test Case 2: Positive to Negative."""
        cagr, flag = compute_cagr(100, -20, 3, 3)
        self.assertIsNone(cagr)
        self.assertEqual(flag, "DECLINE_TO_LOSS")
        
    def test_turnaround(self):
        """Test Case 3: Negative to Positive."""
        cagr, flag = compute_cagr(-50, 100, 5, 5)
        self.assertIsNone(cagr)
        self.assertEqual(flag, "TURNAROUND")
        
    def test_both_negative(self):
        """Test Case 4: Both values are negative."""
        cagr, flag = compute_cagr(-100, -50, 3, 3)
        self.assertIsNone(cagr)
        self.assertEqual(flag, "BOTH_NEGATIVE")
        
    def test_zero_base(self):
        """Test Case 5: Starting index is zero."""
        cagr, flag = compute_cagr(0, 150, 5, 5)
        self.assertIsNone(cagr)
        self.assertEqual(flag, "ZERO_BASE")
        
    def test_insufficient_data(self):
        """Test Case 6: Less data points than requested period window."""
        cagr, flag = compute_cagr(100, 200, 5, 3)
        self.assertIsNone(cagr)
        self.assertEqual(flag, "INSUFFICIENT")

if __name__ == "__main__":
    unittest.main()