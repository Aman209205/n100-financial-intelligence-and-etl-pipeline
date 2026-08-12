import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "db_row_counts" in data

def test_get_companies():
    res = client.get("/api/v1/companies")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_company_by_ticker():
    res = client.get("/api/v1/companies/TCS")
    assert res.status_code == 200
    data = res.json()
    assert data["company_id"] == "TCS"

def test_get_invalid_company():
    res = client.get("/api/v1/companies/INVALID_TICKER_X")
    assert res.status_code == 404

def test_screener_endpoint():
    res = client.get("/api/v1/screener?min_roe=15")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_sectors_endpoint():
    res = client.get("/api/v1/sectors")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_portfolio_stats_endpoint():
    res = client.get("/api/v1/portfolio/stats")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)