import pytest

def normalize_year(val):
    """Utility normalization function covering various format edge cases."""
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.isdigit() and len(val_str) == 4:
        return int(val_str)
    if 'FY' in val_str.upper():
        clean = val_str.upper().replace('FY', '').replace("'", "").strip()
        if clean.isdigit():
            num = int(clean)
            return 2000 + num if num < 100 else num
    if '-' in val_str:
        parts = val_str.split('-')
        if parts[0].isdigit() and len(parts[0]) == 4:
            return int(parts[0])
    return None

def test_norm_standard_year():
    assert normalize_year(2024) == 2024
    assert normalize_year("2024") == 2024

def test_norm_fy_string():
    assert normalize_year("FY24") == 2024
    assert normalize_year("FY 2024") == 2024
    assert normalize_year("fy23") == 2023

def test_norm_date_range():
    assert normalize_year("2023-24") == 2023
    assert normalize_year("2024-2025") == 2024

def test_norm_edge_cases():
    assert normalize_year(None) is None
    assert normalize_year("") is None
    assert normalize_year("INVALID") is None
    assert normalize_year("123") is None

@pytest.mark.parametrize("input_val,expected", [
    (2020, 2020), ("2021", 2021), ("FY22", 2022), ("FY 2025", 2025),
    ("2021-22", 2021), ("2022-2023", 2022), (None, None), ("abc", None),
    ("1999", 1999), ("FY99", 2099), ("FY 98", 2098)
])
def test_norm_parameterized(input_val, expected):
    assert normalize_year(input_val) == expected