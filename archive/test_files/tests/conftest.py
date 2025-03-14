import os
import sys
import pytest
import tempfile
from datetime import datetime, timedelta
from flask import Flask, session
from app import create_app
from werkzeug.security import generate_password_hash
from supabase import create_client

# Add the application to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def init_test_data(supabase):
    """Initialize test data for the database."""
    # Create test users
    supabase.table('user_profiles').insert({
        'id': '00000000-0000-0000-0000-000000000001',
        'username': 'testadmin',
        'email': 'admin@test.com',
        'role': 'admin',
        'first_name': 'Test',
        'last_name': 'Admin'
    }).execute()
    
    supabase.table('user_profiles').insert({
        'id': '00000000-0000-0000-0000-000000000002',
        'username': 'testuser',
        'email': 'user@test.com',
        'role': 'employee',
        'first_name': 'Test',
        'last_name': 'User'
    }).execute()
    
    # Create test clients
    supabase.table('clients').insert({
        'name': 'Test Client 1',
        'contact_name': 'John Doe',
        'email': 'john@test.com',
        'phone': '555-1234',
        'address': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'zip_code': '12345',
        'notes': 'Test client notes'
    }).execute()
    
    supabase.table('clients').insert({
        'name': 'Test Client 2',
        'contact_name': 'Jane Smith',
        'email': 'jane@test.com',
        'phone': '555-5678',
        'address': '456 Oak Ave',
        'city': 'Somewhere',
        'state': 'NY',
        'zip_code': '67890',
        'notes': 'Another test client'
    }).execute()

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'SERVER_NAME': 'localhost.localdomain',
        'SECRET_KEY': 'test',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF during testing
        'UPLOAD_FOLDER': tempfile.mkdtemp(),  # Temporary folder for uploads
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY')
    })

    # Initialize test data
    with app.app_context():
        from app.supabase_client import get_supabase
        supabase = get_supabase()
        init_test_data(supabase)

    yield app

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

    def login(self, username='admin@test.com', password='password'):
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
    return '00000000-0000-0000-0000-000000000001'

@pytest.fixture
def regular_user_id():
    """Return the ID of the regular user."""
    return '00000000-0000-0000-0000-000000000002'

@pytest.fixture
def with_admin_user(client, auth):
    """Log in as admin user and set user_id in session."""
    with client.session_transaction() as sess:
        sess['user_id'] = '00000000-0000-0000-0000-000000000001'
        sess['user_role'] = 'admin'
    return client

@pytest.fixture
def with_regular_user(client, auth):
    """Log in as regular user and set user_id in session."""
    with client.session_transaction() as sess:
        sess['user_id'] = '00000000-0000-0000-0000-000000000002'
        sess['user_role'] = 'employee'
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