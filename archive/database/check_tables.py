"""
Check Tables

This script checks which tables exist in the Supabase database.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def check_environment():
    """Check if the required environment variables are set."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables.")
        print("Please create a .env file in the root directory with these variables.")
        sys.exit(1)
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase service key length: {len(supabase_key)}")
    
    return supabase_url, supabase_key

def check_tables(client: Client):
    """Check which tables exist in the database."""
    tables = [
        "user_profiles",
        "user_notifications",
        "clients",
        "projects",
        "project_tasks",
        "invoices",
        "invoice_items",
        "payments",
        "bids",
        "bid_items",
        "expenses",
        "time_entries",
        "documents"
    ]
    
    existing_tables = []
    missing_tables = []
    
    print("Checking tables...")
    for table in tables:
        try:
            # Try to select one row from the table
            response = client.table(table).select('*').limit(1).execute()
            print(f"✅ Table '{table}': exists")
            existing_tables.append(table)
        except Exception as e:
            print(f"❌ Table '{table}': does not exist (error code: {getattr(e, 'code', 'unknown')})")
            missing_tables.append(table)
    
    print("\nSummary:")
    print(f"- {len(existing_tables)} of {len(tables)} tables exist")
    print(f"- {len(missing_tables)} tables are missing: {', '.join(missing_tables) if missing_tables else 'None'}")
    
    if missing_tables:
        print("\nTo create the missing tables, follow the instructions in supabase_setup_instructions.md")
    
    return existing_tables, missing_tables

def check_functions(client: Client):
    """Check if required functions exist in the database."""
    print("\nChecking functions...")
    
    # Check for exec_sql function
    try:
        response = client.rpc('exec_sql', {'query': 'SELECT 1 as test'}).execute()
        print("✅ Function 'exec_sql': exists")
        exec_sql_exists = True
    except Exception as e:
        print(f"❌ Function 'exec_sql': does not exist (error code: {getattr(e, 'code', 'unknown')})")
        exec_sql_exists = False
    
    # Check for update_updated_at_column function by checking if a trigger using it exists
    try:
        # Query to check if the function is referenced by any trigger
        query = """
        SELECT 1 FROM pg_trigger t
        JOIN pg_proc p ON t.tgfoid = p.oid
        WHERE p.proname = 'update_updated_at_column'
        LIMIT 1
        """
        response = client.rpc('exec_sql', {'query': query}).execute()
        
        if response.data and len(response.data) > 0:
            print("✅ Function 'update_updated_at_column': exists")
            update_fn_exists = True
        else:
            print("❌ Function 'update_updated_at_column': does not exist or not used by any trigger")
            update_fn_exists = False
    except Exception as e:
        # If exec_sql doesn't exist, we can't check for update_updated_at_column this way
        if not exec_sql_exists:
            print("⚠️ Cannot check for 'update_updated_at_column' function without 'exec_sql'")
        else:
            print(f"❌ Error checking for 'update_updated_at_column' function: {str(e)}")
        update_fn_exists = False
    
    return exec_sql_exists, update_fn_exists

def main():
    try:
        supabase_url, supabase_key = check_environment()
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase client created successfully.")
        
        # Check tables
        existing_tables, missing_tables = check_tables(supabase)
        
        # Check functions
        exec_sql_exists, update_fn_exists = check_functions(supabase)
        
        # Print overall summary
        print("\nOverall Status:")
        if not missing_tables and exec_sql_exists and update_fn_exists:
            print("✅ All required tables and functions exist!")
        else:
            print("⚠️ Some required components are missing:")
            if missing_tables:
                print(f"  - Missing tables: {', '.join(missing_tables)}")
            if not exec_sql_exists:
                print("  - Missing 'exec_sql' function")
            if not update_fn_exists:
                print("  - Missing 'update_updated_at_column' function")
            
            print("\nPlease follow the instructions in supabase_setup_instructions.md to create the missing components.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 