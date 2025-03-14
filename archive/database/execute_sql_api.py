#!/usr/bin/env python3
"""
Execute SQL API

This script executes SQL statements directly using the Supabase SQL API.
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

def check_environment():
    """Check if all required environment variables are set."""
    if not SUPABASE_URL:
        print("Error: SUPABASE_URL environment variable is not set.")
        return False
    
    if not SUPABASE_SERVICE_KEY:
        print("Error: SUPABASE_SERVICE_ROLE_KEY environment variable is not set.")
        return False
    
    return True

def execute_sql(sql_statement):
    """Execute a SQL statement directly using the Supabase SQL API."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("Error: Supabase credentials not set.")
        return False

    # Endpoint for SQL execution
    url = f"{SUPABASE_URL}/rest/v1"
    
    # Headers
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # For SQL statements that might return data
    if sql_statement.lower().strip().startswith(('select', 'with')):
        # Use the SQL API
        sql_url = f"{SUPABASE_URL}/rest/v1/sql"
        data = {"query": sql_statement}
        
        try:
            response = requests.post(sql_url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"SQL query executed successfully: {sql_statement[:50]}...")
                return True
            else:
                print(f"Error executing SQL query: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"Exception executing SQL query: {str(e)}")
            return False
    else:
        # For DDL statements, use the SQL API with minimal return
        sql_url = f"{SUPABASE_URL}/rest/v1/sql"
        data = {"query": sql_statement}
        headers["Prefer"] = "return=minimal"
        
        try:
            response = requests.post(sql_url, headers=headers, json=data)
            
            if response.status_code in [200, 201, 204]:
                print(f"SQL statement executed successfully: {sql_statement[:50]}...")
                return True
            else:
                print(f"Error executing SQL statement: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"Exception executing SQL statement: {str(e)}")
            return False

def execute_sql_file(file_path):
    """Execute a SQL file."""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        # Split the SQL into individual statements
        statements = sql_content.split(';')
        
        success_count = 0
        error_count = 0
        
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
            
            if execute_sql(statement):
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
        print("Usage: python execute_sql_api.py <sql_file>")
        return False
    
    # Check environment
    if not check_environment():
        return False
    
    # Execute SQL file
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    return execute_sql_file(file_path)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 