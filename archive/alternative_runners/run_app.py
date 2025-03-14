"""
Run Application

This script runs the FastAPI application and tests the database connection.
"""

import os
import sys
from dotenv import load_dotenv
from services.database_service import DatabaseService
from test_db_connection import test_database_connection

# Load environment variables
load_dotenv()

def check_environment():
    """Check if the required environment variables are set."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables.")
        print("Please create a .env file in the root directory with these variables.")
        sys.exit(1)
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase service key length: {len(supabase_key)}")

def run_app():
    """Run the FastAPI application."""
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    print("Checking environment variables...")
    check_environment()
    
    print("\nTesting database connection...")
    if test_database_connection():
        print("\nDatabase connection successful! Starting the application...")
        run_app()
    else:
        print("\nDatabase connection failed. Please check your Supabase credentials and try again.")
        sys.exit(1) 