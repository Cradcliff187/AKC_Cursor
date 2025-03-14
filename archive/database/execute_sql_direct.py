#!/usr/bin/env python3
"""
Execute SQL Directly

This script executes a SQL script directly in Supabase without using the exec_sql function.
"""

import os
import sys
import re
from dotenv import load_dotenv
import requests

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

def remove_comments(sql):
    """Remove SQL comments from the SQL content."""
    # Remove single-line comments
    sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
    # Remove multi-line comments
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    return sql

def split_sql_statements(sql_content):
    """Split SQL content into individual statements, handling function definitions properly."""
    # Remove comments
    sql_content = remove_comments(sql_content)
    
    # If the SQL is simple (less than 5000 characters and contains one or fewer semicolons),
    # just return it as a single statement
    if len(sql_content) < 5000 and sql_content.count(';') <= 1:
        return [sql_content]
    
    # Otherwise, we need to handle function definitions and other complex SQL
    statements = []
    current_statement = ""
    in_function_body = False
    dollar_quote_tag = None
    
    for line in sql_content.splitlines():
        line = line.strip()
        if not line:
            continue
        
        # Check for dollar-quoted string start/end
        if dollar_quote_tag:
            current_statement += line + "\n"
            if line.endswith(dollar_quote_tag):
                dollar_quote_tag = None
            continue
        
        # Check for dollar-quoted string start
        dollar_quote_match = re.search(r'\$([a-zA-Z0-9_]*)\$', line)
        if dollar_quote_match and not dollar_quote_tag:
            dollar_quote_tag = dollar_quote_match.group(0)
            current_statement += line + "\n"
            continue
        
        # Check for function body start
        if re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION', line, re.IGNORECASE) or \
           re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE', line, re.IGNORECASE):
            in_function_body = True
        
        current_statement += line + "\n"
        
        # Check for function body end
        if in_function_body and line.rstrip().endswith(';') and \
           (re.search(r'LANGUAGE\s+[a-zA-Z_]+\s*;', line, re.IGNORECASE) or \
            re.search(r'SECURITY\s+(?:DEFINER|INVOKER)\s*;', line, re.IGNORECASE)):
            in_function_body = False
            statements.append(current_statement)
            current_statement = ""
        # Check for normal statement end
        elif not in_function_body and line.rstrip().endswith(';'):
            statements.append(current_statement)
            current_statement = ""
    
    # Add any remaining statement
    if current_statement.strip():
        statements.append(current_statement)
    
    print(f"Split SQL into {len(statements)} statements")
    return statements

def execute_sql_direct(file_path, supabase_url, supabase_key):
    """Execute a SQL file directly in Supabase."""
    try:
        # Read the SQL file
        with open(file_path, 'r') as file:
            sql_content = file.read()
        
        # Check if the SQL is simple enough to execute as a single statement
        if len(sql_content) < 5000 and sql_content.count(';') <= 1:
            print(f"SQL file is simple (length: {len(sql_content)} chars). Executing as a single statement.")
            statements = [sql_content]
        else:
            # Split the SQL into statements
            statements = split_sql_statements(sql_content)
        
        # Execute the SQL using the Supabase REST API
        headers = {
            'Content-Type': 'application/json',
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}'
        }
        
        success_count = 0
        failure_count = 0
        
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            
            # Use the SQL API endpoint
            sql_url = f"{supabase_url}/rest/v1/sql"
            
            # Execute the SQL statement
            response = requests.post(
                sql_url,
                headers=headers,
                json={'query': stmt}
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
        print(f"Error executing SQL file: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if a file path is provided
    if len(sys.argv) < 2:
        print("Usage: python execute_sql_direct.py <sql_file_path>")
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
    success = execute_sql_direct(file_path, supabase_url, supabase_key)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 