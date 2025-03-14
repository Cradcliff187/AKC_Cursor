-- Create bids table to store proposals and estimates
CREATE TABLE IF NOT EXISTS bids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    client_id INTEGER,
    project_id INTEGER,
    created_by_id INTEGER,
    status TEXT DEFAULT 'Draft',
    version INTEGER DEFAULT 1,
    bid_number TEXT,
    proposal_date DATE NOT NULL,
    valid_until DATE,
    total_amount REAL DEFAULT 0,
    labor_cost REAL DEFAULT 0,
    material_cost REAL DEFAULT 0,
    overhead_cost REAL DEFAULT 0,
    profit_margin REAL DEFAULT 0,
    description TEXT,
    notes TEXT,
    terms_and_conditions TEXT,
    client_message TEXT,
    client_response TEXT,
    client_response_date DATE,
    file_path TEXT,
    original_filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id),
    FOREIGN KEY (project_id) REFERENCES projects (id),
    FOREIGN KEY (created_by_id) REFERENCES users (id)
);

-- Create bid_items table to store line items for bids
CREATE TABLE IF NOT EXISTS bid_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bid_id INTEGER NOT NULL,
    item_type TEXT DEFAULT 'Labor',
    category TEXT,
    description TEXT NOT NULL,
    quantity REAL DEFAULT 1,
    unit TEXT DEFAULT 'Hours',
    unit_cost REAL DEFAULT 0,
    total_cost REAL DEFAULT 0,
    markup_percentage REAL DEFAULT 0,
    markup_amount REAL DEFAULT 0,
    total_price REAL DEFAULT 0,
    notes TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bid_id) REFERENCES bids (id) ON DELETE CASCADE
);

-- Create bid_versions table to track changes to bids
CREATE TABLE IF NOT EXISTS bid_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bid_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    data TEXT NOT NULL, -- JSON serialized bid data
    created_by_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bid_id) REFERENCES bids (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_id) REFERENCES users (id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_bids_client_id ON bids(client_id);
CREATE INDEX IF NOT EXISTS idx_bids_project_id ON bids(project_id);
CREATE INDEX IF NOT EXISTS idx_bids_status ON bids(status);
CREATE INDEX IF NOT EXISTS idx_bid_items_bid_id ON bid_items(bid_id);
CREATE INDEX IF NOT EXISTS idx_bid_versions_bid_id ON bid_versions(bid_id); 