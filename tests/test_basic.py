"""
Basic test to verify that our test environment is working
"""

def test_app_creates(app):
    """Test that app fixture works"""
    assert app is not None

def test_client_works(client):
    """Test that client fixture works"""
    response = client.get('/')
    assert response is not None
    
def test_auth_page_loads(client):
    """Test that login page loads"""
    response = client.get('/auth/login')
    assert response.status_code in (200, 302)  # Either OK or redirect 