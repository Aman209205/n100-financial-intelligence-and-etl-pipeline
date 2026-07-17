"""
N100 Financial Intelligence Platform - Ratio Engine
Day 08: Profitability Calculations & Structural Framework
"""

def compute_net_profit_margin(net_profit: float, sales: float) -> float:
    """Computes NPM. Returns None if sales are 0 or empty."""
    if sales is None or net_profit is None or float(sales) == 0:
        return None
    return (float(net_profit) / float(sales)) * 100.0

def compute_operating_profit_margin(operating_profit: float, sales: float, reported_opm: float = None) -> tuple:
    """
    Computes OPM and cross-checks it against the reported source field.
    Logs warnings if variance shifts beyond absolute > 1%.
    """
    if sales is None or operating_profit is None or float(sales) == 0:
        return None, False
        
    computed_opm = (float(operating_profit) / float(sales)) * 100.0
    mismatch_flag = False
    
    if reported_opm is not None:
        if abs(computed_opm - float(reported_opm)) > 1.0:
            mismatch_flag = True
            
    return computed_opm, mismatch_flag

def compute_return_on_equity(net_profit: float, equity_capital: float, reserves: float) -> float:
    """Computes ROE. Returns None if denominator (equity_capital + reserves) is <= 0."""
    if net_profit is None or equity_capital is None or reserves is None:
        return None
    denominator = float(equity_capital) + float(reserves)
    if denominator <= 0:
        return None
    return (float(net_profit) / denominator) * 100.0

def compute_return_on_capital_employed(ebit: float, equity_capital: float, reserves: float, borrowings: float, sector: str = "General") -> tuple:
    """
    Computes ROCE: EBIT / (Equity + Reserves + Borrowings) * 100
    Applies special relative benchmark context checks if broad_sector is Financials.
    """
    if ebit is None or equity_capital is None or reserves is None or borrowings is None:
        return None, "Insufficient Data"
        
    denominator = float(equity_capital) + float(reserves) + float(borrowings)
    if denominator <= 0:
        return None, "Negative/Zero Capital Base"
        
    computed_roce = (float(ebit) / denominator) * 100.0
    
    # Day 08 Sector-Relative ROCE Benchmarking rule
    if sector is not None and "financial" in sector.lower():
        benchmark_status = "Sector-Relative Evaluation Active"
    else:
        benchmark_status = "Standard Threshold Applied"
        
    return computed_roce, benchmark_status

def compute_return_on_assets(net_profit: float, total_assets: float) -> float:
    """Computes ROA. Returns None if total_assets is equal to 0."""
    if net_profit is None or total_assets is None or float(total_assets) == 0:
        return None
    return (float(net_profit) / float(total_assets)) * 100.0

def compute_debt_to_equity(borrowings: float, equity_capital: float, reserves: float, sector: str = "General") -> tuple:
    """
    Computes Debt-to-Equity ratio and applies high leverage flags.
    Returns (de_ratio, high_leverage_flag).
    """
    if borrowings is None or equity_capital is None or reserves is None:
        return None, False
        
    if float(borrowings) == 0:
        return 0.0, False
        
    denominator = float(equity_capital) + float(reserves)
    if denominator <= 0:
        return None, False
        
    de_ratio = float(borrowings) / denominator
    high_leverage_flag = False
    
    # Financial sector companies structurally high leverage maintain karti hain, isliye unhe exclude karenge
    if de_ratio > 5.0 and (sector is None or "financial" not in sector.lower()):
        high_leverage_flag = True
        
    return de_ratio, high_leverage_flag

def compute_interest_coverage_ratio(operating_profit: float, other_income: float, interest: float) -> tuple:
    """
    Computes ICR and returns (icr_value, icr_label, warning_flag).
    """
    if operating_profit is None or other_income is None or interest is None:
        return None, None, False
        
    if float(interest) == 0:
        return None, "Debt Free", False
        
    ebit = float(operating_profit) + float(other_income)
    icr_value = ebit / float(interest)
    
    icr_label = "Standard"
    warning_flag = False
    
    if icr_value < 1.5:
        warning_flag = True
        
    return icr_value, icr_label, warning_flag

def compute_net_debt(borrowings: float, investments: float) -> float:
    """Computes Net Debt using investments as liquid asset proxy."""
    if borrowings is None or investments is None:
        return None
    return float(borrowings) - float(investments)

def compute_asset_turnover(sales: float, total_assets: float) -> float:
    """Computes Asset Turnover. Returns None if total_assets = 0."""
    if sales is None or total_assets is None or float(total_assets) == 0:
        return None
    return float(sales) / float(total_assets)