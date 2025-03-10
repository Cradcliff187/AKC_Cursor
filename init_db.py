# Create subcontractors table
cursor.execute('''
CREATE TABLE IF NOT EXISTS subcontractors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company_name TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    specialty TEXT,
    rate_type TEXT,
    hourly_rate REAL,
    tax_id TEXT,
    payment_terms TEXT,
    notes TEXT,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
)
''')

# Create subcontractor_projects table
cursor.execute('''
CREATE TABLE IF NOT EXISTS subcontractor_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcontractor_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    contract_amount REAL,
    contract_type TEXT,
    status TEXT DEFAULT 'Active',
    FOREIGN KEY (subcontractor_id) REFERENCES subcontractors (id),
    FOREIGN KEY (project_id) REFERENCES projects (id)
)
''')

# Create subcontractor_invoices table
cursor.execute('''
CREATE TABLE IF NOT EXISTS subcontractor_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcontractor_id INTEGER NOT NULL,
    project_id INTEGER,
    invoice_number TEXT,
    invoice_date DATE NOT NULL,
    due_date DATE,
    amount REAL NOT NULL,
    paid_amount REAL DEFAULT 0,
    description TEXT,
    status TEXT DEFAULT 'Pending',
    file_path TEXT,
    original_filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (subcontractor_id) REFERENCES subcontractors (id),
    FOREIGN KEY (project_id) REFERENCES projects (id)
)
''')

# Create vendors table
cursor.execute('''
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    vendor_type TEXT,
    payment_terms TEXT,
    tax_id TEXT,
    notes TEXT,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
)
''')

# Create purchases table
cursor.execute('''
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    project_id INTEGER,
    purchase_date DATE NOT NULL,
    invoice_number TEXT,
    amount REAL NOT NULL,
    payment_status TEXT DEFAULT 'Pending',
    description TEXT,
    category TEXT,
    receipt_path TEXT,
    original_filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors (id),
    FOREIGN KEY (project_id) REFERENCES projects (id)
)
''')

# Insert sample subcontractors
sample_subcontractors = [
    ('John Smith Electrical', 'Smith Electrical LLC', 'John Smith', 'john@smithelectrical.com', '555-123-4567', '123 Main St, Anytown, USA', 'Electrical', 'Hourly', 75.00, '12-3456789', 'Net 30', 'Reliable electrical contractor with 15+ years experience', 'Active'),
    ('Mike\'s Plumbing', 'Mike\'s Plumbing Services', 'Mike Johnson', 'mike@mikesplumbing.com', '555-234-5678', '456 Oak Ave, Anytown, USA', 'Plumbing', 'Hourly', 65.00, '23-4567890', 'Net 15', 'Specializes in commercial plumbing systems', 'Active'),
    ('ABC HVAC Solutions', 'ABC HVAC Inc.', 'Robert Williams', 'robert@abchvac.com', '555-345-6789', '789 Pine Rd, Anytown, USA', 'HVAC', 'Fixed', None, '34-5678901', 'Net 30', 'Full service heating and cooling contractor', 'Active'),
    ('Quality Carpentry', 'Quality Carpentry LLC', 'David Brown', 'david@qualitycarpentry.com', '555-456-7890', '101 Cedar Ln, Anytown, USA', 'Carpentry', 'Per Project', None, '45-6789012', 'Net 45', 'Custom cabinetry and finish carpentry', 'Active'),
    ('Superior Roofing', 'Superior Roofing Co.', 'James Wilson', 'james@superiorroofing.com', '555-567-8901', '202 Maple Dr, Anytown, USA', 'Roofing', 'Per Project', None, '56-7890123', 'Net 30', 'Commercial and residential roofing specialist', 'Active')
]

