"""
Create exec_sql Function

This script creates the exec_sql function in Supabase using the Supabase Python client.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

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

def create_exec_sql_function(supabase_url, supabase_key):
    """Create the exec_sql function in Supabase."""
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
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
        
        # Execute the SQL
        response = supabase.table('_exec_sql_temp').select('*').execute()
        print(f"Connected to Supabase successfully.")
        
        # Use the PostgreSQL function to execute the SQL
        response = supabase.rpc('exec_sql', {'query': sql}).execute()
        print(f"exec_sql function created successfully.")
        
        return True
    except Exception as e:
        print(f"Error creating exec_sql function: {str(e)}")
        
        # Try a different approach if the first one fails
        try:
            print("Trying alternative approach...")
            
            # Create a temporary table to execute the SQL
            create_temp_table_sql = """
            CREATE TABLE IF NOT EXISTS public._exec_sql_temp (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Execute the SQL using the REST API
            import requests
            
            headers = {
                'Content-Type': 'application/json',
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}'
            }
            
            # Create the temporary table
            response = requests.post(
                f"{supabase_url}/rest/v1/sql",
                headers=headers,
                json={'query': create_temp_table_sql}
            )
            
            if response.status_code != 200:
                print(f"Error creating temporary table: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            # Create the exec_sql function
            response = requests.post(
                f"{supabase_url}/rest/v1/sql",
                headers=headers,
                json={'query': sql}
            )
            
            if response.status_code == 200:
                print(f"exec_sql function created successfully using alternative approach.")
                return True
            else:
                print(f"Error creating exec_sql function: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e2:
            print(f"Error with alternative approach: {str(e2)}")
            return False

if __name__ == "__main__":
    # Check the environment
    supabase_url, supabase_key = check_environment()
    
    # Create the exec_sql function
    success = create_exec_sql_function(supabase_url, supabase_key)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1) 