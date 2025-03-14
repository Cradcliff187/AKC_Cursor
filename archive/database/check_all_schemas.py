"""
Check All Schemas

This script checks the schema of all tables in the Supabase database.
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

def get_all_tables(supabase):
    """Get a list of all tables in the public schema."""
    try:
        # Try to use exec_sql function if it exists
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        response = supabase.rpc('exec_sql', {'query': query}).execute()
        tables = [table['table_name'] for table in response.data]
        return tables
    except Exception as e:
        print(f"Could not use exec_sql function: {str(e)}")
        print("Falling back to hardcoded table list...")
        
        # Hardcoded list of tables we expect to exist
        return [
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

def check_table_schema(supabase, table_name):
    """Check the schema of a specified table."""
    try:
        # Try to use exec_sql function if it exists
        query = f"""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = '{table_name}'
        ORDER BY ordinal_position;
        """
        response = supabase.rpc('exec_sql', {'query': query}).execute()
        columns = response.data
        
        if not columns:
            print(f"No columns found for table '{table_name}'.")
            return None
        
        return columns
    except Exception as e:
        print(f"Could not use exec_sql function: {str(e)}")
        print("Trying to get schema information from a sample record...")
        
        try:
            # Try to get a sample record to infer schema
            response = supabase.table(table_name).select('*').limit(1).execute()
            
            if response.data:
                # Create a list of column dictionaries with just the name
                columns = [{'column_name': key, 'data_type': 'unknown', 'is_nullable': 'unknown'} 
                          for key in response.data[0].keys()]
                return columns
            else:
                print(f"No data found in table '{table_name}'.")
                return None
        except Exception as sample_error:
            print(f"Error getting sample data: {str(sample_error)}")
            return None

def main():
    try:
        supabase_url, supabase_key = check_environment()
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase client created successfully.")
        
        # Get all tables
        tables = get_all_tables(supabase)
        print(f"Found {len(tables)} tables in the database.")
        
        # Check schema for each table
        for table_name in tables:
            print(f"\n{'=' * 60}")
            print(f"Schema for table '{table_name}':")
            print(f"{'=' * 60}")
            
            columns = check_table_schema(supabase, table_name)
            
            if columns:
                print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10}")
                print(f"{'-' * 60}")
                
                for column in columns:
                    column_name = column.get('column_name', 'unknown')
                    data_type = column.get('data_type', 'unknown')
                    is_nullable = column.get('is_nullable', 'unknown')
                    
                    print(f"{column_name:<30} {data_type:<20} {is_nullable:<10}")
                
                print(f"{'-' * 60}")
                print(f"Total columns: {len(columns)}")
            else:
                print(f"Could not retrieve schema for table '{table_name}'.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 