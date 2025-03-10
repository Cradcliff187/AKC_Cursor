import os
import sys
import pytest
import tempfile
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, session
from app import create_app
from app.db import get_db, close_db, init_db_command
from werkzeug.security import generate_password_hash

# Add the application to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SERVER_NAME': 'localhost.localdomain',
        'SECRET_KEY': 'test',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF during testing
        'UPLOAD_FOLDER': tempfile.mkdtemp()  # Temporary folder for uploads
    })

    # Create the database and load test data
    with app.app_context():
        init_db_command()
        init_test_data()

    yield app

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


class AuthActions:
    """Helper class for authentication actions in tests."""
    
    def __init__(self, client):
        self._client = client

    def login(self, username='admin@example.com', password='password'):
        """Log in as the test user."""
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        """Log out the test user."""
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """Authentication fixture for tests."""
    return AuthActions(client)


@pytest.fixture
def admin_user_id():
    """Return the ID of the admin user."""
    return 1


@pytest.fixture
def regular_user_id():
    """Return the ID of the regular user."""
    return 2


@pytest.fixture
def with_admin_user(client, auth):
    """Log in as admin user and set user_id in session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'admin'
    return client


@pytest.fixture
def with_regular_user(client, auth):
    """Log in as regular user and set user_id in session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['user_role'] = 'user'
    return client


@pytest.fixture
def test_client_id():
    """Return the ID of the test client."""
    return 1


@pytest.fixture
def test_project_id():
    """Return the ID of the test project."""
    return 1


@pytest.fixture
def test_invoice_id():
    """Return the ID of the test invoice."""
    return 1


@pytest.fixture
def test_invoice_data():
    """Return test invoice data for creating a new invoice."""
    today = datetime.now().date()
    due_date = today + timedelta(days=30)
    return {
        'client_id': 1,
        'project_id': 1,
        'issue_date': today.isoformat(),
        'due_date': due_date.isoformat(),
        'tax_rate': 8.0,
        'notes': 'Test invoice notes',
        'terms': 'Net 30',
        'footer': 'Thank you for your business!',
        'payment_instructions': 'Please make payments to: AKC Construction LLC'
    }


@pytest.fixture
def test_invoice_item_data():
    """Return test invoice item data for creating a new invoice item."""
    return [
        {
            'description': 'Design Services',
            'quantity': 10,
            'unit_price': 150.00,
            'type': 'Service',
            'taxable': True,
            'sort_order': 1
        },
        {
            'description': 'Construction Materials',
            'quantity': 1,
            'unit_price': 500.00,
            'type': 'Material',
            'taxable': True,
            'sort_order': 2
        }
    ]


@pytest.fixture
def test_payment_data():
    """Return test payment data for creating a new payment."""
    return {
        'invoice_id': 2,  # For the invoice that can accept payments
        'amount': 500.00,
        'payment_date': datetime.now().date().isoformat(),
        'payment_method': 'Credit Card',
        'reference_number': 'TEST-REF-001',
        'notes': 'Test payment',
        'created_by_id': 1
    }


@pytest.fixture
def test_client_data():
    """Return test client data for creating a new client."""
    return {
        'name': 'Test New Client',
        'contact_name': 'Jane Smith',
        'email': 'janesmith@example.com',
        'phone': '555-789-1234',
        'address': '456 Test Ave',
        'city': 'Testville',
        'state': 'TS',
        'zip': '12345',
        'notes': 'This is a test client'
    }


@pytest.fixture
def test_project_data():
    """Return test project data for creating a new project."""
    today = datetime.now().date()
    end_date = today + timedelta(days=90)
    return {
        'name': 'Test New Project',
        'client_id': 1,
        'description': 'This is a test project',
        'status': 'Planning',
        'start_date': today.isoformat(),
        'end_date': end_date.isoformat(),
        'budget': 25000.00,
        'address': '789 Test Blvd',
        'city': 'Testopolis',
        'state': 'TS',
        'zip': '54321'
    }


@pytest.fixture
def test_task_data():
    """Return test task data for creating a new task."""
    today = datetime.now().date()
    due_date = today + timedelta(days=7)
    return {
        'project_id': 1,
        'title': 'Test Task',
        'description': 'This is a test task',
        'status': 'To Do',
        'priority': 'Medium',
        'assigned_to': 2,
        'due_date': due_date.isoformat()
    }


@pytest.fixture
def test_document_data(app):
    """Return test document data for creating a new document."""
    return {
        'name': 'Test Document.pdf',
        'description': 'This is a test document',
        'type': 'PDF',
        'size': 12345,
        'uploaded_by': 1,
        'client_id': 1,
        'project_id': 1
    }


