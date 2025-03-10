import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv
import smtplib
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
from flask import render_template, url_for

# Load environment variables
load_dotenv()

# Configure email settings
GOOGLE_SERVICE_ACCOUNT_INFO = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
GOOGLE_WORKSPACE_ADMIN_EMAIL = os.environ.get('GOOGLE_WORKSPACE_ADMIN_EMAIL')
DEFAULT_SENDER = os.environ.get('DEFAULT_EMAIL_SENDER', 'noreply@example.com')
EMAIL_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'emails')

# Configure Jinja environment for email templates
template_env = Environment(loader=FileSystemLoader(EMAIL_TEMPLATES_DIR))

def get_service_account_credentials():
    """Get service account credentials for admin operations"""
    if not GOOGLE_SERVICE_ACCOUNT_INFO:
        return None
        
    try:
        service_account_info = json.loads(GOOGLE_SERVICE_ACCOUNT_INFO)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        # Delegate credentials to admin
        if GOOGLE_WORKSPACE_ADMIN_EMAIL:
            credentials = credentials.with_subject(GOOGLE_WORKSPACE_ADMIN_EMAIL)
            
        return credentials
    except Exception as e:
        print(f"Error creating service account credentials: {e}")
        return None

def get_gmail_service():
    """Get Gmail API service using admin service account"""
    credentials = get_service_account_credentials()
    if not credentials:
        return None
        
    try:
        service = build('gmail', 'v1', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None

def create_message(sender, to, subject, message_html, message_text=None, attachments=None):
    """Create an email message with optional attachments"""
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = to
    
    # Attach plain text and HTML versions
    if message_text:
        message.attach(MIMEText(message_text, 'plain'))
    message.attach(MIMEText(message_html, 'html'))
    
    # Attach files if provided
    if attachments:
        for attachment in attachments:
            filename = attachment.get('filename')
            content = attachment.get('content')
            content_type = attachment.get('content_type', 'application/octet-stream')
            
            if filename and content:
                part = MIMEApplication(content)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                part.add_header('Content-Type', content_type)
                message.attach(part)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(to, subject, template_name, template_data, attachments=None):
    """Send an email using Gmail API with a template"""
    # Get Gmail service
    service = get_gmail_service()
    if not service:
        print("Gmail service not available")
        return False
    
    try:
        # Get the template
        template = template_env.get_template(f"{template_name}.html")
        
        # Add common template data
        template_data.update({
            'current_year': datetime.now().year,
            'app_name': 'Construction CRM',
            'company_name': 'AKC LLC',
            'support_email': DEFAULT_SENDER
        })
        
        # Render the template
        message_html = template.render(**template_data)
        
        # Create the message
        message = create_message(
            sender=DEFAULT_SENDER,
            to=to,
            subject=subject,
            message_html=message_html,
            attachments=attachments
        )
        
        # Send the message
        send_result = service.users().messages().send(userId='me', body=message).execute()
        print(f"Email sent to {to}, message_id: {send_result.get('id')}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_notification_email(to, notification):
    """Send an email for a notification"""
    return send_email(
        to=to,
        subject=notification.title,
        template_name='notification',
        template_data={
            'notification': notification,
            'action_url': notification.action_url
        }
    )

def send_document_share_email(recipient_email, sender_name, document_name, download_url, message=None):
    """Send an email to a recipient with a link to download a shared document"""
    subject = f"{sender_name} shared a document with you: {document_name}"
    
    # Create context for email template
    context = {
        'sender_name': sender_name,
        'document_name': document_name,
        'download_url': download_url,
        'message': message
    }
    
    # Render the email template
    html_content = render_template('emails/document_share.html', **context)
    
    # Send the email
    return send_email(recipient_email, subject, html_content)

def send_invoice_email(invoice_id, email_type='new'):
    """
    Send an invoice email to a client
    
    Args:
        invoice_id: The ID of the invoice to send
        email_type: Type of email - 'new' (new invoice), 'reminder' (payment reminder), 'receipt' (payment receipt)
    
    Returns:
        Boolean indicating success or failure
    """
    from app.services.invoices import get_invoice_by_id, get_invoice_items, get_invoice_payments
    from app.services.clients import get_client_by_id
    
    # Get invoice, items, and client information
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        return False
    
    items = get_invoice_items(invoice_id)
    
    client = get_client_by_id(invoice['client_id'])
    if not client or not client.get('email'):
        return False
    
    # Get the client's email
    recipient_email = client['email']
    
    # Setup email variables based on email type
    if email_type == 'new':
        subject = f"Invoice #{invoice['invoice_number']} from AKC LLC Construction"
        template = 'emails/invoice_new.html'
        
    elif email_type == 'reminder':
        subject = f"Payment Reminder: Invoice #{invoice['invoice_number']} from AKC LLC Construction"
        template = 'emails/invoice_reminder.html'
        
    elif email_type == 'receipt':
        subject = f"Payment Receipt for Invoice #{invoice['invoice_number']} from AKC LLC Construction"
        template = 'emails/invoice_receipt.html'
        # Get the most recent payment
        payments = get_invoice_payments(invoice_id)
        last_payment = payments[-1] if payments else None
        
    else:
        return False  # Invalid email type
    
    # Get company info
    company_info = {
        'name': 'AKC LLC Construction',
        'address': '123 Construction Way',
        'city': 'Anytown',
        'state': 'NY',
        'zip': '12345',
        'phone': '(555) 123-4567',
        'email': 'info@akcllcconstruction.com',
        'website': 'www.akcllcconstruction.com',
        'logo_url': 'img/akc-logo.jpg'  # For email templates, use a web-accessible URL
    }
    
    # Create context for email template
    context = {
        'invoice': invoice,
        'items': items,
        'client': client,
        'company': company_info,
        'view_url': url_for('invoices.view_invoice', invoice_id=invoice_id, _external=True),
    }
    
    # Add email type specific context
    if email_type == 'receipt' and last_payment:
        context['payment'] = last_payment
    
    # Render the email template
    html_content = render_template(template, **context)
    
    # Send the email
    success = send_email(recipient_email, subject, html_content)
    
    # If the email was sent successfully and it's a new invoice, mark it as sent
    if success and email_type == 'new':
        from app.services.invoices import mark_invoice_as_sent
        mark_invoice_as_sent(invoice_id)
        
    return success

def send_project_update_email(to, project, update_type, update_details=None):
    """Send an email with project updates"""
    return send_email(
        to=to,
        subject=f"Project Update: {project.name}",
        template_name='project_update',
        template_data={
            'project': project,
            'update_type': update_type,
            'update_details': update_details
        }
    )

def send_task_assignment_email(to, task, project, assigned_by=None):
    """Send an email for a task assignment"""
    return send_email(
        to=to,
        subject=f"New Task Assignment: {task.title}",
        template_name='task_assignment',
        template_data={
            'task': task,
            'project': project,
            'assigned_by': assigned_by
        }
    )

def send_report_email(to, report_name, report_data, attachment=None):
    """Send an email with a report"""
    attachments = None
    if attachment:
        attachments = [{
            'filename': attachment.get('filename'),
            'content': attachment.get('content'),
            'content_type': attachment.get('content_type', 'application/pdf')
        }]
        
    return send_email(
        to=to,
        subject=f"Construction CRM Report: {report_name}",
        template_name='report',
        template_data={
            'report_name': report_name,
            'report_data': report_data
        },
        attachments=attachments
    )

def send_schedule_reminder_email(to, events):
    """Send a daily schedule reminder email"""
    return send_email(
        to=to,
        subject=f"Your Schedule for {datetime.now().strftime('%B %d, %Y')}",
        template_name='schedule_reminder',
        template_data={
            'events': events,
            'date': datetime.now()
        }
    ) 