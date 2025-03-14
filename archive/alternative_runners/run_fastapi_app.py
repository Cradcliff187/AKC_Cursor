#!/usr/bin/env python3
"""
Run FastAPI Application with Supabase Integration

This script runs the FastAPI application with Supabase integration,
with proper error handling and detailed logging.
"""

import os
import sys
import time
import traceback
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

def check_environment():
    """Check if the required environment variables are set."""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Error: The following environment variables are missing: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file.")
        return False
    
    print("✅ All required environment variables are set.")
    print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
    print(f"Supabase key length: {len(os.getenv('SUPABASE_KEY'))}")
    print(f"Supabase service role key length: {len(os.getenv('SUPABASE_SERVICE_ROLE_KEY'))}")
    print(f"Supabase DB password is set: {'Yes' if os.getenv('SUPABASE_DB_PASSWORD') else 'No'}")
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import fastapi
        import supabase
        import psycopg2
        print("✅ All required dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Error: Missing dependency: {str(e)}")
        print("Please install all required dependencies with: pip install -r requirements.txt")
        return False

def run_app():
    """Run the FastAPI application."""
    try:
        # Check if supabase_api.py exists
        if not os.path.exists('supabase_api.py'):
            print("❌ Error: supabase_api.py file not found.")
            print("Please make sure you're in the correct directory.")
            return False
        
        # Get port from environment variable or use default
        port = int(os.getenv("PORT", 8000))
        
        print(f"\n🚀 Starting FastAPI application with Supabase integration on port {port}...")
        print("Press Ctrl+C to stop the server.")
        
        # Run the application
        uvicorn.run("supabase_api:app", host="0.0.0.0", port=port, reload=True)
        
        return True
    except Exception as e:
        print(f"❌ Error running FastAPI application: {str(e)}")
        print("\nDetailed error traceback:")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("=" * 80)
    print("AKC Construction CRM - FastAPI Application with Supabase Integration")
    print("=" * 80)
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run the application
    if not run_app():
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        print("\nDetailed error traceback:")
        traceback.print_exc()
        sys.exit(1)
 