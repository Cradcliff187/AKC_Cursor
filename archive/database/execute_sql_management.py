#!/usr/bin/env python3
"""
Execute SQL using Supabase Management API

This script executes SQL statements directly using the Supabase Management API.
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_MANAGEMENT_KEY = os.getenv('SUPABASE_MANAGEMENT_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_SERVICE_KEY: {'Set (length: ' + str(len(SUPABASE_SERVICE_KEY)) + ')' if SUPABASE_SERVICE_KEY else 'Not set'}")
print(f"SUPABASE_MANAGEMENT_KEY: {'Set (length: ' + str(len(SUPABASE_MANAGEMENT_KEY)) + ')' if SUPABASE_MANAGEMENT_KEY else 'Not set'}")

# Extract project ID from URL
if SUPABASE_URL:
    project_id = SUPABASE_URL.split('//')[1].split('.')[0]
    print(f"Project ID: {project_id}")
else:
    project_id = None
    print("Project ID: Not available")

def check_environment():
    """Check if all required environment variables are set."""
    if not SUPABASE_URL:
        print("Error: SUPABASE_URL environment variable is not set.")
        return False
    
    if not SUPABASE_SERVICE_KEY:
        print("Error: SUPABASE_SERVICE_ROLE_KEY environment variable is not set.")
        return False
    
    if not SUPABASE_MANAGEMENT_KEY:
        print("Error: SUPABASE_MANAGEMENT_KEY environment variable is not set.")
        print("Please set this variable with your Supabase Management API key.")
        print("You can find this in your Supabase dashboard under Project Settings > API.")
        return False
    
    return True

def execute_sql_management(sql_statement):
    """Execute a SQL statement using the Supabase Management API."""
    if not SUPABASE_URL or not SUPABASE_MANAGEMENT_KEY or not project_id:
        print("Error: Supabase credentials not set.")
        return False

    # Endpoint for SQL execution
    url = f"https://api.supabase.com/v1/projects/{project_id}/sql"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {SUPABASE_MANAGEMENT_KEY}",
        "Content-Type": "application/json"
    }
    
    # Data
    data = {
        "query": sql_statement
    }
    
    print(f"Executing SQL via Management API: {sql_statement[:100]}...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code in [200, 201, 204]:
            print(f"SQL executed successfully.")
            return True
        else:
            print(f"Error executing SQL: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Exception executing SQL: {str(e)}")
        return False

def execute_sql_file_management(file_path):
    """Execute a SQL file using the Management API."""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        print(f"SQL content length: {len(sql_content)}")
        
        # For simple SQL files, just execute the entire content
        if len(sql_content) < 5000:
            print("Executing entire SQL file as a single statement")
            return execute_sql_management(sql_content)
        
        # For more complex files, try to split intelligently
        print("Splitting SQL file into statements")
        
        # Remove comments
        sql_lines = []
        for line in sql_content.split('\n'):
            if line.strip().startswith('--'):
                continue
            sql_lines.append(line)
        
        sql_content = '\n'.join(sql_lines)
        
        # Split by semicolons, but be careful with function definitions
        statements = []
        current_statement = []
        in_function_body = False
        
        for line in sql_content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.upper().startswith('CREATE OR REPLACE FUNCTION') or line.upper().startswith('CREATE FUNCTION'):
                in_function_body = True
                current_statement.append(line)
            elif in_function_body:
                current_statement.append(line)
                if line.endswith('$$;') or line.endswith('LANGUAGE plpgsql;'):
                    in_function_body = False
                    statements.append('\n'.join(current_statement))
                    current_statement = []
            elif line.endswith(';'):
                current_statement.append(line)
                statements.append('\n'.join(current_statement))
                current_statement = []
            else:
                current_statement.append(line)
        
        # Add any remaining statement
        if current_statement:
            statements.append('\n'.join(current_statement))
        
        print(f"Number of SQL statements after parsing: {len(statements)}")
        
        success_count = 0
        error_count = 0
        
        for statement in statements:
            if statement.strip():
                if execute_sql_management(statement):
                    success_count += 1
                else:
                    error_count += 1
        
        print(f"SQL file execution completed: {success_count} statements succeeded, {error_count} statements failed.")
        return error_count == 0
    except Exception as e:
        print(f"Error executing SQL file {file_path}: {str(e)}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python execute_sql_management.py <sql_file>")
        return False
    
    # Check environment
    if not check_environment():
        return False
    
    # Execute SQL file
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    print(f"Executing SQL file: {file_path}")
    return execute_sql_file_management(file_path)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 