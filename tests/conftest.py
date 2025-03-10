import os
import sys
import pytest
import tempfile
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, session
from app import create_app
from app.db import get_db, close_db, init_db, init_db_command
from werkzeug.security import generate_password_hash

# Add the application to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def init_test_data():
    """Initialize test data for the database."""
    db = get_db()
    
    # Create test users
    db.execute(
        "INSERT INTO users (username, email, password, role, first_name, last_name) VALUES (?, ?, ?, ?, ?, ?)",
        ('testadmin', 'admin@test.com', generate_password_hash('password'), 'admin', 'Test', 'Admin')
    )
    db.execute(
        "INSERT INTO users (username, email, password, role, first_name, last_name) VALUES (?, ?, ?, ?, ?, ?)",
        ('testuser', 'user@test.com', generate_password_hash('password'), 'employee', 'Test', 'User')
    )
    
    # Create test clients
    db.execute(
        "INSERT INTO clients (name, contact_name, email, phone, address, city, state, zip_code, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ('Test Client 1', 'John Doe', 'john@test.com', '555-1234', '123 Main St', 'Anytown', 'CA', '12345', 'Test client notes')
    )
    db.execute(
        "INSERT INTO clients (name, contact_name, email, phone, address, city, state, zip_code, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ('Test Client 2', 'Jane Smith', 'jane@test.com', '555-5678', '456 Oak Ave', 'Somewhere', 'NY', '67890', 'Another test client')
    )
    
    # Create test projects
    db.execute(
        "INSERT INTO projects (name, client_id, description, status, start_date, end_date, estimated_budget, created_by_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ('Test Project 1', 1, 'Test project description', 'active', '2023-01-01', '2023-12-31', 10000.00, 1)
    )
    db.execute(
        "INSERT INTO projects (name, client_id, description, status, start_date, end_date, estimated_budget, created_by_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ('Test Project 2', 2, 'Another test project', 'planning', '2023-02-01', '2023-11-30', 15000.00, 1)
    )
    
    # Create test invoices
    db.execute(
        """
        INSERT INTO invoices 
        (invoice_number, client_id, project_id, status, issue_date, due_date, 
         subtotal, tax_rate, tax_amount, total_amount, amount_paid, balance_due, 
         notes, terms, created_by_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ('INV-001', 1, 1, 'draft', '2023-03-01', '2023-03-31', 
         1000.00, 8.5, 85.00, 1085.00, 0.00, 1085.00, 
         'Test invoice notes', 'Net 30', 1)
    )
    
    # Create test invoice items
    db.execute(
        """
        INSERT INTO invoice_items
        (invoice_id, description, quantity, unit_price, amount, type, taxable)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (1, 'Labor hours', 10, 100.00, 1000.00, 'labor', True)
    )
    
    # Create test documents
    db.execute(
        """
        INSERT INTO documents
        (name, file_path, file_type, file_size, project_id, description, created_by_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ('Test Document', 'test/path/document.pdf', 'application/pdf', 1024, 1, 'Test document description', 1)
    )
    
    db.commit()

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
        init_db()  # Call init_db directly instead of the Click command
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