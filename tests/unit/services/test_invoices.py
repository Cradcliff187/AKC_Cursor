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
        """Test fetching all invoices."""
        # Execute with app context since we're mocking get_db
        with app.app_context():
            invoices.get_all_invoices()
            # Check that execute was called with the right SQL
            invoices.get_db().execute.assert_called_once()
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "SELECT * FROM invoices" in call_args
    
    def test_get_all_invoices_with_filters(self, app, mock_get_db):
        """Test fetching invoices with filters."""
        with app.app_context():
            # Test with status filter
            invoices.get_all_invoices(status='Draft')
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "WHERE status = ?" in call_args
            
            # Reset mock for next test
            invoices.get_db().execute.reset_mock()
            
            # Test with client_id filter
            invoices.get_all_invoices(client_id=1)
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "WHERE client_id = ?" in call_args
            
            # Reset mock for next test
            invoices.get_db().execute.reset_mock()
            
            # Test with date filters
            date_from = '2023-01-01'
            date_to = '2023-12-31'
            invoices.get_all_invoices(date_from=date_from, date_to=date_to)
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "WHERE issue_date >= ? AND issue_date <= ?" in call_args
    
    def test_get_invoice_by_id(self, app, mock_get_db):
        """Test fetching a single invoice by ID."""
        with app.app_context():
            invoices.get_invoice_by_id(1)
            invoices.get_db().execute.assert_called_once()
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "SELECT * FROM invoices WHERE id = ?" in call_args
    
    def test_get_next_invoice_number(self, app, mock_get_db):
        """Test generating the next invoice number."""
        # Set up mock to return a result with a highest invoice number
        mock_fetchone = MagicMock()
        mock_fetchone.return_value = {'max_number': 'INV-005'}
        invoices.get_db().execute().fetchone = mock_fetchone
        
        with app.app_context():
            invoice_number = invoices.get_next_invoice_number()
            assert invoice_number == 'INV-006'
            
            # Test with no existing invoices
            mock_fetchone.return_value = {'max_number': None}
            invoice_number = invoices.get_next_invoice_number()
            assert invoice_number == 'INV-001'
    
    def test_create_invoice(self, app, mock_get_db, test_invoice_data, test_invoice_item_data):
        """Test creating a new invoice."""
        # Mock get_next_invoice_number
        with patch('app.services.invoices.get_next_invoice_number', return_value='INV-TEST'):
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
        """Test updating an existing invoice."""
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
        """Test deleting an invoice."""
        with app.app_context():
            invoices.delete_invoice(1)
            
            # Should delete items and payments first, then invoice
            assert invoices.get_db().execute.call_count >= 3
            
            # Check last call was to delete the invoice
            call_args = invoices.get_db().execute.call_args[0]
            assert "DELETE FROM invoices WHERE id = ?" in call_args[0]
    
    def test_get_invoice_items(self, app, mock_get_db):
        """Test fetching items for an invoice."""
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
        """Test recalculating invoice totals."""
        # Mock the item retrieval
        items = [
            {'amount': 100, 'taxable': 1},
            {'amount': 200, 'taxable': 1},
            {'amount': 300, 'taxable': 0}
        ]
        
        mock_fetchall = MagicMock(return_value=items)
        invoices.get_db().execute().fetchall = mock_fetchall
        
        # Mock the invoice retrieval
        invoice = {'tax_rate': 10, 'amount_paid': 200}
        mock_fetchone = MagicMock(return_value=invoice)
        invoices.get_db().execute().fetchone = mock_fetchone
        
        with app.app_context():
            invoices.recalculate_invoice_totals(invoices.get_db(), 1)
            
            # Should query items and invoice, then update totals
            assert invoices.get_db().execute.call_count >= 3
            
            # Check update call
            update_calls = [call for call in invoices.get_db().execute.call_args_list 
                            if "UPDATE invoices SET" in call[0][0]]
            assert len(update_calls) > 0
            update_call = update_calls[-1][0]
            
            # Expected values
            # Subtotal = 100 + 200 + 300 = 600
            # Tax amount = (100 + 200) * 10% = 30
            # Total = 600 + 30 = 630
            # Balance = 630 - 200 = 430
            
            assert "subtotal = ?, tax_amount = ?, total_amount = ?, balance_due = ?" in update_call[0]
            assert 600 in update_call[1]  # subtotal
            assert 30 in update_call[1]  # tax_amount
            assert 630 in update_call[1]  # total_amount
            assert 430 in update_call[1]  # balance_due
    
    def test_get_invoice_payments(self, app, mock_get_db):
        """Test fetching payments for an invoice."""
        with app.app_context():
            invoices.get_invoice_payments(1)
            invoices.get_db().execute.assert_called_once()
            call_args = invoices.get_db().execute.call_args[0][0]
            assert "SELECT * FROM payments WHERE invoice_id = ?" in call_args
    
    def test_record_payment(self, app, mock_get_db, test_payment_data):
        """Test recording a payment."""
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
        """Test marking an invoice as sent."""
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