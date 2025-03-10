import pytest
from flask import g, session
from app.db import get_db

@pytest.mark.functional
class TestAuth:
    
    def test_login(self, client, auth):
        """Test login with valid credentials."""
        response = auth.login()
        assert response.status_code == 302  # Redirect after login

        with client:
            client.get('/')
            assert session['user_id'] == 1
            assert g.user['id'] == 1

    def test_login_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post(
            '/auth/login',
            data={'username': 'invalid@example.com', 'password': 'password'}
        )
        assert b'Incorrect username or password.' in response.data

    def test_login_invalid_password(self, client):
        """Test login with invalid password."""
        response = client.post(
            '/auth/login',
            data={'username': 'admin@example.com', 'password': 'wrongpassword'}
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
                'username': 'testuser@example.com',
                'password': 'testpassword',
                'name': 'Test User',
                'role': 'user'
            },
            follow_redirects=True
        )
        assert b'Registration successful' in response.data or b'You have registered successfully' in response.data
        
        # Verify user was added to the database
        with app.app_context():
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE email = 'testuser@example.com'"
            ).fetchone()
            assert user is not None
            assert user['name'] == 'Test User'
            assert user['role'] == 'user'

    def test_register_validate_input(self, client):
        """Test registration with invalid input."""
        # Test empty username
        response = client.post(
            '/auth/register',
            data={
                'username': '',
                'password': 'testpassword',
                'name': 'Test User',
                'role': 'user'
            }
        )
        assert b'Username is required' in response.data or b'Email is required' in response.data
        
        # Test empty password
        response = client.post(
            '/auth/register',
            data={
                'username': 'testuser@example.com',
                'password': '',
                'name': 'Test User',
                'role': 'user'
            }
        )
        assert b'Password is required' in response.data
        
        # Test username already exists
        response = client.post(
            '/auth/register',
            data={
                'username': 'admin@example.com',  # Existing username
                'password': 'testpassword',
                'name': 'Test User',
                'role': 'user'
            }
        )
        assert b'User admin@example.com is already registered' in response.data or b'Email already registered' in response.data 