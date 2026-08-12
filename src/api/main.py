"""
N100 Platform - FastAPI Server Scaffold
Day 38 Implementation
"""

import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import (
    health,
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_logger")

app = FastAPI(
    title="Nifty 100 Financial Analytics Platform API",
    description="REST API for Nifty 100 fundamental data, ratios, screening, clustering, and tearsheets.",
    version="1.0.0"
)

# 1. CORS Middleware (Allow all origins for internal development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Logging Middleware (Method, Path, Response Time)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"Method={request.method} Path={request.url.path} Status={response.status_code} Time={process_time}ms")
    response.headers["X-Process-Time-MS"] = str(process_time)
    return response

# 3. Import & Include Routers with /api/v1 Prefix
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(companies.router, prefix="/api/v1", tags=["Companies"])
app.include_router(screener.router, prefix="/api/v1", tags=["Screener"])
app.include_router(sectors.router, prefix="/api/v1", tags=["Sectors"])
app.include_router(peers.router, prefix="/api/v1", tags=["Peers"])
app.include_router(valuation.router, prefix="/api/v1", tags=["Valuation"])
app.include_router(portfolio.router, prefix="/api/v1", tags=["Portfolio"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])

@app.get("/")
def root():
    return {"message": "Welcome to Nifty 100 Financial Analytics API. Visit /docs for OpenAPI documentation."}