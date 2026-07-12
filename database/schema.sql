PRAGMA foreign_keys = ON;

-- 1. Core Companies Table
CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT,
    website_url TEXT
);

-- 2. Profit & Loss Table
CREATE TABLE IF NOT EXISTS profitandloss (
    company_id TEXT,
    year INTEGER,
    sales REAL,
    operating_profit REAL,
    opm_percent REAL,
    net_profit REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 3. Balance Sheet Table
CREATE TABLE IF NOT EXISTS balancesheet (
    company_id TEXT,
    year INTEGER,
    total_assets REAL,
    total_liabilities_equity REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 4. Cash Flow Table
CREATE TABLE IF NOT EXISTS cashflow (
    company_id TEXT,
    year INTEGER,
    operating_cash_flow REAL,
    investing_cash_flow REAL,
    financing_cash_flow REAL,
    net_cash_flow REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 5. Financial Ratios Table
CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id TEXT,
    year INTEGER,
    pe_ratio REAL,
    pb_ratio REAL,
    roe_percent REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 6. Stock Prices Table
CREATE TABLE IF NOT EXISTS stock_prices (
    company_id TEXT,
    date TEXT,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,
    PRIMARY KEY (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 7. Analysis Table
CREATE TABLE IF NOT EXISTS analysis (
    company_id TEXT PRIMARY KEY,
    summary TEXT,
    recommendation TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 8. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    company_id TEXT,
    document_type TEXT,
    file_url TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 9. Pros and Cons Table
CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT,
    type TEXT, -- 'PRO' or 'CON'
    point TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 10. Peer Groups Table
CREATE TABLE IF NOT EXISTS peer_groups (
    company_id TEXT,
    peer_company_id TEXT,
    PRIMARY KEY (company_id, peer_company_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    FOREIGN KEY (peer_company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);