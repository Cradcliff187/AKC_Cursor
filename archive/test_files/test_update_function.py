#!/usr/bin/env python3
"""
Test update_updated_at_column Function

This script tests the update_updated_at_column function in Supabase by creating a test table
and trigger, then checking if the function updates the updated_at column correctly.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

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

def test_update_function(supabase_url, db_password):
    """Test the update_updated_at_column function."""
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
        
        # Set isolation level to autocommit
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Create a test table with a unique name to avoid conflicts
        test_table_name = f"test_updated_at_{int(time.time())}"
        print(f"Creating test table: {test_table_name}...")
        
        cursor.execute(f"""
        CREATE TABLE public.{test_table_name} (
            id SERIAL PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """)
        
        # Create a trigger using the update_updated_at_column function
        print("Creating trigger...")
        cursor.execute(f"""
        CREATE TRIGGER update_{test_table_name}_updated_at
        BEFORE UPDATE ON public.{test_table_name}
        FOR EACH ROW
        EXECUTE FUNCTION public.update_updated_at_column();
        """)
        
        # Insert a row
        print("Inserting test row...")
        cursor.execute(f"INSERT INTO public.{test_table_name} (name) VALUES ('test') RETURNING id, name, created_at, updated_at;")
        insert_result = cursor.fetchone()
        print(f"Inserted row: id={insert_result[0]}, name={insert_result[1]}, created_at={insert_result[2]}, updated_at={insert_result[3]}")
        
        # Wait a moment to ensure timestamps will be different
        print("Waiting for 2 seconds...")
        time.sleep(2)
        
        # Update the row
        print("Updating test row...")
        cursor.execute(f"UPDATE public.{test_table_name} SET name = 'updated test' WHERE id = %s RETURNING id, name, created_at, updated_at;", (insert_result[0],))
        update_result = cursor.fetchone()
        print(f"Updated row: id={update_result[0]}, name={update_result[1]}, created_at={update_result[2]}, updated_at={update_result[3]}")
        
        # Check if updated_at was changed
        if update_result[3] > insert_result[3]:
            print("✅ update_updated_at_column function works! The updated_at timestamp was updated.")
            success = True
        else:
            print("❌ update_updated_at_column function does not work. The updated_at timestamp was not updated.")
            success = False
        
        # Drop the test table
        print(f"Dropping test table: {test_table_name}...")
        cursor.execute(f"DROP TABLE public.{test_table_name};")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        return success
    except Exception as e:
        print(f"❌ Error testing update_updated_at_column function: {str(e)}")
        return False

def main():
    """Main function."""
    # Check environment variables
    supabase_url, supabase_key, db_password = check_environment()
    
    # Test the update_updated_at_column function
    success = test_update_function(supabase_url, db_password)
    
    if success:
        print("\n✅ update_updated_at_column function test completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python check_tables.py' to verify that all required tables exist")
        print("2. If any tables are missing, run 'python create_missing_tables.py' to create them")
        sys.exit(0)
    else:
        print("\n❌ update_updated_at_column function test failed.")
        print("\nNext steps:")
        print("1. Check the error message above and fix the issue")
        print("2. Run this script again to verify that the function works correctly")
        sys.exit(1)

if __name__ == "__main__":
    main() 