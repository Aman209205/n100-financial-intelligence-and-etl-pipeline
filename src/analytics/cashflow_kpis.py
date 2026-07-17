"""
N100 Financial Intelligence Platform - Cash Flow Engine
Day 11: FCF, CFO Quality Score, CapEx Intensity, and 8-Pattern Classifier
"""

def compute_free_cash_flow(cfo: float, cfi: float) -> float:
    """Computes FCF: Operating Cash Flow + Investing Cash Flow."""
    if cfo is None or cfi is None:
        return None
    return float(cfo) + float(cfi)

def classify_capital_allocation(cfo: float, cfi: float, cff: float, cfo_pat_ratio: float = 0.0) -> str:
    """
    Classifies the corporate capital allocation strategy into one of 8 distinct patterns
    based on the numeric signs of CFO, CFI, and CFF streams.
    """
    if cfo is None or cfi is None or cff is None:
        return "Unknown"
        
    s_cfo = "+" if float(cfo) >= 0 else "-"
    s_cfi = "+" if float(cfi) >= 0 else "-"
    s_cff = "+" if float(cff) >= 0 else "-"
    
    pattern = (s_cfo, s_cfi, s_cff)
    
    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"
    elif pattern == ("+", "+", "-"):
        return "Liquidating Assets"
    elif pattern == ("-", "+", "+"):
        return "Distress Signal"
    elif pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"
    elif pattern == ("+", "+", "+"):
        return "Cash Accumulator"
    elif pattern == ("-", "-", "-"):
        return "Pre-Revenue"
    elif pattern == ("+", "-", "+"):
        return "Mixed"
        
    return "Mixed"

def compute_capex_intensity(cfi: float, sales: float) -> tuple:
    """Computes CapEx Intensity percent and maps to industrial structural definitions."""
    if cfi is None or sales is None or float(sales) == 0:
        return None, "Unknown"
        
    intensity = (abs(float(cfi)) / float(sales)) * 100.0
    
    if intensity < 3.0:
        label = "Asset Light"
    elif intensity <= 8.0:
        label = "Moderate"
    else:
        label = "Capital Intensive"
        
    return intensity, label