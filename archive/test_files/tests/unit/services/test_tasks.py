"""Unit tests for the tasks service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.tasks import (
    standardize_task_status,
    standardize_task_priority,
    get_all_tasks,
    get_task,
    get_project_tasks,
    get_user_tasks,
    create_task,
    update_task,
    delete_task,
    get_task_stats,
    get_priority_display,
    get_status_display,
    is_valid_status_transition,
    get_task_dependencies,
    get_task_timeline
)

@pytest.fixture
def mock_task():
    return {
        'id': 'test_task_id',
        'title': 'Test Task',
        'description': 'Test Description',
        'project_id': '1',
        'assigned_to': 'test_user_id',
        'status': 'PENDING',
        'priority': 'MEDIUM',
        'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'estimated_hours': 4,
        'actual_hours': 0,
        'created_by': 'test_user_id',
        'created_at': datetime.now().isoformat(),
        'completed_at': None,
        'updated_at': datetime.now().isoformat()
    }

@pytest.fixture
def mock_tasks():
    return [
        {
            'id': '1',
            'title': 'Task 1',
            'description': 'Description 1',
            'project_id': '1',
            'assigned_to': 'test_user_id',
            'status': 'COMPLETED',
            'priority': 'HIGH',
            'due_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 4,
            'actual_hours': 5,
            'created_by': 'test_user_id',
            'created_at': (datetime.now() - timedelta(days=15)).isoformat(),
            'completed_at': (datetime.now() - timedelta(days=5)).isoformat(),
            'updated_at': (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            'id': '2',
            'title': 'Task 2',
            'description': 'Description 2',
            'project_id': '1',
            'assigned_to': 'test_user_id',
            'status': 'IN_PROGRESS',
            'priority': 'MEDIUM',
            'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'estimated_hours': 6,
            'actual_hours': 2,
            'created_by': 'test_user_id',
            'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
            'completed_at': None,
            'updated_at': (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]

def test_standardize_task_status():
    """Test standardizing task status"""
    task = {'status': 'todo'}
    standardized = standardize_task_status(task)
    assert standardized['status'] == 'PENDING'
    
    task = {'status': 'in_progress'}
    standardized = standardize_task_status(task)
    assert standardized['status'] == 'IN_PROGRESS'

def test_standardize_task_priority():
    """Test standardizing task priority"""
    task = {'priority': 'high'}
    standardized = standardize_task_priority(task)
    assert standardized['priority'] == 'HIGH'
    
    task = {'priority': 'medium'}
    standardized = standardize_task_priority(task)
    assert standardized['priority'] == 'MEDIUM'

def test_get_all_tasks(mock_tasks):
    """Test getting all tasks"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = mock_tasks
        
        tasks = get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0]['id'] == '1'
        assert tasks[1]['id'] == '2'

def test_get_task(mock_task):
    """Test getting a single task"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_task]
        
        task = get_task('test_task_id')
        assert task is not None
        assert task['id'] == 'test_task_id'
        assert task['title'] == 'Test Task'

def test_get_project_tasks(mock_tasks):
    """Test getting tasks for a project"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_tasks
        
        tasks = get_project_tasks('1')
        assert len(tasks) == 2
        assert all(task['project_id'] == '1' for task in tasks)

def test_get_user_tasks(mock_tasks):
    """Test getting tasks for a user"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_tasks
        
        tasks = get_user_tasks('test_user_id')
        assert len(tasks) == 2
        assert all(task['assigned_to'] == 'test_user_id' for task in tasks)

def test_create_task(mock_task):
    """Test creating a new task"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_task]
        
        task = create_task(mock_task)
        assert task is not None
        assert task['id'] == 'test_task_id'
        assert task['title'] == 'Test Task'

def test_update_task(mock_task):
    """Test updating a task"""
    updated_data = {'title': 'Updated Task', 'status': 'IN_PROGRESS'}
    expected_task = {**mock_task, **updated_data}
    
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [expected_task]
        
        task = update_task('test_task_id', updated_data)
        assert task is not None
        assert task['title'] == 'Updated Task'
        assert task['status'] == 'IN_PROGRESS'

def test_delete_task():
    """Test deleting a task"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_task('test_task_id')
        assert result is True

def test_get_task_stats(mock_tasks):
    """Test getting task statistics"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = mock_tasks
        
        stats = get_task_stats('1')
        assert stats is not None
        assert 'total_tasks' in stats
        assert 'completed_tasks' in stats
        assert 'in_progress_tasks' in stats
        assert 'pending_tasks' in stats
        assert 'overdue_tasks' in stats

def test_get_priority_display():
    """Test getting priority display value"""
    assert get_priority_display('HIGH') == 'High'
    assert get_priority_display('MEDIUM') == 'Medium'
    assert get_priority_display('LOW') == 'Low'

def test_get_status_display():
    """Test getting status display value"""
    assert get_status_display('PENDING') == 'Pending'
    assert get_status_display('IN_PROGRESS') == 'In Progress'
    assert get_status_display('COMPLETED') == 'Completed'

def test_is_valid_status_transition():
    """Test status transition validation"""
    assert is_valid_status_transition('PENDING', 'IN_PROGRESS') is True
    assert is_valid_status_transition('IN_PROGRESS', 'COMPLETED') is True
    assert is_valid_status_transition('COMPLETED', 'IN_PROGRESS') is False

def test_get_task_dependencies():
    """Test getting task dependencies"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        dependencies = get_task_dependencies('test_task_id')
        assert dependencies is not None
        assert isinstance(dependencies, list)

def test_get_task_timeline(mock_tasks):
    """Test getting task timeline"""
    with patch('app.services.tasks.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = mock_tasks
        
        timeline = get_task_timeline('1')
        assert timeline is not None
        assert isinstance(timeline, list)
        assert len(timeline) > 0 