"""
Insert Test Project

This script attempts to insert a test project into the database.
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

def get_client_id(supabase):
    """Get an existing client ID or create a new client."""
    try:
        # Try to get an existing client
        response = supabase.table('clients').select('id').limit(1).execute()
        
        if response.data:
            client_id = response.data[0]['id']
            print(f"Using existing client with ID: {client_id}")
            return client_id
        
        # If no clients exist, create a new one
        print("No existing clients found. Creating a new client...")
        client_id = str(uuid.uuid4())
        
        data = {
            'id': client_id,
            'name': 'Acme Corporation',
            'contact_name': 'Wile E. Coyote',
            'email': 'wile@acme.com',
            'phone': '555-111-2222',
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'notes': 'Large commercial client',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('clients').insert(data).execute()
        print(f"Created new client with ID: {client_id}")
        return client_id
    except Exception as e:
        print(f"Error getting/creating client: {str(e)}")
        return None

def insert_project(supabase, client_id):
    """Insert a test project."""
    print("\nInserting test project...")
    
    if not client_id:
        print("❌ Cannot insert project without a valid client ID.")
        return None, None
    
    project_id = str(uuid.uuid4())
    
    # Try with different status values
    status_values = [
        'in_progress',
        'active',
        'pending',
        'completed',
        'on_hold',
        'cancelled',
        'planning'
    ]
    
    for status in status_values:
        try:
            # Try with minimal fields and different status values
            data = {
                'id': project_id,
                'client_id': client_id,
                'name': 'Acme HQ Renovation',
                'description': 'Complete renovation of Acme headquarters',
                'status': status
            }
            
            print(f"\nTrying with status: '{status}'")
            response = supabase.table('projects').insert(data).execute()
            print(f"✅ Successfully inserted project with ID: {project_id}")
            print(f"Status value used: {status}")
            return project_id, status
        except Exception as e:
            print(f"❌ Error inserting project with status '{status}': {str(e)}")
    
    # If all status values fail, try without specifying status
    try:
        data = {
            'id': project_id,
            'client_id': client_id,
            'name': 'Acme HQ Renovation',
            'description': 'Complete renovation of Acme headquarters'
        }
        
        print("\nTrying without status field")
        response = supabase.table('projects').insert(data).execute()
        print(f"✅ Successfully inserted project with ID: {project_id}")
        print("No status value specified")
        return project_id, None
    except Exception as e:
        print(f"❌ Error inserting project without status: {str(e)}")
    
    print("❌ All attempts to insert project failed.")
    return None, None

def main():
    try:
        supabase_url, supabase_key = check_environment()
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase client created successfully.")
        
        # Get a client ID
        client_id = get_client_id(supabase)
        
        # Insert test project
        project_id, status = insert_project(supabase, client_id)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Project Insertion Summary")
        print("=" * 60)
        print(f"Project: {'✅ Success' if project_id else '❌ Failed'}")
        if project_id:
            print(f"Project ID: {project_id}")
            print(f"Status value: {status if status else 'Not specified'}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 