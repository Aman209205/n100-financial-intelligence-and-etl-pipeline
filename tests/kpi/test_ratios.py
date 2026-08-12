import pytest

def calc_roe(pat, equity):
    if equity is None or equity <= 0:
        return None
    return round((pat / equity) * 100.0, 2)

def calc_de(debt, equity):
    if equity is None or equity <= 0:
        return None
    if debt == 0:
        return 0.0
    return round(debt / equity, 2)

def calc_icr(ebit, interest):
    if interest is None or interest == 0:
        return None
    return round(ebit / interest, 2)

def test_roe_positive_equity():
    assert calc_roe(100, 500) == 20.0

def test_roe_negative_equity():
    assert calc_roe(100, -500) is None

def test_roe_zero_equity():
    assert calc_roe(100, 0) is None

def test_de_debt_free():
    assert calc_de(0, 500) == 0.0

def test_de_leveraged():
    assert calc_de(1000, 500) == 2.0

def test_icr_zero_interest():
    assert calc_icr(500, 0) is None

def test_icr_normal():
    assert calc_icr(500, 50) == 10.0

@pytest.mark.parametrize("pat,equity,expected", [
    (50, 200, 25.0), (0, 100, 0.0), (-10, 100, -10.0), (100, 0, None),
    (100, -10, None), (15, 60, 25.0), (200, 800, 25.0), (30, 100, 30.0),
    (5, 50, 10.0), (12, 40, 30.0), (100, 1000, 10.0), (1, 10, 10.0), (90, 300, 30.0)
])
def test_roe_parameterized(pat, equity, expected):
    assert calc_roe(pat, equity) == expected