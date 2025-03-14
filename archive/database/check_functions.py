#!/usr/bin/env python3
"""
Check if required functions exist in the Supabase database.
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

def check_functions(supabase_url, db_password):
    """Check if the required functions exist in the database."""
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
        
        # SQL to check if the exec_sql function exists
        sql = """
        SELECT EXISTS (
            SELECT 1 
            FROM pg_proc 
            WHERE proname = 'exec_sql' 
            AND pg_function_is_visible(oid)
        );
        """
        
        # Execute the SQL
        cursor.execute(sql)
        
        # Get the result
        exec_sql_exists = cursor.fetchone()[0]
        
        # SQL to check if the update_updated_at_column function exists
        sql = """
        SELECT EXISTS (
            SELECT 1 
            FROM pg_proc 
            WHERE proname = 'update_updated_at_column' 
            AND pg_function_is_visible(oid)
        );
        """
        
        # Execute the SQL
        cursor.execute(sql)
        
        # Get the result
        update_updated_at_column_exists = cursor.fetchone()[0]
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        # Print the results
        print(f"exec_sql function exists: {'✅' if exec_sql_exists else '❌'}")
        print(f"update_updated_at_column function exists: {'✅' if update_updated_at_column_exists else '❌'}")
        
        # Save the results to a JSON file
        results = {
            "timestamp": str(datetime.now()),
            "exec_sql_exists": exec_sql_exists,
            "update_updated_at_column_exists": update_updated_at_column_exists,
            "all_functions_exist": exec_sql_exists and update_updated_at_column_exists
        }
        
        with open("function_check_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to function_check_results.json")
        
        return exec_sql_exists and update_updated_at_column_exists
    except Exception as e:
        print(f"❌ Error checking functions: {str(e)}")
        return False

def main():
    """Main function."""
    # Check environment variables
    supabase_url, supabase_key, db_password = check_environment()
    
    # Check if the required functions exist
    all_functions_exist = check_functions(supabase_url, db_password)
    
    if all_functions_exist:
        print("\n✅ All required functions exist!")
        print("\nNext steps:")
        print("1. Run 'python check_tables.py' to verify that all required tables exist")
        print("2. If any tables are missing, run 'python create_missing_tables.py' to create them")
        sys.exit(0)
    else:
        print("\n❌ Some required functions are missing.")
        print("\nNext steps:")
        print("1. Run 'python create_exec_sql_direct.py' to create the missing functions")
        print("2. Run this script again to verify that the functions were created successfully")
        sys.exit(1)

if __name__ == "__main__":
    main() 