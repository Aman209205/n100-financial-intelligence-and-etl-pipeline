"""
N100 Platform - Screener Engine Unit Tests
"""

import os
import sys
import unittest
import pandas as pd

# Dynamic path resolution to ensure imports work across different directory names
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.screener.engine import run_preset_screener


class TestScreenerEngine(unittest.TestCase):

    def test_quality_compounder_preset(self):
        df = run_preset_screener("quality_compounder")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0, "Quality Compounder preset returned empty results.")

    def test_value_pick_preset(self):
        df = run_preset_screener("value_pick")
        self.assertIsInstance(df, pd.DataFrame)

    def test_growth_accelerator_preset(self):
        df = run_preset_screener("growth_accelerator")
        self.assertIsInstance(df, pd.DataFrame)

    def test_debt_free_blue_chip_preset(self):
        df = run_preset_screener("debt_free_blue_chip")
        self.assertIsInstance(df, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()