import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/screener')))
from engine import run_preset_screener

class TestScreenerEngine(unittest.TestCase):

    def test_quality_compounder_preset(self):
        df = run_preset_screener("quality_compounder")
        self.assertGreaterEqual(len(df), 1)

    def test_value_pick_preset(self):
        df = run_preset_screener("value_pick")
        self.assertGreaterEqual(len(df), 1)

    def test_growth_accelerator_preset(self):
        df = run_preset_screener("growth_accelerator")
        self.assertGreaterEqual(len(df), 1)

    def test_debt_free_blue_chip_preset(self):
        df = run_preset_screener("debt_free_blue_chip")
        self.assertGreaterEqual(len(df), 1)

if __name__ == "__main__":
    unittest.main()