import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Import the functions to test
from app.services.invoices import (
    get_monthly_revenue,
    get_invoices_by_status,
    get_overdue_invoices,
    get_upcoming_invoices
)


class TestReportingService:
    def test_get_monthly_revenue_with_month(self, app, monkeypatch):
        """Test getting revenue data for a specific month"""
        # Mock data
        mock_revenue_data = [
            {'total': 1000.00, 'payment_method': 'credit_card'},
            {'total': 500.00, 'payment_method': 'bank_transfer'}
        ]
        
        # Create mock row objects that can be converted to dicts
        class MockRow:
            def __init__(self, total, payment_method):
                self.total = total
                self.payment_method = payment_method
                
            def keys(self):
                return ['total', 'payment_method']
                
            def __getitem__(self, key):
                if key == 'total':
                    return self.total
                elif key == 'payment_method':
                    return self.payment_method
        
        # Mock execute and fetchall
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = [
            MockRow(1000.00, 'credit_card'),
            MockRow(500.00, 'bank_transfer')
        ]
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_execute
        
        # Patch the database connection
        monkeypatch.setattr('app.services.invoices.get_db_connection', lambda: mock_conn)
        
        with app.app_context():
            # Test with specific month
            result = get_monthly_revenue(2023, 5)
            
            # Check the SQL query parameters
            mock_conn.execute.assert_called_once()
            args, kwargs = mock_conn.execute.call_args
            query, params = args
            
            # Verify correct date range
            assert '2023-05-01' in params
            assert '2023-06-01' in params
            
            # Verify the return value structure
            assert len(result) == 2
            assert all(isinstance(item, dict) for item in result)
            assert all('total' in item and 'payment_method' in item for item in result)
    
    def test_get_monthly_revenue_december(self, app, monkeypatch):
        """Test getting revenue data for December (edge case for year transition)"""
        # Create mock row objects that can be converted to dicts
        class MockRow:
            def __init__(self, total, payment_method):
                self.total = total
                self.payment_method = payment_method
                
            def keys(self):
                return ['total', 'payment_method']
                
            def __getitem__(self, key):
                if key == 'total':
                    return self.total
                elif key == 'payment_method':
                    return self.payment_method
        
        # Mock execute and fetchall
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = [MockRow(2000.00, 'credit_card')]
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_execute
        
        # Patch the database connection
        monkeypatch.setattr('app.services.invoices.get_db_connection', lambda: mock_conn)
        
        with app.app_context():
            # Test with December
            result = get_monthly_revenue(2023, 12)
            
            # Check the SQL query parameters
            mock_conn.execute.assert_called_once()
            args, kwargs = mock_conn.execute.call_args
            query, params = args
            
            # Verify correct date range (should be 2023-12-01 to 2024-01-01)
            assert '2023-12-01' in params
            assert '2024-01-01' in params
            
            # Verify the return value structure
            assert len(result) == 1
            assert isinstance(result[0], dict)
            assert 'total' in result[0]
            assert 'payment_method' in result[0]
    
    def test_get_monthly_revenue_full_year(self, app, monkeypatch):
        """Test getting revenue data for a full year"""
        # Create mock row objects that can be converted to dicts
        class MockRow:
            def __init__(self, month, total):
                self.month = month
                self.total = total
                
            def keys(self):
                return ['month', 'total']
                
            def __getitem__(self, key):
                if key == 'month':
                    return str(self.month).zfill(2)
                elif key == 'total':
                    return self.total
        
        # Mock data for each month
        mock_rows = [
            MockRow(1, 1000.00),
            MockRow(2, 1200.00),
            MockRow(3, 1500.00),
            MockRow(4, 1800.00)
        ]
        
        # Mock execute and fetchall
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = mock_rows
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_execute
        
        # Patch the database connection
        monkeypatch.setattr('app.services.invoices.get_db_connection', lambda: mock_conn)
        
        with app.app_context():
            # Test for full year
            result = get_monthly_revenue(2023)
            
            # Check the SQL query parameters
            mock_conn.execute.assert_called_once()
            args, kwargs = mock_conn.execute.call_args
            query, params = args
            
            # Verify correct year parameter
            assert '2023' in params
            
            # Verify the return value structure
            assert len(result) == 4
            assert all(isinstance(item, dict) for item in result)
            assert all('month' in item and 'total' in item for item in result)
    
    def test_get_monthly_revenue_default_year(self, app, monkeypatch):
        """Test getting revenue data with default year (current year)"""
        # Mock execute and fetchall
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = []
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_execute
        
        # Create a real datetime object for mocking
        fixed_date = datetime(2023, 6, 15)
        
        # Patch the database connection and datetime
        monkeypatch.setattr('app.services.invoices.get_db_connection', lambda: mock_conn)
        monkeypatch.setattr('app.services.invoices.datetime', MagicMock(now=lambda: fixed_date))
        
        with app.app_context():
            # Test with default year
            result = get_monthly_revenue()
            
            # Check the SQL query parameters
            mock_conn.execute.assert_called_once()
            args, kwargs = mock_conn.execute.call_args
            query, params = args
            
            # Verify current year is used as default
            assert params[0] == '2023'
            
            # Result should be a list (empty in this case)
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_get_invoices_by_status(self, app, monkeypatch):
        """Test getting counts of invoices by status"""
        # Mock data using named tuples or objects with proper attributes
        class StatusRow:
            def __init__(self, status, count, total=0):
                self.status = status
                self.count = count
                self.total = total
                
            def keys(self):
                return ['status', 'count', 'total']
                
            def __getitem__(self, key):
                return getattr(self, key)
                
            def __iter__(self):
                yield 'status', self.status
                yield 'count', self.count
                yield 'total', self.total
        
        mock_status_data = [
            StatusRow('draft', 5, 5000.00),
            StatusRow('sent', 10, 12000.00),
            StatusRow('paid', 20, 25000.00),
            StatusRow('overdue', 3, 4000.00),
            StatusRow('cancelled', 2, 2000.00)
        ]
        
        # Mock execute and fetchall
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = mock_status_data
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_execute
        
        # Patch the database connection
        monkeypatch.setattr('app.services.invoices.get_db_connection', lambda: mock_conn)
        
        with app.app_context():
            result = get_invoices_by_status()
            
            # Check that the correct SQL query is executed
            mock_conn.execute.assert_called_once()
            
            # Verify the result structure
            assert isinstance(result, list)
            assert len(result) == 5  # One entry for each status
            
            # Convert to a more easily searchable format
            result_dict = {item['status']: item for item in result}
            
            # Verify each status is returned with correct count and total
            assert result_dict['draft']['count'] == 5
            assert result_dict['sent']['count'] == 10
            assert result_dict['paid']['count'] == 20
            assert result_dict['overdue']['count'] == 3
            assert result_dict['cancelled']['count'] == 2
            
            # Also verify totals
            assert result_dict['draft']['total'] == 5000.00
            assert result_dict['sent']['total'] == 12000.00
    
    def test_get_overdue_invoices(self, app, monkeypatch):
        """Test getting overdue invoices"""
        # Create a fixed date for testing
        fixed_date = datetime(2023, 6, 15)
        yesterday = (fixed_date - timedelta(days=1)).strftime('%Y-%m-%d')
        month_ago = (fixed_date - timedelta(days=30)).strftime('%Y-%m-%d')
        today_str = fixed_date.strftime('%Y-%m-%d')
        
        # Mock data for overdue invoices with proper row-like objects
        class InvoiceRow:
            def __init__(self, id, invoice_number, client_name, due_date, total_amount, balance_due):
                self.id = id
                self.invoice_number = invoice_number
                self.client_name = client_name
                self.due_date = due_date
                self.total_amount = total_amount
                self.balance_due = balance_due
                # Calculate days overdue based on the fixed date
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                self.days_overdue = (fixed_date.date() - due_date_obj).days
                
            def keys(self):
                return ['id', 'invoice_number', 'client_name', 'due_date', 'total_amount', 
                        'balance_due', 'days_overdue']
                
            def __getitem__(self, key):
                return getattr(self, key)
        
        mock_rows = [
            InvoiceRow(1, 'INV-001', 'Client 1', yesterday, 1000.00, 1000.00),
            InvoiceRow(2, 'INV-002', 'Client 2', month_ago, 2000.00, 1500.00)
        ]
        
        # Mock execute and fetchall
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = mock_rows
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_execute
        
        # Patch the database connection and datetime
        monkeypatch.setattr('app.services.invoices.get_db_connection', lambda: mock_conn)
        monkeypatch.setattr('app.services.invoices.datetime', MagicMock(now=lambda: fixed_date))
        
        with app.app_context():
            result = get_overdue_invoices()
            
            # Check that the correct SQL query is executed
            mock_conn.execute.assert_called_once()
            args, kwargs = mock_conn.execute.call_args
            query, params = args
            
            # Verify today's date is used in the query
            assert today_str in params[0]
            
            # Verify the result
            assert len(result) == 2
            assert result[0]['invoice_number'] == 'INV-001'
            assert result[0]['days_overdue'] == 1
            assert result[1]['invoice_number'] == 'INV-002'
            assert result[1]['days_overdue'] == 30
    
    def test_get_upcoming_invoices(self, app, monkeypatch):
        """Test getting upcoming invoices due in the next few days"""
        # Create a fixed date for testing
        fixed_date = datetime(2023, 6, 15)
        tomorrow = (fixed_date + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (fixed_date + timedelta(days=7)).strftime('%Y-%m-%d')
        today_str = fixed_date.strftime('%Y-%m-%d')
        
        # Mock data for upcoming invoices with proper row-like objects
        class InvoiceRow:
            def __init__(self, id, invoice_number, client_name, due_date, total_amount, balance_due):
                self.id = id
                self.invoice_number = invoice_number
                self.client_name = client_name
                self.due_date = due_date
                self.total_amount = total_amount
                self.balance_due = balance_due
                # Calculate days until due based on the fixed date
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                self.days_until_due = (due_date_obj - fixed_date.date()).days
                
            def keys(self):
                return ['id', 'invoice_number', 'client_name', 'due_date', 'total_amount', 
                        'balance_due', 'days_until_due']
                
            def __getitem__(self, key):
                return getattr(self, key)
        
        mock_rows = [
            InvoiceRow(1, 'INV-003', 'Client 3', tomorrow, 1000.00, 1000.00),
            InvoiceRow(2, 'INV-004', 'Client 4', next_week, 2000.00, 2000.00)
        ]
        
        # Mock execute and fetchall
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = mock_rows
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.execute.return_value = mock_execute
        
        # Patch the database connection and datetime
        monkeypatch.setattr('app.services.invoices.get_db_connection', lambda: mock_conn)
        monkeypatch.setattr('app.services.invoices.datetime', MagicMock(now=lambda: fixed_date))
        
        with app.app_context():
            # Test with default 7 days
            result = get_upcoming_invoices()
            
            # Check that the correct SQL query is executed
            mock_conn.execute.assert_called_once()
            args, kwargs = mock_conn.execute.call_args
            query, params = args
            
            # Verify date range in the query
            assert today_str in params[0]
            # The end date should be 7 days from today
            assert (fixed_date + timedelta(days=7)).strftime('%Y-%m-%d') in params[1]
            
            # Verify the result
            assert len(result) == 2
            assert result[0]['invoice_number'] == 'INV-003'
            assert result[0]['days_until_due'] == 1
            assert result[1]['invoice_number'] == 'INV-004'
            assert result[1]['days_until_due'] == 7
            
            # Test with custom days parameter
            mock_conn.reset_mock()
            mock_conn.execute.return_value = mock_execute
            
            result = get_upcoming_invoices(days=3)
            
            # Check updated parameters
            mock_conn.execute.assert_called_once()
            args, kwargs = mock_conn.execute.call_args
            query, params = args
            
            # Verify the end date is now 3 days from today
            assert (fixed_date + timedelta(days=3)).strftime('%Y-%m-%d') in params[1] 