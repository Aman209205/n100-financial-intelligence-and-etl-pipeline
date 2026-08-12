"""
N100 Platform - OpenAPI Exporter
Day 40 Implementation
"""

import os
import json
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.api.main import app

def export_spec():
    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    openapi_schema = app.openapi()
    spec_path = os.path.join(docs_dir, "openapi.json")
    
    with open(spec_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
        
    print(f"[SUCCESS] OpenAPI spec exported to: {spec_path}")

if __name__ == "__main__":
    export_spec()