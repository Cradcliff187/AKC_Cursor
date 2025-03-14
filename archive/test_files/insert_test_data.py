"""
Insert Test Data

This script attempts to insert test data into each table in the Supabase database.
It uses a cautious approach, inserting one record at a time and handling errors.
"""

import os
import sys
import uuid
from datetime import datetime, timezone
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
        # Try with all possible fields
        data = {
            'id': user_id,
            'auth_id': f'auth_{user_id}',
            'email': f'test_{user_id[:8]}@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'display_name': 'Test User',
            'role': 'admin',
            'status': 'active',
            'phone': '555-123-4567',
            'avatar_url': 'https://randomuser.me/api/portraits/men/1.jpg',
            'title': 'Project Manager',
            'department': 'Management',
            'hire_date': datetime.now(timezone.utc).isoformat(),
            'last_login': datetime.now(timezone.utc).isoformat(),
            'preferences': {},
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('user_profiles').insert(data).execute()
        print(f"✅ Successfully inserted user profile with ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"❌ Error inserting user profile: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': user_id,
                'auth_id': f'auth_{user_id}',
                'email': f'test_{user_id[:8]}@example.com',
                'role': 'admin',
                'status': 'active'
            }
            
            response = supabase.table('user_profiles').insert(minimal_data).execute()
            print(f"✅ Successfully inserted user profile with minimal data, ID: {user_id}")
            return user_id
        except Exception as minimal_error:
            print(f"❌ Error inserting user profile with minimal data: {str(minimal_error)}")
            return None

def insert_client(supabase):
    """Insert a test client."""
    print("\nInserting test client...")
    
    client_id = str(uuid.uuid4())
    
    try:
        # Try with all possible fields
        data = {
            'id': client_id,
            'name': 'Acme Corporation',
            'contact_name': 'Wile E. Coyote',
            'email': 'wile@acme.com',
            'phone': '555-111-2222',
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'zip': '85001',  # Try with 'zip' first
            'status': 'active',
            'notes': 'Large commercial client',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('clients').insert(data).execute()
        print(f"✅ Successfully inserted client with ID: {client_id}")
        return client_id
    except Exception as e:
        print(f"❌ Error inserting client: {str(e)}")
        
        # If 'zip' field fails, try with 'postal_code'
        if "'zip'" in str(e):
            try:
                data['postal_code'] = data.pop('zip')
                response = supabase.table('clients').insert(data).execute()
                print(f"✅ Successfully inserted client with 'postal_code' instead of 'zip', ID: {client_id}")
                return client_id
            except Exception as postal_error:
                print(f"❌ Error inserting client with 'postal_code': {str(postal_error)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': client_id,
                'name': 'Acme Corporation',
                'email': 'wile@acme.com',
                'status': 'active'
            }
            
            response = supabase.table('clients').insert(minimal_data).execute()
            print(f"✅ Successfully inserted client with minimal data, ID: {client_id}")
            return client_id
        except Exception as minimal_error:
            print(f"❌ Error inserting client with minimal data: {str(minimal_error)}")
            return None

def insert_project(supabase, client_id):
    """Insert a test project."""
    print("\nInserting test project...")
    
    if not client_id:
        print("❌ Cannot insert project without a valid client ID.")
        return None
    
    project_id = str(uuid.uuid4())
    
    try:
        # Try with all possible fields
        data = {
            'id': project_id,
            'client_id': client_id,
            'name': 'Acme HQ Renovation',
            'description': 'Complete renovation of Acme headquarters',
            'status': 'in_progress',
            'start_date': '2023-01-15',
            'end_date': '2023-07-30',
            'budget': 1500000.00,
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'zip': '85001',  # Try with 'zip' first
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('projects').insert(data).execute()
        print(f"✅ Successfully inserted project with ID: {project_id}")
        return project_id
    except Exception as e:
        print(f"❌ Error inserting project: {str(e)}")
        
        # If 'zip' field fails, try with 'postal_code'
        if "'zip'" in str(e):
            try:
                data['postal_code'] = data.pop('zip')
                response = supabase.table('projects').insert(data).execute()
                print(f"✅ Successfully inserted project with 'postal_code' instead of 'zip', ID: {project_id}")
                return project_id
            except Exception as postal_error:
                print(f"❌ Error inserting project with 'postal_code': {str(postal_error)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': project_id,
                'client_id': client_id,
                'name': 'Acme HQ Renovation',
                'status': 'in_progress'
            }
            
            response = supabase.table('projects').insert(minimal_data).execute()
            print(f"✅ Successfully inserted project with minimal data, ID: {project_id}")
            return project_id
        except Exception as minimal_error:
            print(f"❌ Error inserting project with minimal data: {str(minimal_error)}")
            return None

def insert_project_task(supabase, project_id, user_id):
    """Insert a test project task."""
    print("\nInserting test project task...")
    
    if not project_id:
        print("❌ Cannot insert project task without a valid project ID.")
        return None
    
    task_id = str(uuid.uuid4())
    
    try:
        # Try with all possible fields
        data = {
            'id': task_id,
            'project_id': project_id,
            'name': 'Demolition',
            'description': 'Interior demolition of existing structures',
            'status': 'pending',
            'priority': 'high',
            'assigned_to': user_id,
            'start_date': '2023-01-15',
            'due_date': '2023-02-15',
            'completed_at': None,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('project_tasks').insert(data).execute()
        print(f"✅ Successfully inserted project task with ID: {task_id}")
        return task_id
    except Exception as e:
        print(f"❌ Error inserting project task: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': task_id,
                'project_id': project_id,
                'name': 'Demolition',
                'status': 'pending'
            }
            
            response = supabase.table('project_tasks').insert(minimal_data).execute()
            print(f"✅ Successfully inserted project task with minimal data, ID: {task_id}")
            return task_id
        except Exception as minimal_error:
            print(f"❌ Error inserting project task with minimal data: {str(minimal_error)}")
            return None

def insert_invoice(supabase, client_id, project_id):
    """Insert a test invoice."""
    print("\nInserting test invoice...")
    
    if not client_id or not project_id:
        print("❌ Cannot insert invoice without valid client and project IDs.")
        return None
    
    invoice_id = str(uuid.uuid4())
    
    try:
        # Try with all possible fields
        data = {
            'id': invoice_id,
            'client_id': client_id,
            'project_id': project_id,
            'invoice_number': 'INV-2023-001',
            'status': 'sent',
            'issue_date': '2023-02-01',
            'due_date': '2023-03-01',
            'amount': 50000.00,
            'tax_amount': 4000.00,
            'discount_amount': 0.00,
            'notes': 'First payment for Acme HQ Renovation',
            'terms': 'Net 30',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('invoices').insert(data).execute()
        print(f"✅ Successfully inserted invoice with ID: {invoice_id}")
        return invoice_id
    except Exception as e:
        print(f"❌ Error inserting invoice: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': invoice_id,
                'client_id': client_id,
                'project_id': project_id,
                'invoice_number': 'INV-2023-001',
                'status': 'sent'
            }
            
            response = supabase.table('invoices').insert(minimal_data).execute()
            print(f"✅ Successfully inserted invoice with minimal data, ID: {invoice_id}")
            return invoice_id
        except Exception as minimal_error:
            print(f"❌ Error inserting invoice with minimal data: {str(minimal_error)}")
            return None

def insert_invoice_item(supabase, invoice_id):
    """Insert a test invoice item."""
    print("\nInserting test invoice item...")
    
    if not invoice_id:
        print("❌ Cannot insert invoice item without a valid invoice ID.")
        return None
    
    item_id = str(uuid.uuid4())
    
    try:
        # Try with all possible fields
        data = {
            'id': item_id,
            'invoice_id': invoice_id,
            'description': 'Demolition services',
            'quantity': 1,
            'unit_price': 30000.00,
            'tax_rate': 8.00,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('invoice_items').insert(data).execute()
        print(f"✅ Successfully inserted invoice item with ID: {item_id}")
        return item_id
    except Exception as e:
        print(f"❌ Error inserting invoice item: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': item_id,
                'invoice_id': invoice_id,
                'description': 'Demolition services'
            }
            
            response = supabase.table('invoice_items').insert(minimal_data).execute()
            print(f"✅ Successfully inserted invoice item with minimal data, ID: {item_id}")
            return item_id
        except Exception as minimal_error:
            print(f"❌ Error inserting invoice item with minimal data: {str(minimal_error)}")
            return None

def insert_payment(supabase, invoice_id):
    """Insert a test payment."""
    print("\nInserting test payment...")
    
    if not invoice_id:
        print("❌ Cannot insert payment without a valid invoice ID.")
        return None
    
    payment_id = str(uuid.uuid4())
    
    try:
        # Try with all possible fields
        data = {
            'id': payment_id,
            'invoice_id': invoice_id,
            'amount': 54000.00,
            'payment_date': '2023-02-25',
            'payment_method': 'check',
            'reference_number': 'CHK12345',
            'notes': 'Payment received by mail',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('payments').insert(data).execute()
        print(f"✅ Successfully inserted payment with ID: {payment_id}")
        return payment_id
    except Exception as e:
        print(f"❌ Error inserting payment: {str(e)}")
        
        # Try with minimal fields
        try:
            minimal_data = {
                'id': payment_id,
                'invoice_id': invoice_id,
                'amount': 54000.00,
                'payment_date': '2023-02-25',
                'payment_method': 'check'
            }
            
            response = supabase.table('payments').insert(minimal_data).execute()
            print(f"✅ Successfully inserted payment with minimal data, ID: {payment_id}")
            return payment_id
        except Exception as minimal_error:
            print(f"❌ Error inserting payment with minimal data: {str(minimal_error)}")
            return None

def insert_user_notification(supabase, user_id):
    """Insert a test user notification."""
    print("\nInserting test user notification...")
    
    if not user_id:
        print("❌ Cannot insert user notification without a valid user ID.")
        return None
    
    notification_id = str(uuid.uuid4())
    
    try:
        # Try with all possible fields
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
        print(f"✅ Successfully inserted user notification with ID: {notification_id}")
        return notification_id
    except Exception as e:
        print(f"❌ Error inserting user notification: {str(e)}")
        
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
            print(f"✅ Successfully inserted user notification with minimal data, ID: {notification_id}")
            return notification_id
        except Exception as minimal_error:
            print(f"❌ Error inserting user notification with minimal data: {str(minimal_error)}")
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
        task_id = insert_project_task(supabase, project_id, user_id)
        invoice_id = insert_invoice(supabase, client_id, project_id)
        item_id = insert_invoice_item(supabase, invoice_id)
        payment_id = insert_payment(supabase, invoice_id)
        notification_id = insert_user_notification(supabase, user_id)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Data Insertion Summary")
        print("=" * 60)
        print(f"User Profile: {'✅ Success' if user_id else '❌ Failed'}")
        print(f"Client: {'✅ Success' if client_id else '❌ Failed'}")
        print(f"Project: {'✅ Success' if project_id else '❌ Failed'}")
        print(f"Project Task: {'✅ Success' if task_id else '❌ Failed'}")
        print(f"Invoice: {'✅ Success' if invoice_id else '❌ Failed'}")
        print(f"Invoice Item: {'✅ Success' if item_id else '❌ Failed'}")
        print(f"Payment: {'✅ Success' if payment_id else '❌ Failed'}")
        print(f"User Notification: {'✅ Success' if notification_id else '❌ Failed'}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 