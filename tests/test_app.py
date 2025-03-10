import pytest

@pytest.mark.functional
def test_app_exists(app):
    """Test that app exists."""
    assert app is not None

@pytest.mark.functional
def test_app_config(app):
    """Test app configuration."""
    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] == 'test'

@pytest.mark.functional
def test_index_page(client):
    """Test index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

@pytest.mark.functional
def test_login_page(client):
    """Test login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Log In' in response.data

@pytest.mark.functional
def test_registration_page(client):
    """Test registration page loads."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data

@pytest.mark.functional
def test_login_required(client):
    """Test login required middleware."""
    # Try accessing a protected page
    response = client.get('/projects', follow_redirects=True)
    # Should redirect to login page
    assert response.status_code == 200
    assert b'Log In' in response.data

@pytest.mark.functional
def test_login_logout(client, auth):
    """Test login and logout functionality."""
    # Test login
    response = auth.login()
    assert response.status_code == 302  # Redirect after login
    
    # Test accessing protected page after login
    response = client.get('/projects')
    assert response.status_code == 200
    assert b'Projects' in response.data
    
    # Test logout
    response = auth.logout()
    assert response.status_code == 302  # Redirect after logout
    
    # Test accessing protected page after logout
    response = client.get('/projects', follow_redirects=True)
    assert response.status_code == 200
    assert b'Log In' in response.data 