import os
import pandas as pd

PROJECT_ROOT = r"C:\N100-platform"
RAW_DIR = os.path.join(PROJECT_ROOT, "raw_data")

def inspect_file(file_name):
    path = os.path.join(RAW_DIR, f"{file_name}.xlsx")
    if os.path.exists(path):
        print(f"\n--- INSPECTING {file_name}.xlsx ---")
        df = pd.read_excel(path, engine='openpyxl')
        
        # Check banner
        if df.columns[0].strip().startswith("Mkt Fintech") or "records" in str(df.columns[0]).lower():
            df = pd.read_excel(path, header=1, engine='openpyxl')
            
        print("Columns found:", list(df.columns))
        print("First 3 rows sample:")
        print(df.head(3).to_string())
    else:
        print(f"File not found: {file_name}.xlsx")

inspect_file("companies")
inspect_file("profitandloss")