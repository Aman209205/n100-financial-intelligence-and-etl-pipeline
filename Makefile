# N100 Financial Analytics Platform - Automation Commands

PYTHON := python
PYTEST := pytest
UVICORN := uvicorn
STREAMLIT := streamlit

.PHONY: help load ratios test report dashboard api clean check-deliverables

help:
	@echo "Available Commands:"
	@echo "  make load        - Load raw Excel files into database"
	@echo "  make ratios      - Generate financial_ratios table"
	@echo "  make test        - Run all 102+ pytest tests and generate HTML report"
	@echo "  make report      - Batch generate all 92 tearsheets, sector, and portfolio PDFs"
	@echo "  make dashboard   - Launch Streamlit dashboard on localhost:8501"
	@echo "  make api         - Launch FastAPI REST server on localhost:8000"
	@echo "  make clean       - Remove cached files (.pyc, __pycache__)"

load:
	$(PYTHON) src/etl/loader.py

ratios:
	$(PYTHON) src/analytics/ratios.py

test:
	set PYTHONPATH=.&& $(PYTEST) tests/ -v --html=reports/pytest_report.html

report:
	$(PYTHON) src/reports/batch_generate.py

dashboard:
	$(STREAMLIT) run src/dashboard/app.py --server.port 8501

api:
	$(UVICORN) src.api.main:app --port 8000 --reload

clean:
	powershell -Command "Get-ChildItem -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force; Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force"