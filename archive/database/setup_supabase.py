import os
from dotenv import load_dotenv
from supabase import create_client, Client
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import time

# Load environment variables
load_dotenv()

# Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Using service key for admin operations
db_password = os.getenv("SUPABASE_DB_PASSWORD")  # Database password from Project Settings

def setup_database():
    """Set up the Supabase database with our schema."""
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Connect to database using psycopg2
        project_id = supabase_url.split('//')[1].split('.')[0]
        db_url = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
        
        print("Attempting to connect to database...")
        
        # Connect to database
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Successfully connected to database!")
        
        # Read and execute schema
        print("Reading schema file...")
        with open('supabase_schema.sql', 'r') as file:
            schema_sql = file.read()
            # Split the SQL into individual statements
            statements = schema_sql.split(';')
            
            # Execute each statement separately
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        print(f"Successfully executed: {statement[:100]}...")
                    except Exception as e:
                        print(f"Error executing statement: {str(e)}")
                        print(f"Statement: {statement[:100]}...")
        
        print("Successfully set up database schema!")
        
        # Apply RLS policies
        apply_rls_policies(conn)
        
        # Set up functions and triggers
        setup_functions_and_triggers(conn)
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\nVerifying setup...")
        time.sleep(2)  # Give Supabase a moment to process changes
        verify_setup(supabase)
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

def apply_rls_policies(conn):
    """Apply Row Level Security policies to tables"""
    print("\nApplying Row Level Security policies...")
    
    try:
        cursor = conn.cursor()
        
        # First, enable RLS on all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"ALTER TABLE public.{table_name} ENABLE ROW LEVEL SECURITY;")
                print(f"Enabled RLS on table: {table_name}")
            except Exception as e:
                print(f"Error enabling RLS on {table_name}: {str(e)}")
        
        # Now apply the RLS policies from the file
        print("Applying RLS policies from file...")
        with open('rls_policies.sql', 'r') as file:
            rls_sql = file.read()
            # Split the SQL into individual statements
            statements = rls_sql.split(';')
            
            # Execute each statement separately
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        print(f"Successfully applied policy: {statement[:100]}...")
                    except Exception as e:
                        print(f"Error applying policy: {str(e)}")
                        print(f"Statement: {statement[:100]}...")
        
        cursor.close()
        print("Successfully applied RLS policies!")
        
    except Exception as e:
        print(f"Error applying RLS policies: {str(e)}")
        raise

def setup_functions_and_triggers(conn):
    """Set up database functions and triggers"""
    print("\nSetting up functions and triggers...")
    
    try:
        cursor = conn.cursor()
        
        # Check if trigger_function.sql exists
        if os.path.exists('trigger_function.sql'):
            with open('trigger_function.sql', 'r') as file:
                trigger_function_sql = file.read()
                try:
                    cursor.execute(trigger_function_sql)
                    print("Successfully created trigger functions")
                except Exception as e:
                    print(f"Error creating trigger functions: {str(e)}")
        
        # Check if triggers.sql exists
        if os.path.exists('triggers.sql'):
            with open('triggers.sql', 'r') as file:
                triggers_sql = file.read()
                # Split the SQL into individual statements
                statements = triggers_sql.split(';')
                
                # Execute each statement separately
                for statement in statements:
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                            print(f"Successfully created trigger: {statement[:100]}...")
                        except Exception as e:
                            print(f"Error creating trigger: {str(e)}")
                            print(f"Statement: {statement[:100]}...")
        
        cursor.close()
        print("Successfully set up functions and triggers!")
        
    except Exception as e:
        print(f"Error setting up functions and triggers: {str(e)}")
        raise

def verify_setup(supabase):
    """Verify the database setup"""
    print("\nVerifying database setup...")
    
    try:
        # Check if tables exist
        response = supabase.rpc(
            "exec_sql", 
            {"sql_query": """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """}
        ).execute()
        
        if "error" in response:
            print(f"Error querying tables: {response['error']}")
            return
        
        tables = [row["table_name"] for row in response.data]
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        # Check if RLS is enabled
        response = supabase.rpc(
            "exec_sql", 
            {"sql_query": """
                SELECT tablename, rowsecurity 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """}
        ).execute()
        
        if "error" in response:
            print(f"Error querying RLS status: {response['error']}")
            return
        
        rls_tables = [row["tablename"] for row in response.data if row["rowsecurity"]]
        print(f"RLS enabled on {len(rls_tables)} tables: {', '.join(rls_tables)}")
        
        # Check RLS policies
        response = supabase.rpc(
            "exec_sql", 
            {"sql_query": """
                SELECT tablename, count(*) as policy_count
                FROM pg_policies
                WHERE schemaname = 'public'
                GROUP BY tablename
            """}
        ).execute()
        
        if "error" in response:
            print(f"Error querying RLS policies: {response['error']}")
            return
        
        for row in response.data:
            print(f"Table {row['tablename']} has {row['policy_count']} RLS policies")
        
        print("\n✅ Database setup verification complete!")
        
    except Exception as e:
        print(f"Error verifying setup: {str(e)}")
        raise

def main():
    """Main function to run the setup"""
    print("=== Supabase Database Setup ===\n")
    
    if not supabase_url:
        print("Error: SUPABASE_URL environment variable is not set!")
        return 1
        
    if not supabase_key:
        print("Error: SUPABASE_SERVICE_KEY environment variable is not set!")
        return 1
        
    if not db_password:
        print("Error: SUPABASE_DB_PASSWORD environment variable is not set!")
        print("Please set it to the database password from Project Settings -> Database")
        return 1
        
    try:
        setup_database()
        print("\n✅ Supabase setup completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Supabase setup failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 