cursor.executemany('''
INSERT INTO subcontractors (name, company_name, contact_person, email, phone, address, specialty, rate_type, hourly_rate, tax_id, payment_terms, notes, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', sample_subcontractors)

# Insert sample vendors
sample_vendors = [
    ('BuildRight Materials', 'Sarah Johnson', 'sales@buildright.com', '555-987-6543', '100 Commerce Way, Anytown, USA', 'Materials', 'Net 30', '67-8901234', 'Primary supplier for lumber and building materials', 'Active'),
    ('Pro Tools Supply', 'Mark Davis', 'mark@protoolssupply.com', '555-876-5432', '200 Industrial Blvd, Anytown, USA', 'Tools', 'Net 15', '78-9012345', 'Professional-grade tools and equipment', 'Active'),
    ('City Electric Supply', 'Lisa Chen', 'lisa@cityelectric.com', '555-765-4321', '300 Power Ave, Anytown, USA', 'Materials', 'Net 30', '89-0123456', 'Electrical supplies and fixtures', 'Active'),
    ('Office Plus', 'Tom Wilson', 'tom@officeplus.com', '555-654-3210', '400 Business Park, Anytown, USA', 'Office Supplies', 'COD', '90-1234567', 'Office supplies and furniture', 'Active'),
    ('Equipment Rentals Inc.', 'Jessica Miller', 'jessica@equipmentrentals.com', '555-543-2109', '500 Machinery Rd, Anytown, USA', 'Equipment', 'Due on Receipt', '01-2345678', 'Heavy equipment rental for construction projects', 'Active')
]

cursor.executemany('''
INSERT INTO vendors (name, contact_person, email, phone, address, vendor_type, payment_terms, tax_id, notes, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', sample_vendors)

# Insert sample subcontractor projects (linking subcontractors to projects)
sample_subcontractor_projects = [
    (1, 1, '2023-01-15', '2023-03-15', 12000.00, 'Fixed', 'Active'),  # John Smith Electrical on Office Renovation
    (2, 1, '2023-01-20', '2023-02-28', 8500.00, 'Fixed', 'Active'),   # Mike's Plumbing on Office Renovation
    (3, 2, '2023-02-01', '2023-04-30', 15000.00, 'Fixed', 'Active'),  # ABC HVAC on Residential Construction
    (4, 3, '2023-03-10', '2023-05-15', 9000.00, 'Fixed', 'Active'),   # Quality Carpentry on Commercial Remodel
    (5, 2, '2023-04-01', '2023-06-30', 18000.00, 'Fixed', 'Active')   # Superior Roofing on Residential Construction
]

cursor.executemany('''
INSERT INTO subcontractor_projects (subcontractor_id, project_id, start_date, end_date, contract_amount, contract_type, status)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', sample_subcontractor_projects)

# Insert sample subcontractor invoices
sample_subcontractor_invoices = [
    (1, 1, 'INV-2023-001', '2023-02-15', '2023-03-15', 6000.00, 6000.00, 'First payment for electrical work', 'Paid', None, None),
    (1, 1, 'INV-2023-002', '2023-03-20', '2023-04-20', 6000.00, 0.00, 'Final payment for electrical work', 'Pending', None, None),
    (2, 1, 'INV-2023-003', '2023-02-28', '2023-03-28', 8500.00, 8500.00, 'Complete plumbing installation', 'Paid', None, None),
    (3, 2, 'INV-2023-004', '2023-03-15', '2023-04-15', 7500.00, 7500.00, 'HVAC system installation - 50%', 'Paid', None, None),
    (3, 2, 'INV-2023-005', '2023-04-30', '2023-05-30', 7500.00, 0.00, 'HVAC system installation - Final', 'Pending', None, None)
]

cursor.executemany('''
INSERT INTO subcontractor_invoices (subcontractor_id, project_id, invoice_number, invoice_date, due_date, amount, paid_amount, description, status, file_path, original_filename)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', sample_subcontractor_invoices)

# Insert sample purchases
sample_purchases = [
    (1, 1, '2023-01-10', 'PO-2023-001', 5000.00, 'Paid', 'Lumber and building materials for office renovation', 'Materials', None, None),
    (2, 2, '2023-02-05', 'PO-2023-002', 1200.00, 'Paid', 'Power tools for residential construction', 'Tools', None, None),
    (3, 1, '2023-01-25', 'PO-2023-003', 3500.00, 'Paid', 'Electrical supplies for office renovation', 'Materials', None, None),
    (4, 3, '2023-03-01', 'PO-2023-004', 500.00, 'Paid', 'Office supplies for project management', 'Office Supplies', None, None),
    (5, 2, '2023-02-15', 'PO-2023-005', 2500.00, 'Paid', 'Excavator rental for residential construction', 'Equipment', None, None)
]

cursor.executemany('''
INSERT INTO purchases (vendor_id, project_id, purchase_date, invoice_number, amount, payment_status, description, category, receipt_path, original_filename)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', sample_purchases) 