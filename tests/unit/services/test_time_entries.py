"""
Unit tests for time entries service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.services.time_entries import (
    get_all_time_entries,
    get_time_entry_by_id,
    get_time_entries_by_project,
    get_time_entries_by_employee,
    add_time_entry,
    edit_time_entry,
    delete_time_entry,
    get_project_time_summary
)

@pytest.fixture
def mock_time_entry():
    return {
        'id': 'time_001',
        'project_id': 'proj_001',
        'employee_id': 'emp_001',
        'date': '2023-05-15',
        'hours': 4.5,
        'billable': True,
        'description': 'Project planning and client consultation',
        'task_id': None,
        'created_at': '2023-05-15T14:30:00'
    }

def test_get_all_time_entries():
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = [{'id': 'time_001'}]
        
        time_entries = get_all_time_entries()
        assert len(time_entries) == 1
        assert time_entries[0]['id'] == 'time_001'
        mock_supabase.from_.assert_called_once()

def test_get_time_entry_by_id():
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'time_001'}]
        
        time_entry = get_time_entry_by_id('time_001')
        assert time_entry is not None
        assert time_entry['id'] == 'time_001'
        mock_supabase.from_.assert_called_once()

def test_get_time_entries_by_project():
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'time_001'}]
        
        time_entries = get_time_entries_by_project('proj_001')
        assert len(time_entries) == 1
        assert time_entries[0]['id'] == 'time_001'
        mock_supabase.from_.assert_called_once()

def test_get_time_entries_by_employee():
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': 'time_001'}]
        
        time_entries = get_time_entries_by_employee('emp_001')
        assert len(time_entries) == 1
        assert time_entries[0]['id'] == 'time_001'
        mock_supabase.from_.assert_called_once()

def test_add_time_entry(mock_time_entry):
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_time_entry]
        
        time_entry = add_time_entry(mock_time_entry)
        assert time_entry is not None
        assert time_entry['id'] == mock_time_entry['id']
        mock_supabase.from_.assert_called_once()

def test_edit_time_entry(mock_time_entry):
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_time_entry]
        
        time_entry = edit_time_entry('time_001', mock_time_entry)
        assert time_entry is not None
        assert time_entry['id'] == mock_time_entry['id']
        mock_supabase.from_.assert_called_once()

def test_delete_time_entry():
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_time_entry('time_001')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_get_project_time_summary():
    with patch('app.services.time_entries.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            'total_hours': 10.5,
            'billable_hours': 8.0,
            'total_cost': 1050.00
        }]
        
        summary = get_project_time_summary('proj_001')
        assert summary is not None
        assert summary['total_hours'] == 10.5
        assert summary['billable_hours'] == 8.0
        assert summary['total_cost'] == 1050.00
        mock_supabase.from_.assert_called_once() 