#!/usr/bin/env python3
"""
Check Database Setup

This script checks the Supabase database setup, including tables and functions,
using direct PostgreSQL connection.
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

def check_environment():
    """Check if the required environment variables are set."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    
    if not supabase_url or not supabase_key or not db_password:
        print("Error: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and SUPABASE_DB_PASSWORD must be set in environment variables.")
        sys.exit(1)
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase service key length: {len(supabase_key)}")
    print(f"Database password is set: {'Yes' if db_password else 'No'}")
    
    return supabase_url, supabase_key, db_password

def check_database_setup(supabase_url, db_password):
    """Check the database setup, including tables and functions."""
    try:
        # Extract the project ID from the Supabase URL
        project_id = supabase_url.split('//')[1].split('.')[0]
        
        # Construct the database connection string
        db_host = f"db.{project_id}.supabase.co"
        db_port = 5432
        db_name = "postgres"
        db_user = "postgres"
        
        print(f"Connecting to PostgreSQL database at {db_host}...")
        
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
            sslmode='require'
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check tables
        required_tables = [
            'user_profiles',
            'user_notifications',
            'clients',
            'projects',
            'project_tasks',
            'invoices',
            'invoice_items',
            'payments',
            'bids',
            'bid_items',
            'expenses',
            'time_entries',
            'documents'
        ]
        
        print("\nChecking tables...")
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table}'
            );
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                print(f"✅ Table '{table}': exists")
                existing_tables.append(table)
            else:
                print(f"❌ Table '{table}': does not exist")
                missing_tables.append(table)
        
        print(f"\nSummary:")
        print(f"- {len(existing_tables)} of {len(required_tables)} tables exist")
        if missing_tables:
            print(f"- {len(missing_tables)} tables are missing: {', '.join(missing_tables)}")
        else:
            print(f"- 0 tables are missing: None")
        
        # Check functions
        required_functions = [
            'exec_sql',
            'update_updated_at_column'
        ]
        
        print("\nChecking functions...")
        existing_functions = []
        missing_functions = []
        
        for function in required_functions:
            cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_proc 
                WHERE proname = '{function}' 
                AND pg_function_is_visible(oid)
            );
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                print(f"✅ Function '{function}': exists")
                existing_functions.append(function)
            else:
                print(f"❌ Function '{function}': does not exist")
                missing_functions.append(function)
        
        print(f"\nSummary:")
        print(f"- {len(existing_functions)} of {len(required_functions)} functions exist")
        if missing_functions:
            print(f"- {len(missing_functions)} functions are missing: {', '.join(missing_functions)}")
        else:
            print(f"- 0 functions are missing: None")
        
        # Check if update_updated_at_column function works
        if 'update_updated_at_column' in existing_functions:
            print("\nTesting update_updated_at_column function...")
            try:
                # Create a temporary test table
                cursor.execute("""
                CREATE TEMPORARY TABLE test_updated_at (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """)
                
                # Create a trigger using the update_updated_at_column function
                cursor.execute("""
                CREATE TRIGGER update_test_updated_at
                BEFORE UPDATE ON test_updated_at
                FOR EACH ROW
                EXECUTE FUNCTION public.update_updated_at_column();
                """)
                
                # Insert a row
                cursor.execute("INSERT INTO test_updated_at (name) VALUES ('test') RETURNING id, name, created_at, updated_at;")
                insert_result = cursor.fetchone()
                
                # Wait a moment to ensure timestamps will be different
                import time
                time.sleep(1)
                
                # Update the row
                cursor.execute("UPDATE test_updated_at SET name = 'updated test' WHERE id = %s RETURNING id, name, created_at, updated_at;", (insert_result[0],))
                update_result = cursor.fetchone()
                
                # Check if updated_at was changed
                if update_result[3] > insert_result[3]:
                    print("✅ update_updated_at_column function works! The updated_at timestamp was updated.")
                else:
                    print("❌ update_updated_at_column function does not work. The updated_at timestamp was not updated.")
                
                # Drop the temporary table (it will be dropped automatically at the end of the session, but let's be explicit)
                cursor.execute("DROP TABLE test_updated_at;")
            except Exception as e:
                print(f"❌ Error testing update_updated_at_column function: {str(e)}")
        
        # Check if exec_sql function works
        if 'exec_sql' in existing_functions:
            print("\nTesting exec_sql function...")
            try:
                cursor.execute("SELECT * FROM public.exec_sql('SELECT ''test'' as test_column', NULL) as t(test_column text);")
                result = cursor.fetchone()
                print(f"✅ exec_sql function works! Result: {result[0]}")
            except Exception as e:
                print(f"❌ Error using exec_sql function: {str(e)}")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        # Save the results to a JSON file
        results = {
            "timestamp": str(datetime.now()),
            "tables": {
                "required": required_tables,
                "existing": existing_tables,
                "missing": missing_tables
            },
            "functions": {
                "required": required_functions,
                "existing": existing_functions,
                "missing": missing_functions
            },
            "all_components_exist": len(missing_tables) == 0 and len(missing_functions) == 0
        }
        
        with open("db_setup_check_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to db_setup_check_results.json")
        
        # Print overall status
        print("\nOverall Status:")
        if len(missing_tables) == 0 and len(missing_functions) == 0:
            print("✅ All required components exist!")
        else:
            print("⚠️ Some required components are missing:")
            if missing_tables:
                print(f"  - Missing tables: {', '.join(missing_tables)}")
            if missing_functions:
                print(f"  - Missing functions: {', '.join(missing_functions)}")
        
        return len(missing_tables) == 0 and len(missing_functions) == 0
    except Exception as e:
        print(f"❌ Error checking database setup: {str(e)}")
        return False

def main():
    """Main function."""
    # Check environment variables
    supabase_url, supabase_key, db_password = check_environment()
    
    # Check database setup
    success = check_database_setup(supabase_url, db_password)
    
    if success:
        print("\nNext steps:")
        print("1. Run 'python test_supabase_api.py' to test the Supabase API")
        print("2. Run 'python run_with_supabase.py' to run the application with Supabase integration")
        sys.exit(0)
    else:
        print("\nNext steps:")
        print("1. Fix the missing components")
        print("2. Run this script again to verify that all components exist")
        sys.exit(1)

if __name__ == "__main__":
    main() 