def init_test_data():
    """Initialize the database with test data."""
    db = get_db()
    
    # Create test users
    db.execute(
        "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
        ('admin@example.com', generate_password_hash('password'), 'Admin User', 'admin')
    )
    db.execute(
        "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
        ('user@example.com', generate_password_hash('password'), 'Regular User', 'user')
    )
    
    # Create test clients
    db.execute(
        "INSERT INTO clients (name, contact_name, email, phone, address, city, state, zip, active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ('Test Client 1', 'John Doe', 'john@example.com', '555-123-4567', '123 Main St', 'Anytown', 'NY', '12345', 1)
    )
    db.execute(
        "INSERT INTO clients (name, contact_name, email, phone, address, city, state, zip, active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ('Test Client 2', 'Jane Smith', 'jane@example.com', '555-987-6543', '456 Oak Ave', 'Somewhere', 'CA', '67890', 1)
    )
    
    # Create test projects
    db.execute(
        "INSERT INTO projects (name, client_id, description, status, start_date, end_date, budget) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ('Test Project 1', 1, 'This is a test project', 'In Progress', '2023-01-01', '2023-12-31', 50000.00)
    )
    db.execute(
        "INSERT INTO projects (name, client_id, description, status, start_date, end_date, budget) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ('Test Project 2', 2, 'Another test project', 'Planning', '2023-02-01', '2023-11-30', 75000.00)
    )

    # Create test tasks
    db.execute(
        "INSERT INTO tasks (project_id, title, description, status, priority, assigned_to, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, 'Task 1', 'Complete foundation work', 'In Progress', 'High', 2, '2023-04-15')
    )
    db.execute(
        "INSERT INTO tasks (project_id, title, description, status, priority, assigned_to, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, 'Task 2', 'Finish framing', 'To Do', 'Medium', 2, '2023-05-01')
    )
    
    # Create test invoices
    db.execute(
        """INSERT INTO invoices 
           (invoice_number, client_id, project_id, status, issue_date, due_date, 
            subtotal, tax_rate, tax_amount, total_amount, balance_due)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ('INV-001', 1, 1, 'Draft', '2023-03-01', '2023-04-01', 1000.00, 8.0, 80.00, 1080.00, 1080.00)
    )
    db.execute(
        """INSERT INTO invoices 
           (invoice_number, client_id, project_id, status, issue_date, due_date, 
            subtotal, tax_rate, tax_amount, total_amount, amount_paid, balance_due)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ('INV-002', 2, 2, 'Sent', '2023-03-15', '2023-04-15', 2000.00, 8.0, 160.00, 2160.00, 1000.00, 1160.00)
    )
    
    # Create test invoice items
    db.execute(
        """INSERT INTO invoice_items 
           (invoice_id, description, quantity, unit_price, amount, type, taxable)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (1, 'Design Services', 10, 50.00, 500.00, 'Service', 1)
    )
    db.execute(
        """INSERT INTO invoice_items 
           (invoice_id, description, quantity, unit_price, amount, type, taxable)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (1, 'Construction Materials', 1, 500.00, 500.00, 'Material', 1)
    )
    db.execute(
        """INSERT INTO invoice_items 
           (invoice_id, description, quantity, unit_price, amount, type, taxable)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (2, 'Labor Hours', 40, 50.00, 2000.00, 'Labor', 1)
    )
    
    # Create test payments
    db.execute(
        """INSERT INTO payments
           (invoice_id, amount, payment_date, payment_method, reference_number)
           VALUES (?, ?, ?, ?, ?)""",
        (2, 1000.00, '2023-03-20', 'Credit Card', 'REF12345')
    )
    
    # Create test documents
    db.execute(
        """INSERT INTO documents
           (name, description, type, size, path, uploaded_by, client_id, project_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ('Contract.pdf', 'Project contract', 'PDF', 1024000, 'path/to/contract.pdf', 1, 1, 1)
    )
    db.execute(
        """INSERT INTO documents
           (name, description, type, size, path, uploaded_by, client_id, project_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ('Blueprint.jpg', 'Building blueprint', 'Image', 2048000, 'path/to/blueprint.jpg', 1, 2, 2)
    )

    # Create test bids
    db.execute(
        """INSERT INTO bids
           (client_id, project_name, status, created_by, subtotal, tax_rate, tax_amount, total)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (1, 'Home Renovation', 'Draft', 1, 15000.00, 8.0, 1200.00, 16200.00)
    )
    db.execute(
        """INSERT INTO bids
           (client_id, project_name, status, created_by, subtotal, tax_rate, tax_amount, total)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (2, 'Commercial Building', 'Sent', 1, 50000.00, 8.0, 4000.00, 54000.00)
    )

    # Create test bid items
    db.execute(
        """INSERT INTO bid_items
           (bid_id, description, quantity, unit_price, amount)
           VALUES (?, ?, ?, ?, ?)""",
        (1, 'Demolition', 1, 3000.00, 3000.00)
    )
    db.execute(
        """INSERT INTO bid_items
           (bid_id, description, quantity, unit_price, amount)
           VALUES (?, ?, ?, ?, ?)""",
        (1, 'New Flooring', 1000, 12.00, 12000.00)
    )
    
    # Create test notifications
    db.execute(
        """INSERT INTO notifications
           (user_id, type, title, message, related_id, related_type, is_read)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (2, 'task_assigned', 'New Task Assigned', 'You have been assigned a new task', 1, 'task', 0)
    )
    db.execute(
        """INSERT INTO notifications
           (user_id, type, title, message, related_id, related_type, is_read)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (1, 'payment_received', 'Payment Received', 'A payment has been received for invoice #INV-002', 2, 'invoice', 0)
    )
    
    db.commit() 