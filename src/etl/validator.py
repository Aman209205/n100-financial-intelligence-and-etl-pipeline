import pandas as pd
import numpy as np

class DataValidator:
    def __init__(self):
        self.failures = []

    def log_failure(self, rule_id: str, severity: str, table: str, column: str, entity_id: str, message: str):
        self.failures.append({
            "rule_id": rule_id,
            "severity": severity,
            "table": table,
            "column": column,
            "entity_id": entity_id,
            "message": message
        })

    def validate_companies(self, df: pd.DataFrame):
        table_name = "companies"
        for idx, row in df.iterrows():
            cid = str(row.get("company_id", "")).strip()
            if cid == "" or pd.isna(row.get("company_id")):
                self.log_failure("DQ-01", "CRITICAL", table_name, "company_id", cid, "Primary Key is missing or null")
            
            url = str(row.get("website_url", "")).strip() if pd.notna(row.get("website_url")) else ""
            if url and not url.startswith(("http://", "https://")):
                self.log_failure("DQ-12", "WARNING", table_name, "website_url", cid, f"Invalid URL format: {url}")

    def validate_financials(self, df: pd.DataFrame, table_name: str):
        for idx, row in df.iterrows():
            cid = str(row.get("company_id", "")).strip()
            year_val = row.get("year", 0)
            
            try:
                year = int(float(year_val)) if pd.notna(year_val) else 0
            except:
                year = 0
                
            entity_key = f"{cid}_{year}"

            if cid == "" or year == 0:
                self.log_failure("DQ-02", "CRITICAL", table_name, "company_id/year", entity_key, "Composite PK contains null or zero values")

            if table_name == "profitandloss" and "sales" in df.columns:
                sales = row.get("sales", 0)
                if pd.notna(sales) and isinstance(sales, (int, float)) and sales < 0:
                    self.log_failure("DQ-06", "WARNING", table_name, "sales", entity_key, f"Sales value cannot be negative: {sales}")

            if table_name == "balancesheet" and "total_assets" in df.columns and "total_liabilities_equity" in df.columns:
                assets = row.get("total_assets", 0)
                liab = row.get("total_liabilities_equity", 0)
                if pd.notna(assets) and pd.notna(liab):
                    try:
                        if abs(float(assets) - float(liab)) > 0.01:
                            self.log_failure("DQ-04", "CRITICAL", table_name, "balance_check", entity_key, f"Balance sheet mismatch: Assets ({assets}) != Liab+Eq ({liab})")
                    except:
                        pass

            if table_name == "profitandloss" and "opm_percent" in df.columns and "sales" in df.columns and "operating_profit" in df.columns:
                opm = row.get("opm_percent", 0)
                sales = row.get("sales", 0)
                op = row.get("operating_profit", 0)
                if pd.notna(sales) and pd.notna(op) and pd.notna(opm):
                    try:
                        s_f, o_f, opm_f = float(sales), float(op), float(opm)
                        if s_f > 0:
                            calculated_opm = (o_f / s_f) * 100
                            if abs(opm_f - calculated_opm) > 1.0:
                                self.log_failure("DQ-05", "WARNING", table_name, "opm_percent", entity_key, f"OPM mismatch. Reported: {opm_f}%, Calculated: {calculated_opm:.2f}%")
                    except:
                        pass

    def save_failures(self, output_path: str = "output/validation_failures.csv"):
        if self.failures:
            df_fail = pd.DataFrame(self.failures)
            df_fail.to_csv(output_path, index=False)
            print(f"[DATA QUALITY] Generated report with {len(self.failures)} violations at {output_path}")
        else:
            df_fail = pd.DataFrame(columns=["rule_id", "severity", "table", "column", "entity_id", "message"])
            df_fail.to_csv(output_path, index=False)
            print("[DATA QUALITY] Perfect execution: 0 data quality violations detected.")