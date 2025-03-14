#!/usr/bin/env python3
"""
Test Database Connection and Functions

This script tests the connection to the Supabase PostgreSQL database and verifies
that the required functions can be used.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import json
from datetime import datetime

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

def test_connection_and_functions(supabase_url, db_password):
    """Test the database connection and functions."""
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
        
        # Test basic query
        print("\nTesting basic query...")
        cursor.execute("SELECT current_timestamp;")
        result = cursor.fetchone()
        print(f"Current timestamp: {result[0]}")
        
        # Test exec_sql function
        print("\nTesting exec_sql function...")
        try:
            # Use the correct syntax for calling the exec_sql function with SETOF record return type
            cursor.execute("SELECT * FROM public.exec_sql('SELECT ''test'' as test_column', NULL) as t(test_column text);")
            result = cursor.fetchone()
            print(f"exec_sql result: {result[0]}")
            print("✅ exec_sql function works!")
        except Exception as e:
            print(f"❌ Error using exec_sql function: {str(e)}")
        
        # Test update_updated_at_column function by creating a test table with a trigger
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
            print(f"Inserted row: id={insert_result[0]}, name={insert_result[1]}, created_at={insert_result[2]}, updated_at={insert_result[3]}")
            
            # Wait a moment to ensure timestamps will be different
            import time
            time.sleep(1)
            
            # Update the row
            cursor.execute("UPDATE test_updated_at SET name = 'updated test' WHERE id = %s RETURNING id, name, created_at, updated_at;", (insert_result[0],))
            update_result = cursor.fetchone()
            print(f"Updated row: id={update_result[0]}, name={update_result[1]}, created_at={update_result[2]}, updated_at={update_result[3]}")
            
            # Check if updated_at was changed
            if update_result[3] > insert_result[3]:
                print("✅ update_updated_at_column function works! The updated_at timestamp was updated.")
            else:
                print("❌ update_updated_at_column function does not work. The updated_at timestamp was not updated.")
            
            # Drop the temporary table (it will be dropped automatically at the end of the session, but let's be explicit)
            cursor.execute("DROP TABLE test_updated_at;")
        except Exception as e:
            print(f"❌ Error testing update_updated_at_column function: {str(e)}")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Database connection test completed!")
        return True
    except Exception as e:
        print(f"❌ Error testing database connection: {str(e)}")
        return False

def main():
    """Main function."""
    # Check environment variables
    supabase_url, supabase_key, db_password = check_environment()
    
    # Test the database connection and functions
    success = test_connection_and_functions(supabase_url, db_password)
    
    if success:
        print("\nNext steps:")
        print("1. Run 'python check_tables.py' to verify that all required tables exist")
        print("2. If any tables are missing, run 'python create_missing_tables.py' to create them")
        print("3. Run 'python test_supabase_api.py' to test the Supabase API")
        sys.exit(0)
    else:
        print("\nFailed to test database connection. Please check the error message above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 