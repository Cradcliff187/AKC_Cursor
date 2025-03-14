"""
Execute SQL Script

This script executes a SQL script in Supabase.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if the required environment variables are set."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables.")
        sys.exit(1)
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase service key length: {len(supabase_key)}")
    
    return supabase_url, supabase_key

def execute_sql_file(file_path, supabase_url, supabase_key):
    """Execute a SQL file in Supabase."""
    try:
        # Read the SQL file
        with open(file_path, 'r') as file:
            sql_content = file.read()
        
        # Execute the SQL using the Supabase REST API
        headers = {
            'Content-Type': 'application/json',
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }
        
        # Use the SQL API endpoint
        sql_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        
        # Execute the SQL
        response = requests.post(
            sql_url,
            headers=headers,
            json={'query': sql_content}
        )
        
        # Check the response
        if response.status_code == 200:
            print(f"SQL file executed successfully: {file_path}")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Error executing SQL file: {file_path}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            # If the error is because exec_sql doesn't exist, try using the SQL API directly
            if response.status_code == 404:
                print("Attempting to execute SQL directly using the SQL API...")
                return execute_sql_direct(sql_content, supabase_url, supabase_key)
            
            return False
    except Exception as e:
        print(f"Error executing SQL file: {str(e)}")
        return False

def execute_sql_direct(sql_content, supabase_url, supabase_key):
    """Execute SQL directly using the SQL API."""
    try:
        # Execute the SQL using the Supabase Management API
        headers = {
            'Content-Type': 'application/json',
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }
        
        # Use the SQL API endpoint
        sql_url = f"{supabase_url}/rest/v1"
        
        # Split the SQL into statements
        statements = sql_content.split(';')
        statements = [stmt.strip() for stmt in statements if stmt.strip()]
        
        success_count = 0
        failure_count = 0
        
        for stmt in statements:
            # Execute the SQL statement
            response = requests.post(
                sql_url,
                headers=headers,
                data=stmt
            )
            
            # Check the response
            if response.status_code == 200:
                print(f"SQL statement executed successfully")
                success_count += 1
            else:
                print(f"Error executing SQL statement")
                print(f"Status code: {response.status_code}")
                print(f"Response: {response.text}")
                failure_count += 1
        
        print(f"SQL execution summary: {success_count} statements succeeded, {failure_count} statements failed")
        return success_count > 0 and failure_count == 0
    except Exception as e:
        print(f"Error executing SQL directly: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if a file path is provided
    if len(sys.argv) < 2:
        print("Usage: python execute_sql.py <sql_file_path>")
        sys.exit(1)
    
    # Get the file path
    file_path = sys.argv[1]
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Check the environment
    supabase_url, supabase_key = check_environment()
    
    # Execute the SQL file
    success = execute_sql_file(file_path, supabase_url, supabase_key)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 