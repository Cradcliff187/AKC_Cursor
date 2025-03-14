#!/usr/bin/env python3
"""
Fix update_updated_at_column Function

This script fixes the update_updated_at_column function in Supabase.
"""

import os
import sys
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

def fix_update_updated_at_function(supabase_url, db_password):
    """Fix the update_updated_at_column function."""
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
        
        # Drop the existing function
        print("Dropping existing update_updated_at_column function...")
        drop_sql = "DROP FUNCTION IF EXISTS public.update_updated_at_column();"
        cursor.execute(drop_sql)
        
        # SQL for creating the update_updated_at_column function
        sql = """
        CREATE OR REPLACE FUNCTION public.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        print("Creating new update_updated_at_column function...")
        
        # Execute the SQL
        cursor.execute(sql)
        
        # Test the fixed function
        print("Testing fixed update_updated_at_column function...")
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
            print(f"❌ Error testing fixed update_updated_at_column function: {str(e)}")
            return False
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("✅ Function fixed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error fixing function: {str(e)}")
        return False

def main():
    """Main function."""
    # Check environment variables
    supabase_url, supabase_key, db_password = check_environment()
    
    # Fix the update_updated_at_column function
    success = fix_update_updated_at_function(supabase_url, db_password)
    
    if success:
        print("\nNext steps:")
        print("1. Run 'python test_db_connection.py' to verify that the functions work correctly")
        print("2. Run 'python check_tables.py' to verify that all required tables exist")
        sys.exit(0)
    else:
        print("\nFailed to fix function. Please check the error message above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 