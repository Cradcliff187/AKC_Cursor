import pytest
from app.db import get_db

@pytest.mark.functional
class TestClients:
    
    def test_client_list(self, with_admin_user):
        """Test listing clients."""
        response = with_admin_user.get('/clients/')
        assert response.status_code == 200
        assert b'Test Client 1' in response.data
        assert b'Test Client 2' in response.data
    
    def test_client_detail(self, with_admin_user, test_client_id):
        """Test viewing client details."""
        response = with_admin_user.get(f'/clients/{test_client_id}')
        assert response.status_code == 200
        assert b'Test Client 1' in response.data
        assert b'John Doe' in response.data
        assert b'john@example.com' in response.data
    
    def test_create_client(self, with_admin_user, app, test_client_data):
        """Test creating a new client."""
        response = with_admin_user.post(
            '/clients/create',
            data=test_client_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Client created successfully' in response.data or b'Test New Client' in response.data
        
        # Verify client was added to the database
        with app.app_context():
            db = get_db()
            client = db.execute(
                "SELECT * FROM clients WHERE name = 'Test New Client'"
            ).fetchone()
            assert client is not None
            assert client['contact_name'] == 'Jane Smith'
            assert client['email'] == 'janesmith@example.com'
    
    def test_edit_client(self, with_admin_user, app, test_client_id):
        """Test editing an existing client."""
        # Get current client data
        with app.app_context():
            db = get_db()
            client = db.execute(f"SELECT * FROM clients WHERE id = {test_client_id}").fetchone()
        
        # Modify data
        updated_data = {
            'name': client['name'],
            'contact_name': 'John Smith',  # Changed
            'email': client['email'],
            'phone': '555-999-8888',  # Changed
            'address': client['address'],
            'city': client['city'],
            'state': client['state'],
            'zip': client['zip'],
            'notes': 'Updated notes'  # Changed
        }
        
        response = with_admin_user.post(
            f'/clients/{test_client_id}/edit',
            data=updated_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Client updated successfully' in response.data or b'John Smith' in response.data
        
        # Verify client was updated in the database
        with app.app_context():
            db = get_db()
            updated_client = db.execute(
                f"SELECT * FROM clients WHERE id = {test_client_id}"
            ).fetchone()
            assert updated_client['contact_name'] == 'John Smith'
            assert updated_client['phone'] == '555-999-8888'
    
    def test_delete_client(self, with_admin_user, app, test_client_id):
        """Test deactivating a client."""
        response = with_admin_user.post(
            f'/clients/{test_client_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Client deleted successfully' in response.data or b'Client deactivated' in response.data
        
        # Verify client was deactivated in the database
        with app.app_context():
            db = get_db()
            client = db.execute(
                f"SELECT * FROM clients WHERE id = {test_client_id}"
            ).fetchone()
            # Check if client is marked as inactive or deleted
            if 'active' in client.keys():
                assert client['active'] == 0
            else:
                assert client is None
    
    def test_unauthorized_client_access(self, client):
        """Test unauthorized access to client pages."""
        # Try accessing clients without login
        response = client.get('/clients/', follow_redirects=True)
        assert response.status_code == 200
        assert b'Log In' in response.data 