"""
Unit tests for email service
"""
import pytest
from app.services.email import (
    send_email, send_document_share_email, send_invoice_email,
    send_payment_receipt_email, send_project_update_email,
    send_task_assignment_email, send_report_email
)

def test_send_email(capsys):
    """Test the basic send_email function"""
    # Test basic email
    result = send_email('test@example.com', 'Test Subject', '<p>Test content</p>')
    assert result is True
    
    # Check that it logged the email (using capsys to capture stdout)
    captured = capsys.readouterr()
    assert "Email sent to test@example.com with subject 'Test Subject'" in captured.out
    
    # Test with attachments
    attachments = [{'filename': 'test.pdf', 'content': b'test content'}]
    result = send_email('test@example.com', 'Test Subject', '<p>Test content</p>', attachments=attachments)
    assert result is True

def test_send_document_share_email(monkeypatch):
    """Test the document sharing email function"""
    # Mock the send_email function
    mock_calls = []
    def mock_send_email(to, subject, html_content, *args, **kwargs):
        mock_calls.append({
            'to': to,
            'subject': subject,
            'html_content': html_content
        })
        return True
        
    monkeypatch.setattr('app.services.email.send_email', mock_send_email)
    
    # Call the function
    result = send_document_share_email(
        recipient_email='client@example.com',
        document_name='Contract.pdf',
        download_link='https://example.com/download/123',
        sender_name='John Doe',
        message='Please review this document'
    )
    
    # Check result and mock calls
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['to'] == 'client@example.com'
    assert 'John Doe shared a document with you: Contract.pdf' in mock_calls[0]['subject']
    assert 'Contract.pdf' in mock_calls[0]['html_content']
    assert 'John Doe has shared a document with you' in mock_calls[0]['html_content']
    assert 'https://example.com/download/123' in mock_calls[0]['html_content']
    assert 'Please review this document' in mock_calls[0]['html_content']
    
    # Test without message
    mock_calls.clear()
    result = send_document_share_email(
        recipient_email='client@example.com',
        document_name='Contract.pdf',
        download_link='https://example.com/download/123',
        sender_name='John Doe'
    )
    
    assert result is True
    assert len(mock_calls) == 1
    assert 'Please review this document' not in mock_calls[0]['html_content']

def test_send_invoice_email(monkeypatch):
    """Test the invoice email function"""
    # Mock the send_email function
    mock_calls = []
    def mock_send_email(to, subject, html_content, *args, **kwargs):
        mock_calls.append({
            'to': to,
            'subject': subject,
            'html_content': html_content,
            'attachments': kwargs.get('attachments')
        })
        return True
        
    monkeypatch.setattr('app.services.email.send_email', mock_send_email)
    
    # Call the function
    invoice_data = {
        'invoice_number': 'INV-001',
        'total_amount': 1000.00,
        'due_date': '2023-03-31'
    }
    pdf_attachment = {
        'filename': 'invoice.pdf',
        'content': b'test content'
    }
    
    result = send_invoice_email(
        recipient_email='client@example.com',
        invoice_data=invoice_data,
        pdf_attachment=pdf_attachment
    )
    
    # Check result and mock calls
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['to'] == 'client@example.com'
    assert 'Invoice #INV-001' in mock_calls[0]['subject']
    assert 'INV-001' in mock_calls[0]['html_content']
    assert '1000.00' in mock_calls[0]['html_content']
    assert '2023-03-31' in mock_calls[0]['html_content']
    assert mock_calls[0]['attachments'] == pdf_attachment
    
    # Test without attachment
    mock_calls.clear()
    result = send_invoice_email(
        recipient_email='client@example.com',
        invoice_data=invoice_data
    )
    
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['attachments'] is None

def test_send_payment_receipt_email(monkeypatch):
    """Test the payment receipt email function"""
    # Mock the send_email function
    mock_calls = []
    def mock_send_email(to, subject, html_content, *args, **kwargs):
        mock_calls.append({
            'to': to,
            'subject': subject,
            'html_content': html_content
        })
        return True
        
    monkeypatch.setattr('app.services.email.send_email', mock_send_email)
    
    # Call the function
    payment_data = {
        'amount': 500.00,
        'payment_date': '2023-03-01',
        'payment_method': 'Credit Card'
    }
    invoice_data = {
        'invoice_number': 'INV-001',
        'total_amount': 1000.00
    }
    
    result = send_payment_receipt_email(
        recipient_email='client@example.com',
        payment_data=payment_data,
        invoice_data=invoice_data
    )
    
    # Check result and mock calls
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['to'] == 'client@example.com'
    assert 'Payment Receipt for Invoice #INV-001' in mock_calls[0]['subject']
    assert 'INV-001' in mock_calls[0]['html_content']
    assert '500.00' in mock_calls[0]['html_content']
    assert '2023-03-01' in mock_calls[0]['html_content']
    assert 'Credit Card' in mock_calls[0]['html_content']

