import os
from dotenv import load_dotenv
from supabase import create_client, Client
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    if not db_password:
        print("Error: SUPABASE_DB_PASSWORD environment variable is not set!")
        print("Please set it to the database password from Project Settings -> Database")
        exit(1)
    setup_database() 