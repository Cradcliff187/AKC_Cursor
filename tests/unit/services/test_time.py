"""
Unit tests for time service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.time import (
    get_all_time_entries,
    get_user_time_entries,
    get_project_time_entries,
    get_time_entry,
    create_time_entry,
    update_time_entry,
    delete_time_entry,
    update_time_entry_status,
    get_time_summary
)

@pytest.fixture
def mock_time_entry():
    return {
        'id': 'test_id',
        'user_id': 'test_user_id',
        'project_id': 'test_project_id',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'hours': 8.0,
        'description': 'Test Description',
        'status': 'pending',
        'billable': True,
        'created_at': datetime.now().isoformat(),
        'project_name': 'Test Project'
    }

@pytest.fixture
def mock_time_entries():
    return [
        {
            'id': '1',
            'user_id': 'test_user_id',
            'project_id': 1,
            'date': '2023-03-01',
            'hours': 8.0,
            'description': 'Test Entry 1',
            'status': 'approved',
            'billable': True,
            'created_at': '2023-03-01T08:00:00',
            'project_name': 'Test Project 1'
        },
        {
            'id': '2',
            'user_id': 'test_user_id',
            'project_id': 2,
            'date': '2023-03-02',
            'hours': 6.0,
            'description': 'Test Entry 2',
            'status': 'pending',
            'billable': False,
            'created_at': '2023-03-02T09:00:00',
            'project_name': 'Test Project 2'
        }
    ]

def test_get_all_time_entries():
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = [{'id': 'test_id', 'projects': {'name': 'Test Project'}}]
        
        entries = get_all_time_entries()
        assert len(entries) == 1
        assert entries[0]['id'] == 'test_id'
        assert entries[0]['project_name'] == 'Test Project'
        mock_supabase.from_.assert_called_once()

def test_get_user_time_entries():
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'test_id', 'projects': {'name': 'Test Project'}}]
        
        entries = get_user_time_entries('test_user_id')
        assert len(entries) == 1
        assert entries[0]['id'] == 'test_id'
        assert entries[0]['project_name'] == 'Test Project'
        mock_supabase.from_.assert_called_once()

def test_get_project_time_entries():
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'test_id', 'projects': {'name': 'Test Project'}}]
        
        entries = get_project_time_entries('test_project_id')
        assert len(entries) == 1
        assert entries[0]['id'] == 'test_id'
        assert entries[0]['project_name'] == 'Test Project'
        mock_supabase.from_.assert_called_once()

def test_get_time_entry():
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'test_id', 'projects': {'name': 'Test Project'}}]
        
        entry = get_time_entry('test_id')
        assert entry is not None
        assert entry['id'] == 'test_id'
        assert entry['project_name'] == 'Test Project'
        mock_supabase.from_.assert_called_once()

def test_create_time_entry(mock_time_entry):
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_time_entry]
        
        entry = create_time_entry(mock_time_entry)
        assert entry is not None
        assert entry['id'] == mock_time_entry['id']
        mock_supabase.from_.assert_called_once()

def test_update_time_entry(mock_time_entry):
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_time_entry]
        
        entry = update_time_entry('test_id', mock_time_entry)
        assert entry is not None
        assert entry['id'] == mock_time_entry['id']
        mock_supabase.from_.assert_called_once()

def test_delete_time_entry():
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_time_entry('test_id')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_update_time_entry_status():
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [{'id': 'test_id', 'status': 'approved', 'projects': {'name': 'Test Project'}}]
        
        entry = update_time_entry_status('test_id', 'approved')
        assert entry is not None
        assert entry['status'] == 'approved'
        assert entry['project_name'] == 'Test Project'
        mock_supabase.from_.assert_called_once()

def test_get_time_summary():
    with patch('app.services.time.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = [
            {'hours': 8.0, 'billable': True},
            {'hours': 4.0, 'billable': False}
        ]
        
        summary = get_time_summary()
        assert summary is not None
        assert summary['total_hours'] == 12.0
        assert summary['billable_hours'] == 8.0
        assert summary['non_billable_hours'] == 4.0
        mock_supabase.from_.assert_called_once() 