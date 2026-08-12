import pytest
import pandas as pd

def check_dq_rule_negative_revenue(df):
    failures = df[df['revenue'] < 0]
    return len(failures)

def check_dq_rule_de_threshold(df, is_financial=False):
    if is_financial:
        return 0
    failures = df[df['debt_to_equity'] > 5.0]
    return len(failures)

def test_dq_negative_revenue_pass():
    df = pd.DataFrame([{'revenue': 100}, {'revenue': 500}])
    assert check_dq_rule_negative_revenue(df) == 0

def test_dq_negative_revenue_fail():
    df = pd.DataFrame([{'revenue': -100}, {'revenue': 500}])
    assert check_dq_rule_negative_revenue(df) == 1

def test_dq_de_high_non_financial():
    df = pd.DataFrame([{'debt_to_equity': 6.0}, {'debt_to_equity': 1.0}])
    assert check_dq_rule_de_threshold(df, is_financial=False) == 1

def test_dq_de_high_financial_ignored():
    df = pd.DataFrame([{'debt_to_equity': 6.0}, {'debt_to_equity': 1.0}])
    assert check_dq_rule_de_threshold(df, is_financial=True) == 0

@pytest.mark.parametrize("rev,expected_failures", [
    (100, 0), (0, 0), (-1, 1), (-500, 1), (10000, 0), (50, 0),
    (-10, 1), (0.1, 0), (-0.1, 1), (999, 0)
])
def test_dq_revenue_param(rev, expected_failures):
    df = pd.DataFrame([{'revenue': rev}])
    assert check_dq_rule_negative_revenue(df) == expected_failures