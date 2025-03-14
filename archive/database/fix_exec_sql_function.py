#!/usr/bin/env python3
"""
Fix exec_sql Function

This script fixes the exec_sql function in Supabase to handle different return types.
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

def fix_exec_sql_function(supabase_url, db_password):
    """Fix the exec_sql function to handle different return types."""
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
        print("Dropping existing exec_sql function...")
        drop_sql = "DROP FUNCTION IF EXISTS public.exec_sql(text, jsonb);"
        cursor.execute(drop_sql)
        
        # SQL for creating the exec_sql function with a different return type
        sql = """
        CREATE OR REPLACE FUNCTION public.exec_sql(query text, params jsonb DEFAULT NULL)
        RETURNS SETOF record AS $$
        BEGIN
            IF params IS NULL THEN
                RETURN QUERY EXECUTE query;
            ELSE
                RETURN QUERY EXECUTE query USING params;
            END IF;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        print("Creating new exec_sql function...")
        
        # Execute the SQL
        cursor.execute(sql)
        
        # Test the fixed function
        print("Testing fixed exec_sql function...")
        try:
            cursor.execute("SELECT * FROM public.exec_sql('SELECT current_timestamp as time', NULL) as t(time timestamp with time zone);")
            result = cursor.fetchone()
            print(f"exec_sql test result: {result[0]}")
            print("✅ exec_sql function fixed and tested successfully!")
        except Exception as e:
            print(f"❌ Error testing fixed exec_sql function: {str(e)}")
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
    
    # Fix the exec_sql function
    success = fix_exec_sql_function(supabase_url, db_password)
    
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