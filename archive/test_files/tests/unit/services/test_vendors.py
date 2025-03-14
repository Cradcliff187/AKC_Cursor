"""
Unit tests for vendors service
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.vendors import (
    get_all_vendors,
    get_vendor_by_id,
    create_vendor,
    update_vendor,
    delete_vendor,
    get_vendor_purchases,
    add_purchase,
    update_purchase,
    delete_purchase,
    get_vendor_purchase_summary,
    get_vendor_purchase_history,
    get_vendor_purchase_by_id,
    get_vendor_purchases_by_project,
    get_vendor_purchases_by_date_range
)

@pytest.fixture
def mock_vendor():
    return {
        'id': '1',
        'name': 'ABC Lumber Supply',
        'contact_name': 'John Smith',
        'email': 'john@abclumber.com',
        'phone': '555-123-4567',
        'address': '123 Main St, Anytown, USA',
        'notes': 'Reliable supplier for lumber and building materials'
    }

@pytest.fixture
def mock_purchase():
    return {
        'id': '1',
        'vendor_id': '1',
        'project_id': 1,
        'description': 'Lumber for framing',
        'amount': 2500.00,
        'date': '2023-03-01',
        'receipt_url': None
    }

def test_get_all_vendors():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.execute.return_value.data = [{'id': '1'}]
        
        vendors = get_all_vendors()
        assert len(vendors) == 1
        assert vendors[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_get_vendor_by_id():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        vendor = get_vendor_by_id('1')
        assert vendor is not None
        assert vendor['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_create_vendor(mock_vendor):
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_vendor]
        
        vendor = create_vendor(mock_vendor)
        assert vendor is not None
        assert vendor['id'] == mock_vendor['id']
        mock_supabase.from_.assert_called_once()

def test_update_vendor(mock_vendor):
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_vendor]
        
        vendor = update_vendor('1', mock_vendor)
        assert vendor is not None
        assert vendor['id'] == mock_vendor['id']
        mock_supabase.from_.assert_called_once()

def test_delete_vendor():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_vendor('1')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_get_vendor_purchases():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        purchases = get_vendor_purchases('1')
        assert len(purchases) == 1
        assert purchases[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_add_purchase(mock_purchase):
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.insert.return_value.execute.return_value.data = [mock_purchase]
        
        purchase = add_purchase(mock_purchase)
        assert purchase is not None
        assert purchase['id'] == mock_purchase['id']
        mock_supabase.from_.assert_called_once()

def test_update_purchase(mock_purchase):
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_purchase]
        
        purchase = update_purchase('1', mock_purchase)
        assert purchase is not None
        assert purchase['id'] == mock_purchase['id']
        mock_supabase.from_.assert_called_once()

def test_delete_purchase():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.delete.return_value.eq.return_value.execute.return_value = True
        
        result = delete_purchase('1')
        assert result is True
        mock_supabase.from_.assert_called_once()

def test_get_vendor_purchase_summary():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
            'total_amount': 5000.00,
            'total_purchases': 2,
            'average_amount': 2500.00
        }]
        
        summary = get_vendor_purchase_summary('1')
        assert summary is not None
        assert summary['total_amount'] == 5000.00
        assert summary['total_purchases'] == 2
        assert summary['average_amount'] == 2500.00
        mock_supabase.from_.assert_called_once()

def test_get_vendor_purchase_history():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [{'id': '1'}]
        
        history = get_vendor_purchase_history('1')
        assert len(history) == 1
        assert history[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_get_vendor_purchase_by_id():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        purchase = get_vendor_purchase_by_id('1')
        assert purchase is not None
        assert purchase['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_get_vendor_purchases_by_project():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '1'}]
        
        purchases = get_vendor_purchases_by_project('1', 1)
        assert len(purchases) == 1
        assert purchases[0]['id'] == '1'
        mock_supabase.from_.assert_called_once()

def test_get_vendor_purchases_by_date_range():
    with patch('app.services.vendors.supabase') as mock_supabase:
        mock_supabase.from_.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value.data = [{'id': '1'}]
        
        purchases = get_vendor_purchases_by_date_range('1', '2023-01-01', '2023-12-31')
        assert len(purchases) == 1
        assert purchases[0]['id'] == '1'
        mock_supabase.from_.assert_called_once() 