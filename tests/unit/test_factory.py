"""
Unit tests for the Flask application factory
"""
import os
from flask import session
from app import create_app, nl2br

def test_config():
    """Test that the app loads different configurations based on test_config"""
    # Test default config
    assert not create_app().testing
    
    # Test explicit config
    assert create_app({'TESTING': True}).testing

def test_instance_path(tmp_path):
    """Test that instance folders are created"""
    instance_path = tmp_path / 'instance'
    upload_path = instance_path / 'uploads'
    
    os.environ['INSTANCE_PATH'] = str(instance_path)
    app = create_app({'UPLOAD_FOLDER': str(upload_path)})
    
    assert os.path.exists(instance_path)
    assert os.path.exists(upload_path)

def test_hello_route(client):
    """Test the index route works and returns 200"""
    response = client.get('/')
    assert response.status_code == 200
    
def test_404_page(client):
    """Test the 404 error handler"""
    response = client.get('/nonexistent-route')
    assert response.status_code == 404
    assert b'Page not found' in response.data

def test_nl2br_filter():
    """Test the newline to br filter"""
    assert nl2br('Hello\nWorld') == 'Hello<br>World'
    assert nl2br('Hello\r\nWorld') == 'Hello<br>World'
    assert nl2br(None) == ''
    assert nl2br('') == '' 