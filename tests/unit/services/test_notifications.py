"""
Unit tests for notifications service
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from app.services.notifications import (
    get_user_notifications,
    get_notification_by_id,
    create_notification,
    update_notification,
    delete_notification,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_unread_notification_count,
    notify_task_assignment,
    notify_task_due_soon,
    notify_task_overdue,
    notify_project_status_change,
    notify_document_upload,
    notify_budget_warning
)

@pytest.fixture
def mock_notification():
    return {
        'id': 'test_id',
        'user_id': 'test_user_id',
        'title': 'Test Notification',
        'message': 'Test Message',
        'notification_type': 'info',
        'category': 'test',
        'entity_id': 'test_entity_id',
        'entity_type': 'test_entity',
        'action_url': '/test/url',
        'is_read': False,
        'created_at': datetime.now().isoformat()
    }

@pytest.fixture
def mock_task():
    task = MagicMock()
    task.id = 'test_task_id'
    task.title = 'Test Task'
    task.days_remaining = 3
    return task

@pytest.fixture
def mock_project():
    project = MagicMock()
    project.id = 'test_project_id'
    project.name = 'Test Project'
    project.status = 'In Progress'
    project.budget_percentage = 85
    return project

@pytest.fixture
def mock_document():
    document = MagicMock()
    document.id = 'test_document_id'
    document.title = 'Test Document'
    return document

def test_get_user_notifications():
    with patch('app.services.notifications.get_table_data') as mock_get_data:
        mock_get_data.return_value = [{'id': 'test_id'}]
        
        notifications = get_user_notifications('test_user_id')
        assert len(notifications) == 1
        assert notifications[0].id == 'test_id'
        mock_get_data.assert_called_once()

def test_get_notification_by_id():
    with patch('app.services.notifications.get_table_data') as mock_get_data:
        mock_get_data.return_value = [{'id': 'test_id'}]
        
        notification = get_notification_by_id('test_id')
        assert notification is not None
        assert notification.id == 'test_id'
        mock_get_data.assert_called_once()

def test_create_notification(mock_notification):
    with patch('app.services.notifications.insert_record') as mock_insert:
        mock_insert.return_value = mock_notification
        
        notification = create_notification(mock_notification)
        assert notification is not None
        assert notification.id == mock_notification['id']
        mock_insert.assert_called_once()

def test_update_notification(mock_notification):
    with patch('app.services.notifications.update_record') as mock_update:
        mock_update.return_value = mock_notification
        
        notification = update_notification('test_id', mock_notification)
        assert notification is not None
        assert notification.id == mock_notification['id']
        mock_update.assert_called_once()

def test_delete_notification():
    with patch('app.services.notifications.delete_record') as mock_delete:
        mock_delete.return_value = True
        
        result = delete_notification('test_id')
        assert result is True
        mock_delete.assert_called_once()

def test_mark_notification_as_read():
    with patch('app.services.notifications.update_notification') as mock_update:
        mock_update.return_value = {'id': 'test_id', 'is_read': True}
        
        result = mark_notification_as_read('test_id')
        assert result is not None
        assert result.is_read is True
        mock_update.assert_called_once_with('test_id', {'is_read': True})

def test_mark_all_notifications_as_read():
    with patch('app.services.notifications.get_user_notifications') as mock_get_notifications:
        mock_notifications = [
            MagicMock(id='test_id1'),
            MagicMock(id='test_id2')
        ]
        mock_get_notifications.return_value = mock_notifications
        
        with patch('app.services.notifications.mark_notification_as_read') as mock_mark_read:
            result = mark_all_notifications_as_read('test_user_id')
            assert result is True
            assert mock_mark_read.call_count == 2

def test_get_unread_notification_count():
    with patch('app.services.notifications.get_user_notifications') as mock_get_notifications:
        mock_get_notifications.return_value = [
            MagicMock(),
            MagicMock(),
            MagicMock()
        ]
        
        count = get_unread_notification_count('test_user_id')
        assert count == 3
        mock_get_notifications.assert_called_once()

def test_notify_task_assignment(mock_task):
    with patch('app.services.notifications.create_notification') as mock_create:
        mock_create.return_value = MagicMock()
        
        notification = notify_task_assignment(mock_task, 'test_user_id')
        assert notification is not None
        mock_create.assert_called_once()

def test_notify_task_due_soon(mock_task):
    with patch('app.services.notifications.create_notification') as mock_create:
        mock_create.return_value = MagicMock()
        
        notification = notify_task_due_soon(mock_task, 'test_user_id')
        assert notification is not None
        mock_create.assert_called_once()

def test_notify_task_overdue(mock_task):
    with patch('app.services.notifications.create_notification') as mock_create:
        mock_create.return_value = MagicMock()
        
        notification = notify_task_overdue(mock_task, 'test_user_id')
        assert notification is not None
        mock_create.assert_called_once()

def test_notify_project_status_change(mock_project):
    with patch('app.services.notifications.create_notification') as mock_create:
        mock_create.return_value = MagicMock()
        
        notification = notify_project_status_change(mock_project, 'test_user_id', 'Planning')
        assert notification is not None
        mock_create.assert_called_once()

def test_notify_document_upload(mock_document):
    with patch('app.services.notifications.create_notification') as mock_create:
        mock_create.return_value = MagicMock()
        
        notification = notify_document_upload(mock_document, 'test_user_id')
        assert notification is not None
        mock_create.assert_called_once()

def test_notify_budget_warning(mock_project):
    with patch('app.services.notifications.create_notification') as mock_create:
        mock_create.return_value = MagicMock()
        
        notification = notify_budget_warning(mock_project, 'test_user_id')
        assert notification is not None
        mock_create.assert_called_once() 