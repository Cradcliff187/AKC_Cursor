"""
Insert Test Client

This script attempts to insert a test client into the database.
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

def insert_client(supabase):
    """Insert a test client."""
    print("\nInserting test client...")
    
    client_id = str(uuid.uuid4())
    
    # Try with different field combinations
    field_combinations = [
        # Try without status field
        {
            'id': client_id,
            'name': 'Acme Corporation',
            'contact_name': 'Wile E. Coyote',
            'email': 'wile@acme.com',
            'phone': '555-111-2222',
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'zip': '85001',
            'notes': 'Large commercial client',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        # Try with postal_code instead of zip
        {
            'id': client_id,
            'name': 'Acme Corporation',
            'contact_name': 'Wile E. Coyote',
            'email': 'wile@acme.com',
            'phone': '555-111-2222',
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'postal_code': '85001',
            'notes': 'Large commercial client',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        # Try with zipcode instead of zip
        {
            'id': client_id,
            'name': 'Acme Corporation',
            'contact_name': 'Wile E. Coyote',
            'email': 'wile@acme.com',
            'phone': '555-111-2222',
            'address': '123 Main St',
            'city': 'Phoenix',
            'state': 'AZ',
            'zipcode': '85001',
            'notes': 'Large commercial client',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        },
        # Try without any zip/postal code
        {
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
        },
        # Try with minimal fields
        {
            'id': client_id,
            'name': 'Acme Corporation',
            'email': 'wile@acme.com'
        }
    ]
    
    for i, data in enumerate(field_combinations):
        try:
            print(f"\nAttempt {i+1}: Trying with fields: {', '.join(data.keys())}")
            response = supabase.table('clients').insert(data).execute()
            print(f"✅ Successfully inserted client with ID: {client_id}")
            print(f"Fields used: {', '.join(data.keys())}")
            return client_id, data.keys()
        except Exception as e:
            print(f"❌ Error inserting client: {str(e)}")
    
    print("❌ All attempts to insert client failed.")
    return None, None

def main():
    try:
        supabase_url, supabase_key = check_environment()
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase client created successfully.")
        
        # Insert test client
        client_id, fields = insert_client(supabase)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Client Insertion Summary")
        print("=" * 60)
        print(f"Client: {'✅ Success' if client_id else '❌ Failed'}")
        if client_id:
            print(f"Client ID: {client_id}")
            print(f"Fields used: {', '.join(fields)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 