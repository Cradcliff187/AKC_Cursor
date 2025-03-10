import pytest
import json
from app.db import get_db
from app.models.invoice import Invoice

@pytest.mark.functional
class TestInvoices:
    
    def test_invoice_list(self, with_admin_user):
        """Test listing invoices."""
        response = with_admin_user.get('/invoices/')
        assert response.status_code == 200
        assert b'INV-001' in response.data
        assert b'INV-002' in response.data
    
    def test_invoice_detail(self, with_admin_user, test_invoice_id):
        """Test viewing invoice details."""
        response = with_admin_user.get(f'/invoices/{test_invoice_id}')
        assert response.status_code == 200
        assert b'INV-001' in response.data
        assert b'Test Client 1' in response.data
        assert b'Draft' in response.data
        assert b'Design Services' in response.data
        assert b'Construction Materials' in response.data
    
    def test_create_invoice(self, with_admin_user, app, test_invoice_data):
        """Test creating a new invoice."""
        response = with_admin_user.post(
            '/invoices/create',
            data=test_invoice_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Invoice created successfully' in response.data
        
        # Verify invoice was added to the database
        with app.app_context():
            db = get_db()
            # Get the latest invoice created
            invoice = db.execute(
                "SELECT * FROM invoices ORDER BY id DESC LIMIT 1"
            ).fetchone()
            assert invoice is not None
            assert invoice['client_id'] == test_invoice_data['client_id']
            assert invoice['project_id'] == test_invoice_data['project_id']
            assert float(invoice['tax_rate']) == test_invoice_data['tax_rate']
            assert invoice['notes'] == test_invoice_data['notes']
            assert invoice['terms'] == test_invoice_data['terms']
            assert invoice['status'] == Invoice.STATUS_DRAFT
    
    def test_add_invoice_items(self, with_admin_user, app, test_invoice_id, test_invoice_item_data):
        """Test adding items to an invoice."""
        # Convert items data to JSON
        items_json = json.dumps(test_invoice_item_data)
        
        response = with_admin_user.post(
            f'/invoices/{test_invoice_id}/items',
            data={'item_data': items_json},
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Check if API returns success
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        
        # Verify items were added to the database
        with app.app_context():
            db = get_db()
            # Get all items for this invoice
            items = db.execute(
                f"SELECT * FROM invoice_items WHERE invoice_id = {test_invoice_id}"
            ).fetchall()
            
            # Should have at least as many items as we added
            assert len(items) >= len(test_invoice_item_data)
            
            # Check if our items are in the database
            found_items = 0
            for test_item in test_invoice_item_data:
                for db_item in items:
                    if (db_item['description'] == test_item['description'] and 
                        float(db_item['unit_price']) == test_item['unit_price']):
                        found_items += 1
                        break
            
            assert found_items == len(test_invoice_item_data)
    
    def test_send_invoice(self, with_admin_user, app, test_invoice_id):
        """Test marking an invoice as sent."""
        # First ensure invoice is in Draft status
        with app.app_context():
            db = get_db()
            db.execute(
                f"UPDATE invoices SET status = '{Invoice.STATUS_DRAFT}' WHERE id = {test_invoice_id}"
            )
            db.commit()
        
        # Mark invoice as sent
        response = with_admin_user.post(
            f'/invoices/{test_invoice_id}/send',
            data={'send_email': 'no'},  # Don't actually send email during test
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Invoice marked as sent' in response.data
        
        # Verify invoice status was updated
        with app.app_context():
            db = get_db()
            invoice = db.execute(
                f"SELECT * FROM invoices WHERE id = {test_invoice_id}"
            ).fetchone()
            assert invoice['status'] == Invoice.STATUS_SENT
            assert invoice['sent_date'] is not None
    
    def test_record_payment(self, with_admin_user, app, test_payment_data):
        """Test recording a payment for an invoice."""
        response = with_admin_user.post(
            f'/invoices/{test_payment_data["invoice_id"]}/payment',
            data=test_payment_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Payment recorded successfully' in response.data
        
        # Verify payment was added to the database
        with app.app_context():
            db = get_db()
            payment = db.execute(
                f"SELECT * FROM payments WHERE invoice_id = {test_payment_data['invoice_id']} ORDER BY id DESC LIMIT 1"
            ).fetchone()
            assert payment is not None
            assert float(payment['amount']) == test_payment_data['amount']
            assert payment['payment_method'] == test_payment_data['payment_method']
            assert payment['reference_number'] == test_payment_data['reference_number']
            
            # Check that invoice was updated
            invoice = db.execute(
                f"SELECT * FROM invoices WHERE id = {test_payment_data['invoice_id']}"
            ).fetchone()
            assert float(invoice['amount_paid']) >= test_payment_data['amount']
            assert invoice['balance_due'] == float(invoice['total_amount']) - float(invoice['amount_paid'])
            
            # Check if status is updated correctly
            if float(invoice['balance_due']) == 0:
                assert invoice['status'] == Invoice.STATUS_PAID
            elif float(invoice['amount_paid']) > 0:
                assert invoice['status'] == Invoice.STATUS_PARTIAL
    
    def test_print_invoice(self, with_admin_user, test_invoice_id):
        """Test printing an invoice."""
        response = with_admin_user.get(f'/invoices/{test_invoice_id}/print')
        assert response.status_code == 200
        assert b'INVOICE' in response.data
        assert b'INV-001' in response.data
        assert b'Print Invoice' in response.data
    
    def test_cancel_invoice(self, with_admin_user, app, test_invoice_id):
        """Test cancelling an invoice."""
        # Ensure invoice is not already cancelled or paid
        with app.app_context():
            db = get_db()
            db.execute(
                f"UPDATE invoices SET status = '{Invoice.STATUS_SENT}' WHERE id = {test_invoice_id}"
            )
            db.commit()
        
        response = with_admin_user.post(
            f'/invoices/{test_invoice_id}/cancel',
            data={'reason': 'Testing cancellation'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Invoice cancelled successfully' in response.data
        
        # Verify invoice status was updated
        with app.app_context():
            db = get_db()
            invoice = db.execute(
                f"SELECT * FROM invoices WHERE id = {test_invoice_id}"
            ).fetchone()
            assert invoice['status'] == Invoice.STATUS_CANCELLED
    
    def test_delete_invoice(self, with_admin_user, app):
        """Test deleting a draft invoice."""
        # Create a draft invoice to delete
        with app.app_context():
            db = get_db()
            cursor = db.execute(
                """INSERT INTO invoices 
                   (invoice_number, client_id, project_id, status, issue_date, due_date, 
                    subtotal, tax_rate, tax_amount, total_amount, balance_due)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ('INV-TEST-DELETE', 1, 1, 'Draft', '2023-03-01', '2023-04-01', 500.00, 8.0, 40.00, 540.00, 540.00)
            )
            invoice_id = cursor.lastrowid
            db.commit()
        
        response = with_admin_user.post(
            f'/invoices/{invoice_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Invoice deleted successfully' in response.data
        
        # Verify invoice was deleted
        with app.app_context():
            db = get_db()
            invoice = db.execute(
                f"SELECT * FROM invoices WHERE id = {invoice_id}"
            ).fetchone()
            assert invoice is None
    
    def test_invoice_dashboard(self, with_admin_user):
        """Test invoice dashboard."""
        response = with_admin_user.get('/invoices/dashboard')
        assert response.status_code == 200
        # Dashboard should show statistics
        assert b'Dashboard' in response.data
        assert b'Overdue' in response.data or b'Invoice Status' in response.data
    
    def test_client_invoices(self, with_admin_user, test_client_id):
        """Test viewing invoices for a specific client."""
        response = with_admin_user.get(f'/invoices/client/{test_client_id}')
        assert response.status_code == 200
        assert b'Test Client 1' in response.data
        assert b'INV-001' in response.data  # First client's invoice
    
    def test_unauthorized_invoice_access(self, client):
        """Test unauthorized access to invoice pages."""
        # Try accessing invoices without login
        response = client.get('/invoices/', follow_redirects=True)
        assert response.status_code == 200
        assert b'Log In' in response.data 