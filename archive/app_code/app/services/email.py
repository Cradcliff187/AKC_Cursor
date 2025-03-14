"""
Mock email service for testing.
In a real application, this would connect to an email service provider.
"""
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import smtplib
from datetime import datetime

# Load environment variables
load_dotenv()

def send_email(to, subject, html_content, text_content=None, attachments=None):
    """
    Mock function to send an email
    """
    print(f"Mock: Email sent to {to} with subject '{subject}'")
    return True

def send_document_share_email(recipient_email, document_name, download_link, sender_name, message=None):
    """
    Mock function to send an email with a document share link
    """
    subject = f"{sender_name} shared a document with you: {document_name}"
    html_content = f"""
    <html>
    <body>
        <h2>{sender_name} has shared a document with you</h2>
        <p>Document: {document_name}</p>
        <p>Download link: {download_link}</p>
        {f"<p>Message: {message}</p>" if message else ""}
    </body>
    </html>
    """
    return send_email(recipient_email, subject, html_content)

def send_invoice_email(recipient_email, invoice_data, pdf_attachment=None):
    """
    Mock function to send an invoice email
    """
    subject = f"Invoice #{invoice_data.get('invoice_number', 'Unknown')} from AKC LLC Construction"
    html_content = f"""
    <html>
    <body>
        <h2>Invoice #{invoice_data.get('invoice_number', 'Unknown')}</h2>
        <p>Amount: ${invoice_data.get('total_amount', 0):.2f}</p>
        <p>Due date: {invoice_data.get('due_date', 'Unknown')}</p>
    </body>
    </html>
    """
    return send_email(recipient_email, subject, html_content, attachments=pdf_attachment)

def send_payment_receipt_email(recipient_email, payment_data, invoice_data):
    """
    Mock function to send a payment receipt email
    """
    subject = f"Payment Receipt for Invoice #{invoice_data.get('invoice_number', 'Unknown')}"
    html_content = f"""
    <html>
    <body>
        <h2>Payment Receipt</h2>
        <p>Invoice: #{invoice_data.get('invoice_number', 'Unknown')}</p>
        <p>Amount paid: ${payment_data.get('amount', 0):.2f}</p>
        <p>Payment date: {payment_data.get('payment_date', 'Unknown')}</p>
        <p>Payment method: {payment_data.get('payment_method', 'Unknown')}</p>
    </body>
    </html>
    """
    return send_email(recipient_email, subject, html_content)

def send_project_update_email(to, project, update_type, update_details=None):
    """
    Mock function to send a project update email
    """
    subject = f"Project Update: {project.get('name', 'Unknown')}"
    html_content = f"""
    <html>
    <body>
        <h2>Project Update: {project.get('name', 'Unknown')}</h2>
        <p>Update type: {update_type}</p>
        {f"<p>Details: {update_details}</p>" if update_details else ""}
    </body>
    </html>
    """
    return send_email(to, subject, html_content)

def send_task_assignment_email(to, task, project, assigned_by=None):
    """
    Mock function to send a task assignment email
    """
    subject = f"Task Assignment: {task.get('name', 'Unknown')}"
    html_content = f"""
    <html>
    <body>
        <h2>Task Assignment</h2>
        <p>Task: {task.get('name', 'Unknown')}</p>
        <p>Project: {project.get('name', 'Unknown')}</p>
        <p>Due date: {task.get('due_date', 'Unknown')}</p>
        {f"<p>Assigned by: {assigned_by}</p>" if assigned_by else ""}
    </body>
    </html>
    """
    return send_email(to, subject, html_content)

def send_report_email(to, report_name, report_data, attachment=None):
    """
    Mock function to send a report email
    """
    subject = f"Report: {report_name}"
    html_content = f"""
    <html>
    <body>
        <h2>Report: {report_name}</h2>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </body>
    </html>
    """
    return send_email(to, subject, html_content, attachments=attachment) 