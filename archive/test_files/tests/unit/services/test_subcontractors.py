"""
Unit tests for subcontractors service
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.subcontractors import (
    get_all_subcontractors,
    get_subcontractor_by_id,
    create_subcontractor,
    update_subcontractor,
    delete_subcontractor,
    get_subcontractor_invoices,
    create_invoice,
    update_invoice,
    delete_invoice,
    get_subcontractor_assignments,
    assign_subcontractor_to_project,
    update_assignment_status,
    remove_subcontractor_from_project,
    get_subcontractors_by_trade,
    get_subcontractors_by_project,
    get_subcontractor_summary
)

@pytest.fixture
def mock_subcontractor():
    return {
        'id': '1',
        'name': 'Elite Electrical',
        'contact_name': 'Mike Johnson',
        'email': 'mike@eliteelectrical.com',
        'phone': '555-123-4567',
        'trade': 'Electrical',
        'rate': 75.00,
        'address': '123 Main St, Anytown, USA',
        'insurance_expiry': '2023-12-31',
        'license': 'EL-12345',
        'notes': 'Reliable electrical contractor'
    }

@pytest.fixture
def mock_invoice():
    return {
        'id': '1',
        'subcontractor_id': '1',
        'project_id': 1,
        'invoice_number': 'INV-001',
        'amount': 2500.00,
        'date': '2023-03-01',
        'due_date': '2023-03-31',
        'status': 'Paid',
        'description': 'Electrical work for Phase 1'
    }

@pytest.fixture
def mock_assignment():
    return {
        'id': '1',
        'subcontractor_id': '1',
        'project_id': 1,
        'project_name': 'Sample Project 1',
        'status': 'In Progress',
        'created_at': '2023-01-15T08:00:00'
    }

def test_get_all_subcontractors():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = [{'id': '1'}]
        
        subcontractors = get_all_subcontractors()
        assert len(subcontractors) == 1
        assert subcontractors[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_get_subcontractor_by_id():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        subcontractor = get_subcontractor_by_id('1')
        assert subcontractor is not None
        assert subcontractor['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_create_subcontractor(mock_subcontractor):
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_subcontractor]
        
        subcontractor = create_subcontractor(mock_subcontractor)
        assert subcontractor is not None
        assert subcontractor['id'] == mock_subcontractor['id']
        mock_supabase.from_.assert_called_once()

def test_update_subcontractor(mock_subcontractor):
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_subcontractor]
        
        subcontractor = update_subcontractor('1', mock_subcontractor)
        assert subcontractor is not None
        assert subcontractor['id'] == mock_subcontractor['id']
        mock_supabase.from_.assert_called_once()

def test_delete_subcontractor():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_subcontractor('1')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_get_subcontractor_invoices():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        invoices = get_subcontractor_invoices('1')
        assert len(invoices) == 1
        assert invoices[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_create_invoice(mock_invoice):
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_invoice]
        
        invoice = create_invoice(mock_invoice)
        assert invoice is not None
        assert invoice['id'] == mock_invoice['id']
        mock_supabase.from_.assert_called_once()

def test_update_invoice(mock_invoice):
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_invoice]
        
        invoice = update_invoice('1', mock_invoice)
        assert invoice is not None
        assert invoice['id'] == mock_invoice['id']
        mock_supabase.from_.assert_called_once()

def test_delete_invoice():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_invoice('1')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_get_subcontractor_assignments():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        assignments = get_subcontractor_assignments('1')
        assert len(assignments) == 1
        assert assignments[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_assign_subcontractor_to_project(mock_assignment):
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_assignment]
        
        assignment = assign_subcontractor_to_project(mock_assignment)
        assert assignment is not None
        assert assignment['id'] == mock_assignment['id']
        mock_supabase.from_.assert_called_once()

def test_update_assignment_status():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [{'id': '1', 'status': 'Completed'}]
        
        assignment = update_assignment_status('1', 'Completed')
        assert assignment is not None
        assert assignment['status'] == 'Completed'
        mock_supabase.from_.assert_called_once()

def test_remove_subcontractor_from_project():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = True
        
        result = remove_subcontractor_from_project('1', 1)
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_get_subcontractors_by_trade():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        subcontractors = get_subcontractors_by_trade('Electrical')
        assert len(subcontractors) == 1
        assert subcontractors[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_get_subcontractors_by_project():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        subcontractors = get_subcontractors_by_project(1)
        assert len(subcontractors) == 1
        assert subcontractors[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_get_subcontractor_summary():
    with patch('app.services.subcontractors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            'total_invoices': 5,
            'total_amount': 15000.00,
            'active_projects': 2,
            'completed_projects': 3
        }]
        
        summary = get_subcontractor_summary('1')
        assert summary is not None
        assert summary['total_invoices'] == 5
        assert summary['total_amount'] == 15000.00
        assert summary['active_projects'] == 2
        assert summary['completed_projects'] == 3
        mock_supabase.from_.assert_called_once() 