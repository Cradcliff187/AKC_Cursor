#!/usr/bin/env python3
"""
Create exec_sql Function Directly

This script creates the exec_sql function in Supabase by connecting directly to the PostgreSQL database.
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

def create_exec_sql_function(supabase_url, db_password):
    """Create the exec_sql function by connecting directly to the PostgreSQL database."""
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
        
        # SQL for creating the exec_sql function
        sql = """
        CREATE OR REPLACE FUNCTION public.exec_sql(query text, params jsonb DEFAULT NULL)
        RETURNS SETOF json AS $$
        BEGIN
            IF params IS NULL THEN
                RETURN QUERY EXECUTE query;
            ELSE
                RETURN QUERY EXECUTE query USING params;
            END IF;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        print("Creating exec_sql function...")
        
        # Execute the SQL
        cursor.execute(sql)
        
        # Create the update_updated_at_column function
        update_at_sql = """
        CREATE OR REPLACE FUNCTION public.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        print("Creating update_updated_at_column function...")
        
        # Execute the SQL
        cursor.execute(update_at_sql)
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("✅ Functions created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating functions: {str(e)}")
        return False

def main():
    """Main function."""
    # Check environment variables
    supabase_url, supabase_key, db_password = check_environment()
    
    # Create the exec_sql function
    success = create_exec_sql_function(supabase_url, db_password)
    
    if success:
        print("\nNext steps:")
        print("1. Run 'python check_tables.py' to verify that the functions were created successfully")
        print("2. If any tables are missing, run 'python create_missing_tables.sql' to create them")
        print("3. Run 'python test_db_connection.py' to test the database connection")
        sys.exit(0)
    else:
        print("\nFailed to create functions. Please check the error message above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 