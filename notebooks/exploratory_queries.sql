-- ====================================================================
-- N100 PLATFORM - DAY 07: EXPLORATORY DATA ANALYSIS QUERIES
-- ====================================================================

-- 1. Master verification: Total number of active companies in platform
SELECT COUNT(*) AS total_companies FROM companies;

-- 2. Sector Distribution: Grouping companies by their industry sector
SELECT sector, COUNT(*) AS company_count 
FROM companies 
GROUP BY sector 
ORDER BY company_count DESC;

-- 3. High Performers Check: Top 5 companies with maximum net profit in P&L records
SELECT c.company_name, c.ticker, p.year, p.net_profit 
FROM profitandloss p
JOIN companies c ON p.company_id = c.company_id
ORDER BY p.net_profit DESC 
LIMIT 5;

-- 4. Profitability Margin Test: Companies maintaining operating profit margin (OPM) above 25%
SELECT DISTINCT c.company_name, c.ticker, p.opm_percent
FROM profitandloss p
JOIN companies c ON p.company_id = c.company_id
WHERE p.opm_percent > 25.0
ORDER BY p.opm_percent DESC;

-- 5. Asset Liabilities Solvency Test: Checking balance sheet configurations for current records
SELECT c.company_name, b.year, b.total_assets, b.total_liabilities_equity
FROM balancesheet b
JOIN companies c ON b.company_id = c.company_id
LIMIT 10;

-- 6. Liquidity Health Test: Top companies managing positive operating cash flows
SELECT c.company_name, cf.year, cf.operating_cash_flow
FROM cashflow cf
JOIN companies c ON cf.company_id = c.company_id
WHERE cf.operating_cash_flow > 0
ORDER BY cf.operating_cash_flow DESC
LIMIT 5;

-- 7. Valuation Multiples Rank: Companies sorted by lowest P/E ratio (Undervalued stocks indicator)
SELECT c.company_name, r.year, r.pe_ratio, r.roe_percent
FROM financial_ratios r
JOIN companies c ON r.company_id = c.company_id
WHERE r.pe_ratio > 0
ORDER BY r.pe_ratio ASC
LIMIT 10;

-- 8. High Volume Market Triggers: Dates and symbols where stock trading volume crossed baseline averages
SELECT c.company_name, s.date, s.close_price, s.volume
FROM stock_prices s
JOIN companies c ON s.company_id = c.company_id
ORDER BY s.volume DESC
LIMIT 10;

-- 9. Corporate Documentation Coverage: Counting document counts linked per corporate group
SELECT c.company_name, COUNT(d.document_id) AS total_documents_uploaded
FROM documents d
JOIN companies c ON d.company_id = c.company_id
GROUP BY c.company_name
ORDER BY total_documents_uploaded DESC;

-- 10. Relational Competitive Matrix: Peer structural pairs verification
SELECT c1.company_name AS target_company, c2.company_name AS peer_competitor
FROM peer_groups pg
JOIN companies c1 ON pg.company_id = c1.company_id
JOIN companies c2 ON pg.peer_company_id = c2.company_id
LIMIT 10;