"""
Insert All Test Data

This script inserts test data for all tables in the Supabase database.
"""

import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client

def check_environment():
    """Check if the required environment variables are set."""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the .env file.")
        print(f"SUPABASE_URL: {'Set' if supabase_url else 'Not set'}")
        print(f"SUPABASE_SERVICE_ROLE_KEY: {'Set' if supabase_key else 'Not set'}")
        sys.exit(1)
    
    return supabase_url, supabase_key

def insert_user_profile(supabase):
    """Insert a test user profile."""
    print("\nInserting test user profile...")
    
    user_id = str(uuid.uuid4())
    
    try:
        data = {
            'id': user_id,
            'auth_id': f'auth_{user_id}',
            'email': f'test_{user_id[:8]}@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'display_name': 'John Doe',
            'role': 'admin',
            'status': 'active',
            'phone': '555-123-4567',
            'avatar_url': 'https://randomuser.me/api/portraits/men/1.jpg',
            'title': 'Project Manager',
            'hire_date': datetime.now(timezone.utc).isoformat(),
            'last_login': datetime.now(timezone.utc).isoformat(),
            'preferences': {},
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('user_profiles').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted user profile with ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"[ERROR] Error inserting user profile: {str(e)}")
        return None

def insert_client(supabase):
    """Insert a test client."""
    print("\nInserting test client...")
    
    client_id = str(uuid.uuid4())
    
    try:
        data = {
            'id': client_id,
            'name': 'Acme Corporation',
            'contact_name': 'Wile E. Coyote',
            'email': 'wile@acme.com',
            'phone': '555-111-2222',
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'zip_code': '85001',
            'notes': 'Large commercial client',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('clients').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted client with ID: {client_id}")
        return client_id
    except Exception as e:
        print(f"[ERROR] Error inserting client: {str(e)}")
        return None

def insert_project(supabase, client_id):
    """Insert a test project."""
    print("\nInserting test project...")
    
    if not client_id:
        print("[ERROR] Cannot insert project without a valid client ID.")
        return None
    
    project_id = str(uuid.uuid4())
    
    try:
        data = {
            'id': project_id,
            'name': 'Acme HQ Renovation',
            'client_id': client_id,
            'description': 'Complete renovation of Acme headquarters',
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'zip_code': '85001',
            'status': 'active',
            'start_date': datetime.now(timezone.utc).isoformat(),
            'end_date': (datetime.now(timezone.utc) + timedelta(days=180)).isoformat(),
            'estimated_budget': 150000.00,
            'actual_budget': 0.00,
            'created_by_id': None,  # Will be updated later with user ID
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('projects').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted project with ID: {project_id}")
        return project_id
    except Exception as e:
        print(f"[ERROR] Error inserting project: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': project_id,
                'name': 'Acme HQ Renovation',
                'client_id': client_id,
                'status': 'active'
            }
            
            response = supabase.table('projects').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted project with minimal data, ID: {project_id}")
            return project_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting project with minimal data: {str(minimal_error)}")
            return None

def insert_project_task(supabase, project_id, user_id):
    """Insert a test project task."""
    print("\nInserting test project task...")
    
    if not project_id:
        print("[ERROR] Cannot insert project task without a valid project ID.")
        return None
    
    task_id = str(uuid.uuid4())
    
    try:
        data = {
            'id': task_id,
            'project_id': project_id,
            'name': 'Demolition',
            'description': 'Interior demolition of existing structures',
            'status': 'pending',
            'priority': 'high',
            'assigned_to': user_id,
            'start_date': datetime.now(timezone.utc).isoformat(),
            'due_date': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            'completed_at': None,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('project_tasks').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted project task with ID: {task_id}")
        return task_id
    except Exception as e:
        print(f"[ERROR] Error inserting project task: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': task_id,
                'project_id': project_id,
                'name': 'Demolition',
                'status': 'pending'
            }
            
            response = supabase.table('project_tasks').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted project task with minimal data, ID: {task_id}")
            return task_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting project task with minimal data: {str(minimal_error)}")
            return None

def insert_task(supabase, project_id, user_id):
    """Insert a test task (for time_entries)."""
    print("\nInserting test task...")
    
    if not project_id:
        print("[ERROR] Cannot insert task without a valid project ID.")
        return None
    
    task_id = str(uuid.uuid4())
    
    try:
        # Since we don't know the exact schema, we'll try with common fields
        data = {
            'id': task_id,
            'project_id': project_id,
            'name': 'Framing',
            'description': 'Framing of interior walls',
            'status': 'pending',
            'assigned_to': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('tasks').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted task with ID: {task_id}")
        return task_id
    except Exception as e:
        print(f"[ERROR] Error inserting task: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': task_id,
                'project_id': project_id,
                'name': 'Framing'
            }
            
            response = supabase.table('tasks').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted task with minimal data, ID: {task_id}")
            return task_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting task with minimal data: {str(minimal_error)}")
            return None

def insert_invoice(supabase, client_id, project_id):
    """Insert a test invoice."""
    print("\nInserting test invoice...")
    
    if not client_id or not project_id:
        print("[ERROR] Cannot insert invoice without valid client and project IDs.")
        return None
    
    invoice_id = str(uuid.uuid4())
    # Generate a unique invoice number using the current timestamp
    unique_invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        # Based on the error message, we need to include balance_due
        data = {
            'id': invoice_id,
            'client_id': client_id,
            'project_id': project_id,
            'invoice_number': unique_invoice_number,
            'status': 'sent',
            'issue_date': datetime.now(timezone.utc).isoformat(),
            'due_date': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            'subtotal': 50000.00,  # Required field
            'total_amount': 54000.00,  # Required field
            'balance_due': 54000.00,  # Required field
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('invoices').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted invoice with ID: {invoice_id}")
        return invoice_id
    except Exception as e:
        print(f"[ERROR] Error inserting invoice: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': invoice_id,
                'client_id': client_id,
                'project_id': project_id,
                'invoice_number': unique_invoice_number,
                'status': 'sent',
                'issue_date': datetime.now(timezone.utc).isoformat(),
                'due_date': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                'subtotal': 50000.00,  # Required field
                'total_amount': 54000.00,  # Required field
                'balance_due': 54000.00  # Required field
            }
            
            response = supabase.table('invoices').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted invoice with minimal data, ID: {invoice_id}")
            return invoice_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting invoice with minimal data: {str(minimal_error)}")
            return None

def insert_invoice_item(supabase, invoice_id):
    """Insert a test invoice item."""
    print("\nInserting test invoice item...")
    
    if not invoice_id:
        print("[ERROR] Cannot insert invoice item without a valid invoice ID.")
        return None
    
    item_id = str(uuid.uuid4())
    
    try:
        # Based on the error message, we need to include amount
        data = {
            'id': item_id,
            'invoice_id': invoice_id,
            'description': 'Demolition services',
            'quantity': 1,
            'unit_price': 30000.00,
            'amount': 30000.00,  # Required field
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('invoice_items').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted invoice item with ID: {item_id}")
        return item_id
    except Exception as e:
        print(f"[ERROR] Error inserting invoice item: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': item_id,
                'invoice_id': invoice_id,
                'description': 'Demolition services',
                'quantity': 1,
                'amount': 30000.00  # Required field
            }
            
            response = supabase.table('invoice_items').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted invoice item with minimal data, ID: {item_id}")
            return item_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting invoice item with minimal data: {str(minimal_error)}")
            return None

def insert_payment(supabase, invoice_id):
    """Insert a test payment."""
    print("\nInserting test payment...")
    
    if not invoice_id:
        print("[ERROR] Cannot insert payment without a valid invoice ID.")
        return None
    
    payment_id = str(uuid.uuid4())
    
    try:
        # Since we don't know the exact schema, we'll try with common fields
        data = {
            'id': payment_id,
            'invoice_id': invoice_id,
            'amount': 54000.00,
            'payment_date': datetime.now(timezone.utc).isoformat(),
            'payment_method': 'check',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('payments').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted payment with ID: {payment_id}")
        return payment_id
    except Exception as e:
        print(f"[ERROR] Error inserting payment: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': payment_id,
                'invoice_id': invoice_id,
                'amount': 54000.00,
                'payment_date': datetime.now(timezone.utc).isoformat()
            }
            
            response = supabase.table('payments').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted payment with minimal data, ID: {payment_id}")
            return payment_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting payment with minimal data: {str(minimal_error)}")
            return None

def insert_user_notification(supabase, user_id):
    """Insert a test user notification."""
    print("\nInserting test user notification...")
    
    if not user_id:
        print("[ERROR] Cannot insert user notification without a valid user ID.")
        return None
    
    notification_id = str(uuid.uuid4())
    
    try:
        data = {
            'id': notification_id,
            'user_id': user_id,
            'title': 'New Invoice Paid',
            'message': 'Acme Corporation has paid invoice INV-2023-001',
            'type': 'info',
            'is_read': False,
            'link': '/invoices/inv-2023-001',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'read_at': None
        }
        
        response = supabase.table('user_notifications').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted user notification with ID: {notification_id}")
        return notification_id
    except Exception as e:
        print(f"[ERROR] Error inserting user notification: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': notification_id,
                'user_id': user_id,
                'title': 'New Invoice Paid',
                'message': 'Acme Corporation has paid invoice INV-2023-001',
                'type': 'info'
            }
            
            response = supabase.table('user_notifications').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted user notification with minimal data, ID: {notification_id}")
            return notification_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting user notification with minimal data: {str(minimal_error)}")
            return None

def insert_bid(supabase, client_id, project_id):
    """Insert a test bid."""
    print("\nInserting test bid...")
    
    if not client_id or not project_id:
        print("[ERROR] Cannot insert bid without valid client and project IDs.")
        return None
    
    bid_id = str(uuid.uuid4())
    
    try:
        # Based on the error message, we need to include name
        data = {
            'id': bid_id,
            'project_id': project_id,
            'client_id': client_id,
            'name': 'Acme HQ Renovation Bid',  # Required field
            'status': 'pending',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('bids').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted bid with ID: {bid_id}")
        return bid_id
    except Exception as e:
        print(f"[ERROR] Error inserting bid: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': bid_id,
                'project_id': project_id,
                'client_id': client_id,
                'name': 'Acme HQ Renovation Bid',  # Required field
                'status': 'pending'
            }
            
            response = supabase.table('bids').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted bid with minimal data, ID: {bid_id}")
            return bid_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting bid with minimal data: {str(minimal_error)}")
            return None

def insert_bid_item(supabase, bid_id):
    """Insert a test bid item."""
    print("\nInserting test bid item...")
    
    if not bid_id:
        print("[ERROR] Cannot insert bid item without a valid bid ID.")
        return None
    
    item_id = str(uuid.uuid4())
    
    try:
        # Based on the error message, we need to include amount and quantity
        data = {
            'id': item_id,
            'bid_id': bid_id,
            'description': 'Demolition services',
            'quantity': 1,
            'unit_price': 30000.00,
            'amount': 30000.00,  # Required field
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('bid_items').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted bid item with ID: {item_id}")
        return item_id
    except Exception as e:
        print(f"[ERROR] Error inserting bid item: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': item_id,
                'bid_id': bid_id,
                'description': 'Demolition services',
                'quantity': 1,
                'amount': 30000.00  # Required field
            }
            
            response = supabase.table('bid_items').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted bid item with minimal data, ID: {item_id}")
            return item_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting bid item with minimal data: {str(minimal_error)}")
            return None

def insert_expense(supabase, project_id, user_id):
    """Insert a test expense."""
    print("\nInserting test expense...")
    
    if not project_id:
        print("[ERROR] Cannot insert expense without a valid project ID.")
        return None
    
    expense_id = str(uuid.uuid4())
    
    try:
        data = {
            'id': expense_id,
            'project_id': project_id,
            'user_id': user_id,
            'amount': 15000.00,
            'description': 'Lumber for framing',
            'category': 'materials',
            'date': datetime.now(timezone.utc).isoformat(),
            'receipt_path': '/receipts/r1.pdf',
            'billable': True,
            'reimbursable': False,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('expenses').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted expense with ID: {expense_id}")
        return expense_id
    except Exception as e:
        print(f"[ERROR] Error inserting expense: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': expense_id,
                'project_id': project_id,
                'amount': 15000.00,
                'description': 'Lumber for framing',
                'category': 'materials',
                'date': datetime.now(timezone.utc).isoformat()
            }
            
            response = supabase.table('expenses').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted expense with minimal data, ID: {expense_id}")
            return expense_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting expense with minimal data: {str(minimal_error)}")
            return None

def insert_time_entry(supabase, project_id, user_id, task_id=None):
    """Insert a test time entry."""
    print("\nInserting test time entry...")
    
    if not project_id or not user_id:
        print("[ERROR] Cannot insert time entry without valid project and user IDs.")
        return None
    
    time_entry_id = str(uuid.uuid4())
    
    try:
        data = {
            'id': time_entry_id,
            'user_id': user_id,
            'project_id': project_id,
            'task_id': task_id,
            'date': datetime.now(timezone.utc).isoformat(),
            'hours': 8.5,
            'description': 'Supervising demolition work',
            'billable': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Remove task_id if it's None
        if task_id is None:
            data.pop('task_id', None)
        
        response = supabase.table('time_entries').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted time entry with ID: {time_entry_id}")
        return time_entry_id
    except Exception as e:
        print(f"[ERROR] Error inserting time entry: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': time_entry_id,
                'user_id': user_id,
                'project_id': project_id,
                'date': datetime.now(timezone.utc).isoformat(),
                'hours': 8.5
            }
            
            response = supabase.table('time_entries').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted time entry with minimal data, ID: {time_entry_id}")
            return time_entry_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting time entry with minimal data: {str(minimal_error)}")
            return None

def insert_document(supabase, project_id, user_id):
    """Insert a test document."""
    print("\nInserting test document...")
    
    if not project_id:
        print("[ERROR] Cannot insert document without a valid project ID.")
        return None
    
    document_id = str(uuid.uuid4())
    
    try:
        # Based on the error message, storage_path is required
        data = {
            'id': document_id,
            'project_id': project_id,
            'name': 'Acme HQ Plans.pdf',
            'storage_path': '/documents/acme_hq_plans.pdf',  # Required field
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('documents').insert(data).execute()
        print(f"[SUCCESS] Successfully inserted document with ID: {document_id}")
        return document_id
    except Exception as e:
        print(f"[ERROR] Error inserting document: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': document_id,
                'project_id': project_id,
                'name': 'Acme HQ Plans.pdf',
                'storage_path': '/documents/acme_hq_plans.pdf'  # Required field
            }
            
            response = supabase.table('documents').insert(minimal_data).execute()
            print(f"[SUCCESS] Successfully inserted document with minimal data, ID: {document_id}")
            return document_id
        except Exception as minimal_error:
            print(f"[ERROR] Error inserting document with minimal data: {str(minimal_error)}")
            return None

def main():
    try:
        supabase_url, supabase_key = check_environment()
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase client created successfully.")
        
        # Insert test data
        user_id = insert_user_profile(supabase)
        client_id = insert_client(supabase)
        project_id = insert_project(supabase, client_id)
        
        # Update project with created_by_id
        if project_id and user_id:
            try:
                supabase.table('projects').update({'created_by_id': user_id}).eq('id', project_id).execute()
                print(f"[SUCCESS] Updated project with created_by_id: {user_id}")
            except Exception as e:
                print(f"[ERROR] Error updating project with created_by_id: {str(e)}")
        
        project_task_id = insert_project_task(supabase, project_id, user_id)
        task_id = insert_task(supabase, project_id, user_id)
        invoice_id = insert_invoice(supabase, client_id, project_id)
        item_id = insert_invoice_item(supabase, invoice_id)
        payment_id = insert_payment(supabase, invoice_id)
        notification_id = insert_user_notification(supabase, user_id)
        bid_id = insert_bid(supabase, client_id, project_id)
        bid_item_id = insert_bid_item(supabase, bid_id)
        expense_id = insert_expense(supabase, project_id, user_id)
        time_entry_id = insert_time_entry(supabase, project_id, user_id, task_id)
        document_id = insert_document(supabase, project_id, None)  # Removed user_id parameter
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Data Insertion Summary")
        print("=" * 60)
        print(f"User Profile: {'[SUCCESS]' if user_id else '[ERROR]'}")
        print(f"Client: {'[SUCCESS]' if client_id else '[ERROR]'}")
        print(f"Project: {'[SUCCESS]' if project_id else '[ERROR]'}")
        print(f"Project Task: {'[SUCCESS]' if project_task_id else '[ERROR]'}")
        print(f"Task: {'[SUCCESS]' if task_id else '[ERROR]'}")
        print(f"Invoice: {'[SUCCESS]' if invoice_id else '[ERROR]'}")
        print(f"Invoice Item: {'[SUCCESS]' if item_id else '[ERROR]'}")
        print(f"Payment: {'[SUCCESS]' if payment_id else '[ERROR]'}")
        print(f"User Notification: {'[SUCCESS]' if notification_id else '[ERROR]'}")
        print(f"Bid: {'[SUCCESS]' if bid_id else '[ERROR]'}")
        print(f"Bid Item: {'[SUCCESS]' if bid_item_id else '[ERROR]'}")
        print(f"Expense: {'[SUCCESS]' if expense_id else '[ERROR]'}")
        print(f"Time Entry: {'[SUCCESS]' if time_entry_id else '[ERROR]'}")
        print(f"Document: {'[SUCCESS]' if document_id else '[ERROR]'}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 