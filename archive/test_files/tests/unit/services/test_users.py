"""
Unit tests for users service
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.users import (
    get_all_users,
    get_user_by_id,
    get_users_by_role,
    get_user_by_email,
    get_user_by_username,
    create_user,
    update_user,
    deactivate_user,
    can_access_role,
    get_role_display,
    get_active_users,
    authenticate_user,
    get_user_projects,
    has_permission,
    get_user_permissions
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

def test_get_all_users():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = [{'id': 'user_001'}]
        
        users = get_all_users()
        assert len(users) == 1
        assert users[0]['id'] == 'user_001'
        mock_supabase.from_.assert_called_once()

def test_get_user_by_id():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'user_001'}]
        
        user = get_user_by_id('user_001')
        assert user is not None
        assert user['id'] == 'user_001'
        mock_supabase.from_.assert_called_once()

def test_get_users_by_role():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'user_001'}]
        
        users = get_users_by_role('admin')
        assert len(users) == 1
        assert users[0]['id'] == 'user_001'
        mock_supabase.from_.assert_called_once()

def test_get_user_by_email():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'user_001'}]
        
        user = get_user_by_email('test@example.com')
        assert user is not None
        assert user['id'] == 'user_001'
        mock_supabase.from_.assert_called_once()

def test_get_user_by_username():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'user_001'}]
        
        user = get_user_by_username('testuser')
        assert user is not None
        assert user['id'] == 'user_001'
        mock_supabase.from_.assert_called_once()

def test_create_user(mock_user):
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_user]
        
        user = create_user(mock_user)
        assert user is not None
        assert user['id'] == mock_user['id']
        mock_supabase.from_.assert_called_once()

def test_update_user(mock_user):
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_user]
        
        user = update_user('user_001', mock_user)
        assert user is not None
        assert user['id'] == mock_user['id']
        mock_supabase.from_.assert_called_once()

def test_deactivate_user():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value = True
        
        result = deactivate_user('user_001')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_can_access_role():
    can_access = can_access_role('admin', 'project_manager')
    assert can_access is True

def test_get_role_display():
    display = get_role_display('admin')
    assert display == 'Administrator'

def test_get_active_users():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'user_001'}]
        
        users = get_active_users()
        assert len(users) == 1
        assert users[0]['id'] == 'user_001'
        mock_supabase.from_.assert_called_once()

def test_authenticate_user():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'user_001'}]
        
        user = authenticate_user('testuser', 'password123')
        assert user is not None
        assert user['id'] == 'user_001'
        mock_supabase.from_.assert_called_once()

def test_get_user_projects():
    with patch('app.services.users.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'proj_001'}]
        
        projects = get_user_projects('user_001')
        assert len(projects) == 1
        assert projects[0]['id'] == 'proj_001'
        mock_supabase.from_.assert_called_once()

def test_has_permission():
    with patch('app.services.users.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = {'role': 'admin'}
        
        has_perm = has_permission('user_001', 'manage_users')
        assert has_perm is True
        mock_get_user.assert_called_once()

def test_get_user_permissions():
    with patch('app.services.users.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = {'role': 'admin'}
        
        permissions = get_user_permissions('user_001')
        assert len(permissions) > 0
        assert 'manage_users' in permissions
        mock_get_user.assert_called_once() 