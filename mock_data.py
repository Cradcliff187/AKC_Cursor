"""
Mock data for testing and development when Supabase is unavailable
"""

# Mock activity data
MOCK_ACTIVITY = [
    {"id": 1, "type": "vendor_added", "description": "New vendor 'ABC Supply' added", "created_at": "2025-03-14T10:00:00Z"},
    {"id": 2, "type": "project_updated", "description": "Project 'Office Renovation' status updated to 'In Progress'", "created_at": "2025-03-14T09:30:00Z"},
    {"id": 3, "type": "expense_approved", "description": "Expense #1234 approved for $1,500", "created_at": "2025-03-14T09:00:00Z"},
    {"id": 4, "type": "time_log_added", "description": "8 hours logged for 'Electrical Work'", "created_at": "2025-03-14T08:30:00Z"},
    {"id": 5, "type": "material_ordered", "description": "Order placed for lumber materials", "created_at": "2025-03-14T08:00:00Z"}
]

# Mock metrics data
MOCK_METRICS = {
    "total_projects": 5,
    "active_vendors": 12,
    "pending_approvals": 3
}

# Mock customer data
MOCK_CUSTOMERS = [
    {
        "id": 1,
        "name": "Acme Corporation",
        "contact_name": "John Smith",
        "email": "john.smith@acme.com",
        "phone": "(555) 123-4567",
        "address": "123 Main Street",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701",
        "status": "Active",
        "customer_since": "2023-01-15",
        "payment_terms": "Net 30",
        "credit_limit": 25000.00,
        "notes": "Key client for commercial projects. Prefers email communication.",
        "created_at": "2023-01-15T10:00:00Z",
        "updated_at": "2025-02-20T14:30:00Z"
    },
    {
        "id": 2,
        "name": "TechSolutions Inc",
        "contact_name": "Sarah Johnson",
        "email": "sarah@techsolutions.com",
        "phone": "(555) 987-6543",
        "address": "456 Tech Boulevard",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94105",
        "status": "Active",
        "customer_since": "2023-03-10",
        "payment_terms": "Net 15",
        "credit_limit": 50000.00,
        "notes": "Tech company requiring regular office renovations. Quick payment history.",
        "created_at": "2023-03-10T09:15:00Z",
        "updated_at": "2025-01-15T11:20:00Z"
    },
    {
        "id": 3,
        "name": "Global Retail Group",
        "contact_name": "Michael Williams",
        "email": "m.williams@globalretail.com",
        "phone": "(555) 456-7890",
        "address": "789 Shopping Lane",
        "city": "Chicago",
        "state": "IL",
        "zip": "60601",
        "status": "Active",
        "customer_since": "2023-05-22",
        "payment_terms": "Net 45",
        "credit_limit": 100000.00,
        "notes": "Multiple retail locations requiring consistent buildouts and maintenance.",
        "created_at": "2023-05-22T13:45:00Z",
        "updated_at": "2024-12-10T16:30:00Z"
    },
    {
        "id": 4,
        "name": "Healthcare Partners",
        "contact_name": "Dr. Emily Chen",
        "email": "dr.chen@healthcarepartners.org",
        "phone": "(555) 234-5678",
        "address": "321 Medical Center Drive",
        "city": "Boston",
        "state": "MA",
        "zip": "02115",
        "status": "Inactive",
        "customer_since": "2023-08-05",
        "payment_terms": "Net 30",
        "credit_limit": 75000.00,
        "notes": "Healthcare facility specializing in clinic renovations. Currently on hold due to budget constraints.",
        "created_at": "2023-08-05T08:20:00Z",
        "updated_at": "2025-01-30T10:15:00Z"
    },
    {
        "id": 5,
        "name": "EduLearn Academy",
        "contact_name": "Robert Taylor",
        "email": "r.taylor@edulearn.edu",
        "phone": "(555) 876-5432",
        "address": "555 Campus Circle",
        "city": "Austin",
        "state": "TX",
        "zip": "78712",
        "status": "Active",
        "customer_since": "2023-11-15",
        "payment_terms": "Net 30",
        "credit_limit": 40000.00,
        "notes": "Educational institution with ongoing campus improvement projects.",
        "created_at": "2023-11-15T15:10:00Z",
        "updated_at": "2025-02-28T09:45:00Z"
    }
]

