import re

def normalize_ticker(ticker: str) -> str:
    """
    Standardizes stock tickers by removing special characters and spaces, 
    then converting them to uppercase.
    """
    if not isinstance(ticker, str):
        return ""
    return re.sub(r'[^A-Za-z0-9]', '', ticker).upper()

def normalize_year(year_val) -> int:
    """
    Extracts a standard 4-digit YYYY integer from various formats like FY2024, 2024-25, or floats.
    """
    if year_val is None or str(year_val).strip() == "":
        return 0
    
    str_val = str(year_val).strip()
    
    # Check for any 4-digit year pattern (e.g., 2024)
    match = re.search(r'\b(20\d{2})\b', str_val)
    if match:
        return int(match.group(1))
    
    # Handle float numbers represented as strings (e.g., "2024.0")
    try:
        float_val = float(str_val)
        if 2000 <= float_val <= 2100:
            return int(float_val)
    except ValueError:
        pass
        
    return 0