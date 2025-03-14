"""
Unit tests for user context service
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.user_context import (
    get_user_role,
    get_current_user,
    has_permission,
    is_mobile_device,
    is_admin_level_user,
    is_field_level_user,
    get_appropriate_template,
    render_appropriate_template,
    get_user_dashboard_url,
    can_edit_project,
    can_access_client
)

@pytest.fixture
def mock_user():
    return {
        'id': 'user_001',
        'username': 'testuser',
        'email': 'test@example.com',
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    }

@pytest.fixture
def mock_session():
    with patch('app.services.user_context.session') as mock:
        mock.get.return_value = 'user_001'
        yield mock

def test_get_user_role(mock_session):
    with patch('app.services.user_context.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = {'role': 'admin'}
        
        role = get_user_role()
        assert role == 'admin'
        mock_get_user.assert_called_once()

def test_get_current_user(mock_session):
    with patch('app.services.user_context.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = {'id': 'user_001'}
        
        user = get_current_user()
        assert user is not None
        assert user['id'] == 'user_001'
        mock_get_user.assert_called_once()

def test_has_permission():
    with patch('app.services.user_context.get_user_role') as mock_get_role:
        mock_get_role.return_value = 'admin'
        
        has_perm = has_permission('manage_users')
        assert has_perm is True
        mock_get_role.assert_called_once()

def test_is_mobile_device():
    with patch('app.services.user_context.request') as mock_request:
        mock_request.user_agent.string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        
        is_mobile = is_mobile_device()
        assert is_mobile is True

def test_is_admin_level_user():
    with patch('app.services.user_context.get_user_role') as mock_get_role:
        mock_get_role.return_value = 'admin'
        
        is_admin = is_admin_level_user()
        assert is_admin is True
        mock_get_role.assert_called_once()

def test_is_field_level_user():
    with patch('app.services.user_context.get_user_role') as mock_get_role:
        mock_get_role.return_value = 'field_worker'
        
        is_field = is_field_level_user()
        assert is_field is True
        mock_get_role.assert_called_once()

def test_get_appropriate_template():
    with patch('app.services.user_context.is_mobile_device') as mock_is_mobile:
        mock_is_mobile.return_value = True
        
        template = get_appropriate_template('dashboard')
        assert template == 'mobile/dashboard.html'
        mock_is_mobile.assert_called_once()

def test_render_appropriate_template():
    with patch('app.services.user_context.current_app') as mock_app:
        mock_app.jinja_env.get_template.return_value.render.return_value = '<html>'
        
        result = render_appropriate_template('dashboard')
        assert result == '<html>'
        mock_app.jinja_env.get_template.assert_called_once()

def test_get_user_dashboard_url():
    with patch('app.services.user_context.get_user_role') as mock_get_role:
        mock_get_role.return_value = 'admin'
        
        url = get_user_dashboard_url()
        assert url == '/admin/dashboard'
        mock_get_role.assert_called_once()

def test_can_edit_project():
    with patch('app.services.user_context.get_current_user') as mock_get_user:
        mock_get_user.return_value = {'role': 'admin'}
        
        can_edit = can_edit_project('proj_001')
        assert can_edit is True
        mock_get_user.assert_called_once()

def test_can_access_client():
    with patch('app.services.user_context.get_current_user') as mock_get_user:
        mock_get_user.return_value = {'role': 'admin'}
        
        can_access = can_access_client('client_001')
        assert can_access is True
        mock_get_user.assert_called_once() 