# Mock vendor data
MOCK_VENDORS = [
    {
        "id": 1,
        "name": "ABC Supply",
        "contact_name": "John Smith",
        "email": "john@abcsupply.com",
        "phone": "555-0100",
        "address": "123 Main St, Anytown, USA",
        "material_category": "Building Materials",
        "preferred": True,
        "rating": 5,
        "status": "active",
        "created_at": "2025-03-01T10:00:00Z",
        "updated_at": "2025-03-14T11:00:00Z"
    },
    {
        "id": 2,
        "name": "XYZ Tools",
        "contact_name": "Jane Doe",
        "email": "jane@xyztools.com",
        "phone": "555-0200",
        "address": "456 Oak St, Anytown, USA",
        "material_category": "Tools & Equipment",
        "preferred": False,
        "rating": 4,
        "status": "active",
        "created_at": "2025-03-02T10:00:00Z",
        "updated_at": "2025-03-14T09:00:00Z"
    }
]

# Mock expense data
MOCK_EXPENSES = [
    {
        "id": 1,
        "date": "2025-03-14",
        "vendor_id": 1,
        "vendor_name": "ABC Supply",
        "project_id": 1,
        "project_name": "Office Renovation",
        "category": "Materials",
        "description": "Lumber and building materials",
        "amount": 1500.00,
        "status": "approved",
        "receipt_url": "/static/mock/receipts/receipt1.pdf",
        "created_at": "2025-03-14T10:00:00Z",
        "updated_at": "2025-03-14T11:00:00Z"
    },
    {
        "id": 2,
        "date": "2025-03-14",
        "vendor_id": 2,
        "vendor_name": "XYZ Tools",
        "project_id": 1,
        "project_name": "Office Renovation",
        "category": "Equipment",
        "description": "Power tools rental",
        "amount": 750.00,
        "status": "pending",
        "receipt_url": "/static/mock/receipts/receipt2.pdf",
        "created_at": "2025-03-14T09:00:00Z",
        "updated_at": "2025-03-14T09:00:00Z"
    }
]

# Mock project data
MOCK_PROJECTS = [
    {
        "id": 1,
        "name": "Office Renovation",
        "client_name": "ABC Corp",
        "status": "in_progress",
        "start_date": "2025-03-01",
        "end_date": "2025-06-30",
        "budget": 50000.00,
        "description": "Complete office renovation including electrical and plumbing",
        "created_at": "2025-03-01T10:00:00Z",
        "updated_at": "2025-03-14T11:00:00Z"
    },
    {
        "id": 2,
        "name": "Warehouse Construction",
        "client_name": "XYZ Logistics",
        "status": "planning",
        "start_date": "2025-04-01",
        "end_date": "2025-12-31",
        "budget": 200000.00,
        "description": "New warehouse construction project",
        "created_at": "2025-03-10T10:00:00Z",
        "updated_at": "2025-03-14T09:00:00Z"
    }
]

# Vendor categories and statuses
VENDOR_CATEGORIES = [
    "Building Materials",
    "Electrical",
    "Plumbing",
    "HVAC",
    "Landscaping",
    "Tools and Equipment",
    "Safety Equipment",
    "Office Supplies",
    "Consulting Services",
    "Other"
]

VENDOR_STATUSES = [
    "Active",
    "Inactive",
    "Pending Review",
    "Blacklisted"
]

# Expense categories and statuses
EXPENSE_CATEGORIES = [
    "Materials",
    "Labor",
    "Equipment Rental",
    "Transportation",
    "Permits and Licenses",
    "Insurance",
    "Office Supplies",
    "Professional Services",
    "Utilities",
    "Other"
]

EXPENSE_STATUSES = [
    "Pending",
    "Approved",
    "Rejected",
    "Paid",
    "Void"
] 