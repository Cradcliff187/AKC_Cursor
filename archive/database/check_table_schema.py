"""
Check Table Schema

This script checks the actual schema of each table in the Supabase database.
"""

import os
import sys
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

def get_table_schema(supabase, table_name):
    """Get the schema of a table."""
    try:
        # First try to get a single row to see the structure
        response = supabase.table(table_name).select('*').limit(1).execute()
        
        if response.data:
            print(f"\n✅ Table '{table_name}' schema (from sample row):")
            for key in response.data[0].keys():
                print(f"  - {key}")
            return True
        else:
            # If no data, try to get the column information using PostgreSQL's information_schema
            print(f"\n⚠️ Table '{table_name}' exists but has no data. Trying to get schema from information_schema...")
            
            # Using the RPC function to execute SQL if it exists
            try:
                sql = f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                """
                
                response = supabase.rpc('exec_sql', {'sql': sql}).execute()
                
                if response.data:
                    print(f"✅ Table '{table_name}' schema (from information_schema):")
                    for column in response.data:
                        nullable = "NULL" if column['is_nullable'] == 'YES' else "NOT NULL"
                        print(f"  - {column['column_name']} ({column['data_type']}, {nullable})")
                    return True
                else:
                    print(f"⚠️ No schema information found for table '{table_name}'")
                    return False
                    
            except Exception as e:
                print(f"❌ Error getting schema from information_schema: {str(e)}")
                
                # Fallback: Try to get the column names by selecting a specific column that should exist
                try:
                    # Try with 'id' which is common in most tables
                    response = supabase.table(table_name).select('id').limit(1).execute()
                    print(f"✅ Table '{table_name}' exists (confirmed by selecting 'id' column)")
                    return True
                except Exception as e2:
                    print(f"❌ Error confirming table existence: {str(e2)}")
                    return False
    except Exception as e:
        print(f"❌ Error checking table '{table_name}': {str(e)}")
        return False

def main():
    try:
        supabase_url, supabase_key = check_environment()
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase client created successfully.")
        
        # List of tables to check
        tables = [
            'user_profiles',
            'user_notifications',
            'clients',
            'projects',
            'project_tasks',
            'tasks',  # Check if this table exists (referenced by time_entries)
            'invoices',
            'invoice_items',
            'payments',
            'bids',
            'bid_items',
            'expenses',
            'time_entries',
            'documents'
        ]
        
        # Check each table
        for table in tables:
            get_table_schema(supabase, table)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 