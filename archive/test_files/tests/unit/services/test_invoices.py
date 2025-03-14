"""
Unit tests for invoices service
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.services import invoices
from app.models.invoice import Invoice

@pytest.mark.unit
@pytest.mark.services
class TestInvoiceService:
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection for testing."""
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_db.execute.return_value = mock_cursor
        mock_cursor.lastrowid = 3  # New invoice ID
        return mock_db
    
    @pytest.fixture
    def mock_get_db(self, mock_db):
        """Mock the get_db function to return our mock db."""
        with patch('app.services.invoices.get_db', return_value=mock_db):
            yield
    
    def test_get_all_invoices(self, app, mock_get_db):
        """Test retrieving all invoices with various filters"""
        # Mock database query result
        mock_result = [
            {'id': 1, 'invoice_number': 'INV-001', 'client_id': 1, 'status': 'draft'},
            {'id': 2, 'invoice_number': 'INV-002', 'client_id': 2, 'status': 'sent'},
        ]
        
        # Mock execute method
        mock_execute = MagicMock()
        mock_execute.fetchall.return_value = mock_result
        
        # Mock db connection and execute
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_execute
        
        # Patch get_db to return our mock
        with patch('app.services.invoices.get_db', return_value=mock_db):
            with app.app_context():
                # Test default parameters
                invoices = invoices.get_all_invoices()
                assert invoices == mock_result
                mock_db.execute.assert_called_once()
                
                # Reset mocks for next test
                mock_db.reset_mock()
                
                # Test with filters
                invoices = invoices.get_all_invoices(
                    limit=10,
                    offset=5,
                    status='draft',
                    client_id=1,
                    project_id=2,
                    date_from='2023-01-01',
                    date_to='2023-01-31'
                )
                assert invoices == mock_result
                mock_db.execute.assert_called_once()
                
                # Check that WHERE clauses include our filters
                sql = mock_db.execute.call_args[0][0]
                assert 'WHERE' in sql
                assert 'LIMIT ? OFFSET ?' in sql
                
                # Check that params include our filter values
                params = mock_db.execute.call_args[0][1]
                assert 'draft' in params  # status
                assert 1 in params  # client_id
                assert 2 in params  # project_id
                assert '2023-01-01' in params  # date_from
                assert '2023-01-31' in params  # date_to
                assert 10 in params  # limit
                assert 5 in params  # offset

    def test_get_invoice_by_id(self, app, mock_get_db):
        """Test retrieving a single invoice by ID"""
        # Mock database query result
        mock_invoice = {
            'id': 1,
            'invoice_number': 'INV-001',
            'client_id': 1,
            'status': 'draft',
            'issue_date': '2023-01-01',
            'due_date': '2023-01-31',
            'total_amount': 1000.00
        }
        
        # Mock execute method
        mock_execute = MagicMock()
        mock_execute.fetchone.return_value = mock_invoice
        
        # Mock db connection and execute
        mock_db = MagicMock()
        mock_db.execute.return_value = mock_execute
        
        # Patch get_db to return our mock
        with patch('app.services.invoices.get_db', return_value=mock_db):
            with app.app_context():
                invoice = invoices.get_invoice_by_id(1)
                assert invoice == mock_invoice
                mock_db.execute.assert_called_once()
                
                # Check that we're querying for the right invoice
                sql = mock_db.execute.call_args[0][0]
                assert 'SELECT * FROM invoices WHERE id = ?' in sql
                assert mock_db.execute.call_args[0][1] == (1,)

    def test_get_next_invoice_number(self, app, mock_get_db):
        """Test generating the next invoice number"""
        # Test when there are existing invoices
        mock_execute_with_results = MagicMock()
        mock_execute_with_results.fetchone.return_value = {'max_number': 'INV-005'}
        
        # Test when there are no existing invoices
        mock_execute_no_results = MagicMock()
        mock_execute_no_results.fetchone.return_value = {'max_number': None}
        
        # Mock db connection
        mock_db = MagicMock()
        
        # Patch get_db to return our mock
        with patch('app.services.invoices.get_db', return_value=mock_db):
            with app.app_context():
                # Case 1: Existing invoices, should increment the number
                mock_db.execute.return_value = mock_execute_with_results
                next_number = invoices.get_next_invoice_number()
                assert next_number == 'INV-006'
                mock_db.execute.assert_called_once()
                
                # Reset for next test
                mock_db.reset_mock()
                
                # Case 2: No existing invoices, should start at 001
                mock_db.execute.return_value = mock_execute_no_results
                next_number = invoices.get_next_invoice_number()
                assert next_number == 'INV-001'
                mock_db.execute.assert_called_once()

    def test_create_invoice(self, app, mock_get_db, test_invoice_data, test_invoice_item_data):
        """Test creating a new invoice"""
        # Mock functions
        with patch('app.services.invoices.get_next_invoice_number', 
                    lambda: 'INV-001'):
            with app.app_context():
                # Create invoice without items
                invoice_id = invoices.create_invoice(test_invoice_data)
                assert invoice_id == 3  # From our mock lastrowid
                
                # Verify correct SQL was executed
                invoices.get_db().execute.assert_called()
                call_args = invoices.get_db().execute.call_args[0]
                assert "INSERT INTO invoices" in call_args[0]
                
                # Reset mock for next test
                invoices.get_db().execute.reset_mock()
                
                # Create invoice with items
                invoice_id = invoices.create_invoice(test_invoice_data, test_invoice_item_data)
                assert invoice_id == 3
                
                # Should have executed multiple times for invoice and each item
                assert invoices.get_db().execute.call_count >= 1 + len(test_invoice_item_data)

    def test_update_invoice(self, app, mock_get_db, test_invoice_data, test_invoice_item_data):
        """Test updating an existing invoice"""
        with app.app_context():
            # Update invoice without items
            invoices.update_invoice(1, test_invoice_data)
            
            # Verify correct SQL was executed
            invoices.get_db().execute.assert_called()
            call_args = invoices.get_db().execute.call_args[0]
            assert "UPDATE invoices SET" in call_args[0]
            
            # Reset mock for next test
            invoices.get_db().execute.reset_mock()
            
            # Update invoice with items
            invoices.update_invoice(1, test_invoice_data, test_invoice_item_data)
            
            # Should have executed multiple times for invoice and deleting old items and adding new ones
            assert invoices.get_db().execute.call_count >= 2

    def test_delete_invoice(self, app, mock_get_db):
        """Test deleting an invoice"""
        with app.app_context():
            invoices.delete_invoice(1)
            
            # Should delete items and payments first, then invoice
            assert invoices.get_db().execute.call_count >= 3
            
            # Check last call was to delete the invoice
            call_args = invoices.get_db().execute.call_args[0]
            assert "DELETE FROM invoices WHERE id = ?" in call_args[0]

    def test_get_invoice_items(self, app, mock_get_db):
        """Test retrieving invoice items"""
        with app.app_context():
            invoices.get_invoice_items(1)
            invoices.get_db().execute.assert_called_once()
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "SELECT * FROM invoice_items WHERE invoice_id = ?" in call_args

    def test_save_invoice_item(self, app, mock_get_db):
        """Test saving an invoice item."""
        item_data = {
            'id': None,  # New item
            'invoice_id': 1,
            'description': 'Test Item',
            'quantity': 1,
            'unit_price': 100,
            'type': 'Service',
            'taxable': True
        }
        
        with app.app_context():
            # Create new item
            invoices.save_invoice_item(invoices.get_db(), item_data)
            
            # Verify insert was called
            call_args = invoices.get_db().execute.call_args[0]
            assert "INSERT INTO invoice_items" in call_args[0]
            
            # Reset mock
            invoices.get_db().execute.reset_mock()
            
            # Update existing item
            item_data['id'] = 1
            invoices.save_invoice_item(invoices.get_db(), item_data)
            
            # Verify update was called
            call_args = invoices.get_db().execute.call_args[0]
            assert "UPDATE invoice_items SET" in call_args[0]

    def test_recalculate_invoice_totals(self, app, mock_get_db):
        """Test recalculating invoice totals"""
        # Mock items query result
        mock_items = [
            {'amount': 100.00, 'taxable': True},
            {'amount': 200.00, 'taxable': True},
            {'amount': 50.00, 'taxable': False},
        ]
        
        # Mock invoice query result
        mock_invoice = {
            'id': 1,
            'tax_rate': 10.0,
            'discount_amount': 20.00,
            'amount_paid': 100.00
        }
        
        # Mock execute method for items
        mock_items_execute = MagicMock()
        mock_items_execute.fetchall.return_value = mock_items
        
        # Mock execute method for invoice
        mock_invoice_execute = MagicMock()
        mock_invoice_execute.fetchone.return_value = mock_invoice
        
        # Mock db connection
        mock_db = MagicMock()
        mock_db.execute.side_effect = [mock_items_execute, mock_invoice_execute]
        
        with app.app_context():
            invoices.recalculate_invoice_totals(mock_db, 1)
            
            # Check that items were queried
            assert mock_db.execute.call_count >= 3  # Items query, invoice query, update query
            
            # Find the update call
            update_call = None
            for call in mock_db.execute.call_args_list:
                if 'UPDATE invoices SET' in call[0][0]:
                    update_call = call
                    break
            
            assert update_call is not None
            
            # Check calculations
            # Subtotal: 100 + 200 + 50 = 350
            # Taxable total: 100 + 200 = 300
            # Tax amount: 300 * 0.1 = 30
            # Total amount: 350 + 30 - 20 (discount) = 360
            # Balance due: 360 - 100 (paid) = 260
            params = update_call[0][1]
            assert 350.0 in params  # subtotal
            assert 30.0 in params   # tax_amount
            assert 360.0 in params  # total_amount
            assert 260.0 in params  # balance_due

    def test_get_invoice_payments(self, app, mock_get_db):
        """Test fetching payments for an invoice."""
        with app.app_context():
            invoices.get_invoice_payments(1)
            invoices.get_db().execute.assert_called_once()
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "SELECT * FROM payments WHERE invoice_id = ?" in call_args

    def test_record_payment(self, app, mock_get_db, test_payment_data):
        """Test recording a payment"""
        # Mock recalculate_invoice_totals
        with patch('app.services.invoices.recalculate_invoice_totals'):
            with app.app_context():
                payment_id = invoices.record_payment(test_payment_data)
                assert payment_id == 3  # From our mock lastrowid
                
                # Verify insert payment was called
                insert_calls = [call for call in invoices.get_db().execute.call_args_list 
                                if "INSERT INTO payments" in call[0][0]]
                assert len(insert_calls) > 0

    def test_mark_invoice_as_sent(self, app, mock_get_db):
        """Test marking an invoice as sent"""
        with app.app_context():
            invoices.mark_invoice_as_sent(1)
            
            # Verify update was called with right status
            update_calls = [call for call in invoices.get_db().execute.call_args_list 
                            if "UPDATE invoices SET" in call[0][0]]
            assert len(update_calls) > 0
            update_call = update_calls[-1][0]
            
            assert "status = ?, sent_date = ?" in update_call[0]
            assert Invoice.STATUS_SENT in update_call[1]

    def test_mark_invoice_as_cancelled(self, app, mock_get_db):
        """Test cancelling an invoice."""
        with app.app_context():
            invoices.mark_invoice_as_cancelled(1, "Test cancellation")
            
            # Verify update was called with right status
            update_calls = [call for call in invoices.get_db().execute.call_args_list 
                            if "UPDATE invoices SET" in call[0][0]]
            assert len(update_calls) > 0
            update_call = update_calls[-1][0]
            
            assert "status = ?" in update_call[0]
            assert Invoice.STATUS_CANCELLED in update_call[1]

    def test_get_overdue_invoices(self, app, mock_get_db):
        """Test getting overdue invoices."""
        with app.app_context():
            invoices.get_overdue_invoices()
            
            # Verify select with overdue condition
            select_calls = [call for call in invoices.get_db().execute.call_args_list 
                           if "SELECT * FROM invoices" in call[0][0]]
            assert len(select_calls) > 0
            select_call = select_calls[-1][0]
            
            assert "due_date < ?" in select_call[0]
            assert "status NOT IN" in select_call[0]
            
            # Status should exclude certain statuses
            excluded_statuses = [Invoice.STATUS_DRAFT, Invoice.STATUS_PAID, Invoice.STATUS_CANCELLED]
            for status in excluded_statuses:
                assert status in select_call[1]

    def test_get_upcoming_invoices(self, app, mock_get_db):
        """Test getting upcoming invoices."""
        with app.app_context():
            # Get invoices due in next 7 days
            invoices.get_upcoming_invoices(7)
            
            # Verify select with upcoming condition
            select_calls = [call for call in invoices.get_db().execute.call_args_list 
                           if "SELECT * FROM invoices" in call[0][0]]
            assert len(select_calls) > 0
            select_call = select_calls[-1][0]
            
            assert "due_date BETWEEN ? AND ?" in select_call[0]
            assert "status NOT IN" in select_call[0] 