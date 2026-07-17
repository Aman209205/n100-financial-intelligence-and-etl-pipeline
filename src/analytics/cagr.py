"""
N100 Financial Intelligence Platform - CAGR Engine
Day 10: Growth Metrics & 6 Corporate Edge Cases Handlers
"""

def compute_cagr(start_value: float, end_value: float, periods: int, actual_years_available: int) -> tuple:
    """
    Computes CAGR handling all 6 financial edge cases required by the Task Board.
    Returns (cagr_value, cagr_flag).
    """
    # Case 6: Less than required years of data
    if actual_years_available < periods:
        return None, "INSUFFICIENT"
        
    if start_value is None or end_value is None:
        return None, "INSUFFICIENT"
        
    start_val = float(start_value)
    end_val = float(end_value)
    
    # Case 5: Zero Base
    if start_val == 0:
        return None, "ZERO_BASE"
        
    # Case 2: Positive to Negative (Decline to Loss)
    if start_val > 0 and end_val <= 0:
        return None, "DECLINE_TO_LOSS"
        
    # Case 3: Negative to Positive (Turnaround)
    if start_val < 0 and end_val > 0:
        return None, "TURNAROUND"
        
    # Case 4: Both Negative
    if start_val < 0 and end_val <= 0:
        return None, "BOTH_NEGATIVE"
        
    # Case 1: Positive + Positive (Normal computation)
    try:
        cagr_value = ((end_val / start_val) ** (1.0 / float(periods)) - 1.0) * 100.0
        return cagr_value, "NORMAL"
    except Exception:
        return None, "ERROR"