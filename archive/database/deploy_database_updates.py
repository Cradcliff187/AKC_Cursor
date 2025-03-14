#!/usr/bin/env python
"""
Database Deployment Script

This script deploys all the necessary updates to the Supabase database
to ensure it is aligned with the schema file and has all required configurations.
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv
from supabase import create_client

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

def create_supabase_client():
    """Create a Supabase client with the service role key."""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {str(e)}")
        return None

def execute_sql_file(supabase, file_path):
    """Execute a SQL file on the Supabase database."""
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
            
            try:
                # Execute the statement
                print(f"Executing SQL statement: {statement[:100]}...")
                
                # For statements that might return data
                if statement.lower().startswith(('select', 'with')):
                    response = supabase.rpc('exec_sql', {'query': statement}).execute()
                    print(f"Response: {response}")
                else:
                    # For statements that don't return data
                    response = supabase.rpc('exec_sql', {'query': statement}).execute()
                
                success_count += 1
            except Exception as e:
                print(f"Error executing SQL statement: {str(e)}")
                print(f"Statement: {statement}")
                error_count += 1
        
        print(f"SQL file execution completed: {success_count} statements succeeded, {error_count} statements failed.")
        return error_count == 0
    except Exception as e:
        print(f"Error executing SQL file {file_path}: {str(e)}")
        return False

def update_schema_file():
    """Update the schema file with missing tables."""
    try:
        subprocess.run([sys.executable, 'update_schema_file.py'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating schema file: {str(e)}")
        return False

def verify_configurations(supabase):
    """Verify that all configurations are properly set up."""
    try:
        # Execute the verification function
        response = supabase.rpc('verify_sql_configurations').execute()
        
        if response.data:
            print("\nConfiguration Verification Results:")
            all_configured = True
            
            for config in response.data:
                status = "✅" if config['status'] else "❌"
                print(f"{status} {config['configuration_name']}: {config['details']}")
                
                if not config['status']:
                    all_configured = False
            
            return all_configured
        else:
            print("Error: No verification results returned.")
            return False
    except Exception as e:
        print(f"Error verifying configurations: {str(e)}")
        return False

def main():
    """Main function."""
    print("Starting database deployment process...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create Supabase client
    supabase = create_supabase_client()
    if not supabase:
        sys.exit(1)
    
    # Update schema file
    print("\nStep 1: Updating schema file...")
    if update_schema_file():
        print("Schema file updated successfully.")
    else:
        print("Warning: Failed to update schema file. Continuing with deployment...")
    
    # Create exec_sql function if it doesn't exist
    print("\nStep 2: Creating exec_sql function...")
    try:
        create_function_query = """
        CREATE OR REPLACE FUNCTION exec_sql(query text) RETURNS SETOF json AS $$
        BEGIN
            RETURN QUERY EXECUTE query;
        END;
        $$ LANGUAGE plpgsql;
        """
        
        supabase.rpc('exec_sql', {'query': create_function_query}).execute()
        print("Created or updated the exec_sql function")
    except Exception as e:
        print(f"Error creating exec_sql function: {str(e)}")
        print("Will try to proceed with deployment anyway...")
    
    # Execute schema updates
    print("\nStep 3: Executing schema updates...")
    if execute_sql_file(supabase, 'schema_updates.sql'):
        print("Schema updates executed successfully.")
    else:
        print("Warning: Failed to execute schema updates. Continuing with deployment...")
    
    # Execute SQL configurations
    print("\nStep 4: Executing SQL configurations...")
    if execute_sql_file(supabase, 'sql_configurations.sql'):
        print("SQL configurations executed successfully.")
    else:
        print("Warning: Failed to execute SQL configurations. Continuing with deployment...")
    
    # Execute Google Cloud alignment updates
    print("\nStep 5: Executing Google Cloud alignment updates...")
    if execute_sql_file(supabase, 'google_cloud_alignment.sql'):
        print("Google Cloud alignment updates executed successfully.")
    else:
        print("Warning: Failed to execute Google Cloud alignment updates. Continuing with deployment...")
    
    # Verify configurations
    print("\nStep 6: Verifying configurations...")
    if verify_configurations(supabase):
        print("All configurations verified successfully.")
    else:
        print("Warning: Some configurations could not be verified.")
    
    print("\nDatabase deployment process completed.")

if __name__ == "__main__":
    main() 