import pytest
from flask import g, session
from app.supabase_client import get_supabase

@pytest.mark.functional
class TestAuth:
    
    def test_login(self, client, auth):
        """Test login with valid credentials."""
        response = auth.login()
        assert response.status_code == 302  # Redirect after login

        with client:
            client.get('/')
            assert session['user_id'] == '00000000-0000-0000-0000-000000000001'
            assert g.user['id'] == '00000000-0000-0000-0000-000000000001'

    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post(
            '/auth/login',
            data={'username': 'invalid@test.com', 'password': 'password'}
        )
        assert b'Incorrect username or password.' in response.data

    def test_login_invalid_password(self, client):
        """Test login with invalid password."""
        response = client.post(
            '/auth/login',
            data={'username': 'admin@test.com', 'password': 'wrongpassword'}
        )
        assert b'Incorrect username or password.' in response.data

    def test_logout(self, client, auth):
        """Test logout functionality."""
        auth.login()

        with client:
            auth.logout()
            assert 'user_id' not in session

    def test_register(self, client, app):
        """Test registration functionality."""
        # Test successful registration
        response = client.post(
            '/auth/register',
            data={
                'username': 'newuser@test.com',
                'password': 'testpassword',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'employee'
            },
            follow_redirects=True
        )
        assert b'Registration successful' in response.data or b'You have registered successfully' in response.data
        
        # Verify user was added to the database
        with app.app_context():
            supabase = get_supabase()
            response = supabase.table('user_profiles').select('*').eq('email', 'newuser@test.com').execute()
            user = response.data[0] if response.data else None
            assert user is not None
            assert user['first_name'] == 'Test'
            assert user['last_name'] == 'User'
            assert user['role'] == 'employee'
            
            # Clean up test user
            supabase.table('user_profiles').delete().eq('email', 'newuser@test.com').execute()

    def test_register_validate_input(self, client):
        """Test registration with invalid input."""
        # Test empty username
        response = client.post(
            '/auth/register',
            data={
                'username': '',
                'password': 'testpassword',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'employee'
            }
        )
        assert b'Username is required' in response.data or b'Email is required' in response.data
        
        # Test empty password
        response = client.post(
            '/auth/register',
            data={
                'username': 'testuser@test.com',
                'password': '',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'employee'
            }
        )
        assert b'Password is required' in response.data
        
        # Test username already exists
        response = client.post(
            '/auth/register',
            data={
                'username': 'admin@test.com',  # Existing username
                'password': 'testpassword',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'employee'
            }
        )
        assert b'User admin@test.com is already registered' in response.data or b'Email already registered' in response.data 