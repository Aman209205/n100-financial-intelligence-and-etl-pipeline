# Day 43 — Performance Benchmarking Notes

* **10 Concurrent API Requests Duration:** 0.25 seconds (Target: < 10.0s)
* **Average Latency per Screener Call:** 204.12 ms
* **Company Profile Load Target:** < 3.0 seconds per ticker
* **Database Optimizations:** Added Composite Indexes `(company_id, year)` on existing financial tables.