def test_send_project_update_email(monkeypatch):
    """Test the project update email function"""
    # Mock the send_email function
    mock_calls = []
    def mock_send_email(to, subject, html_content, *args, **kwargs):
        mock_calls.append({
            'to': to,
            'subject': subject,
            'html_content': html_content
        })
        return True
        
    monkeypatch.setattr('app.services.email.send_email', mock_send_email)
    
    # Call the function
    project = {
        'name': 'Test Project',
        'id': 1
    }
    
    result = send_project_update_email(
        to='team@example.com',
        project=project,
        update_type='milestone_completed',
        update_details='Milestone 1 has been completed'
    )
    
    # Check result and mock calls
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['to'] == 'team@example.com'
    assert 'Project Update: Test Project' in mock_calls[0]['subject']
    assert 'Test Project' in mock_calls[0]['html_content']
    assert 'milestone_completed' in mock_calls[0]['html_content']
    assert 'Milestone 1 has been completed' in mock_calls[0]['html_content']
    
    # Test without details
    mock_calls.clear()
    result = send_project_update_email(
        to='team@example.com',
        project=project,
        update_type='status_changed'
    )
    
    assert result is True
    assert len(mock_calls) == 1
    assert 'status_changed' in mock_calls[0]['html_content']
    assert 'Milestone 1 has been completed' not in mock_calls[0]['html_content']

def test_send_task_assignment_email(monkeypatch):
    """Test the task assignment email function"""
    # Mock the send_email function
    mock_calls = []
    def mock_send_email(to, subject, html_content, *args, **kwargs):
        mock_calls.append({
            'to': to,
            'subject': subject,
            'html_content': html_content
        })
        return True
        
    monkeypatch.setattr('app.services.email.send_email', mock_send_email)
    
    # Call the function
    task = {
        'name': 'Test Task',
        'id': 1,
        'due_date': '2023-04-15'
    }
    project = {
        'name': 'Test Project',
        'id': 1
    }
    
    result = send_task_assignment_email(
        to='worker@example.com',
        task=task,
        project=project,
        assigned_by='Manager'
    )
    
    # Check result and mock calls
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['to'] == 'worker@example.com'
    assert 'Task Assignment: Test Task' in mock_calls[0]['subject']
    assert 'Test Task' in mock_calls[0]['html_content']
    assert 'Test Project' in mock_calls[0]['html_content']
    assert '2023-04-15' in mock_calls[0]['html_content']
    assert 'Manager' in mock_calls[0]['html_content']
    
    # Test without assigned_by
    mock_calls.clear()
    result = send_task_assignment_email(
        to='worker@example.com',
        task=task,
        project=project
    )
    
    assert result is True
    assert len(mock_calls) == 1
    assert 'Manager' not in mock_calls[0]['html_content']

def test_send_report_email(monkeypatch):
    """Test the report email function"""
    # Mock the send_email function
    mock_calls = []
    def mock_send_email(to, subject, html_content, *args, **kwargs):
        mock_calls.append({
            'to': to,
            'subject': subject,
            'html_content': html_content,
            'attachments': kwargs.get('attachments')
        })
        return True
        
    monkeypatch.setattr('app.services.email.send_email', mock_send_email)
    
    # Call the function
    report_data = {
        'total_projects': 15,
        'active_projects': 8
    }
    attachment = {
        'filename': 'report.pdf',
        'content': b'test content'
    }
    
    result = send_report_email(
        to='manager@example.com',
        report_name='Monthly Project Summary',
        report_data=report_data,
        attachment=attachment
    )
    
    # Check result and mock calls
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['to'] == 'manager@example.com'
    assert 'Report: Monthly Project Summary' in mock_calls[0]['subject']
    assert 'Monthly Project Summary' in mock_calls[0]['html_content']
    assert mock_calls[0]['attachments'] == attachment
    
    # Test without attachment
    mock_calls.clear()
    result = send_report_email(
        to='manager@example.com',
        report_name='Monthly Project Summary',
        report_data=report_data
    )
    
    assert result is True
    assert len(mock_calls) == 1
    assert mock_calls[0]['attachments'] is None 