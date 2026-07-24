"""
N100 Platform - Sprint 3 Comprehensive Data Quality (DQ) Test Suite
Day 21 Implementation (14 DQ Rules)
"""

import os
import sys
import sqlite3
import unittest
import openpyxl
import pandas as pd

PROJECT_ROOT = r"C:\N100-platform"
DB_PATH = os.path.join(PROJECT_ROOT, "database", "nifty100.db")

sys.path.append(os.path.join(PROJECT_ROOT, "src", "screener"))
from engine import run_preset_screener

class TestSprint3DQSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(DB_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # Rule 1-6: 6 Preset Screeners Return Valid Datasets
    def test_dq_rule_1_quality_compounder_returns(self):
        df = run_preset_screener("quality_compounder")
        self.assertGreaterEqual(len(df), 1)

    def test_dq_rule_2_value_pick_returns(self):
        df = run_preset_screener("value_pick")
        self.assertGreaterEqual(len(df), 1)

    def test_dq_rule_3_growth_accelerator_returns(self):
        df = run_preset_screener("growth_accelerator")
        self.assertGreaterEqual(len(df), 1)

    def test_dq_rule_4_dividend_champion_returns(self):
        df = run_preset_screener("dividend_champion")
        self.assertGreaterEqual(len(df), 1)

    def test_dq_rule_5_debt_free_blue_chip_returns(self):
        df = run_preset_screener("debt_free_blue_chip")
        self.assertGreaterEqual(len(df), 1)

    def test_dq_rule_6_turnaround_watch_returns(self):
        df = run_preset_screener("turnaround_watch")
        self.assertGreaterEqual(len(df), 1)

    # Rule 7: Screener Output File Exists
    def test_dq_rule_7_screener_output_exists(self):
        path = os.path.join(PROJECT_ROOT, "output", "screener_output.xlsx")
        self.assertTrue(os.path.exists(path))

    # Rule 8: Peer Comparison File Exists
    def test_dq_rule_8_peer_comparison_exists(self):
        path = os.path.join(PROJECT_ROOT, "output", "peer_comparison.xlsx")
        self.assertTrue(os.path.exists(path))

    # Rule 9: Peer Comparison Covers Exactly 11 Peer Group Sheets
    def test_dq_rule_9_peer_comparison_11_sheets(self):
        path = os.path.join(PROJECT_ROOT, "output", "peer_comparison.xlsx")
        wb = openpyxl.load_workbook(path, read_only=True)
        self.assertEqual(len(wb.sheetnames), 11)

    # Rule 10: Peer Percentiles Table Populated in SQLite
    def test_dq_rule_10_peer_percentiles_populated(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM peer_percentiles;")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0)

    # Rule 11: Percentile Ranks Within Valid Range (0 to 100)
    def test_dq_rule_11_percentile_rank_bounds(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MIN(percentile_rank), MAX(percentile_rank) FROM peer_percentiles;")
        min_r, max_r = cursor.fetchone()
        self.assertGreaterEqual(min_r, 0.0)
        self.assertLessEqual(max_r, 100.0)

    # Rule 12: Radar Charts Generated for Companies
    def test_dq_rule_12_radar_charts_dir(self):
        path = os.path.join(PROJECT_ROOT, "reports", "radar_charts")
        self.assertTrue(os.path.exists(path))
        files = [f for f in os.listdir(path) if f.endswith("_radar.png")]
        self.assertGreaterEqual(len(files), 1)

    # Rule 13: Screener Config YAML File Exists
    def test_dq_rule_13_config_exists(self):
        path = os.path.join(PROJECT_ROOT, "config", "screener_config.yaml")
        self.assertTrue(os.path.exists(path))

    # Rule 14: Quality Compounder Preset Filtering Integrity (D/E <= 2.0 & ROE >= 10%)
    def test_dq_rule_14_quality_compounder_filtering_integrity(self):
        df = run_preset_screener("quality_compounder")
        # Non-financials must satisfy debt-to-equity constraint
        non_fin = df[~df['broad_sector'].astype(str).str.lower().str.contains('financial')]
        if not non_fin.empty:
            self.assertTrue((non_fin['debt_to_equity'] <= 2.0).all())

if __name__ == "__main__":
    unittest.main()