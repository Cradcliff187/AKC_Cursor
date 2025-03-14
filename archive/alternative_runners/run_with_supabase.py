#!/usr/bin/env python
"""
Run AKC Construction CRM with Supabase Integration

This script sets up the Supabase integration and runs the FastAPI application.
It performs the following steps:
1. Verifies Supabase connection
2. Checks if required tables exist
3. Applies RLS policies if needed
4. Starts the FastAPI application
"""

import os
import sys
import time
import subprocess
import uvicorn
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Supabase utilities
from check_supabase import check_supabase_connection
from setup_supabase import setup_database

# Load environment variables
load_dotenv()

def verify_supabase():
    """Verify Supabase connection and setup"""
    print("=== Verifying Supabase Connection ===")
    
    # Check Supabase connection
    connection_result = check_supabase_connection()
    
    if not connection_result.get("success", False):
        print("❌ Supabase connection failed!")
        print(f"Error: {connection_result.get('error', 'Unknown error')}")
        
        # Ask if user wants to continue anyway
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    else:
        print("✅ Supabase connection successful!")
    
    return connection_result

def setup_supabase_if_needed():
    """Set up Supabase database if needed"""
    print("\n=== Checking Supabase Setup ===")
    
    # Ask if user wants to set up Supabase
    response = input("Do you want to set up the Supabase database? (y/n): ")
    if response.lower() == 'y':
        try:
            setup_database()
            print("✅ Supabase database setup complete!")
        except Exception as e:
            print(f"❌ Error setting up Supabase database: {str(e)}")
            
            # Ask if user wants to continue anyway
            response = input("Do you want to continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Exiting...")
                sys.exit(1)

def run_app():
    """Run the FastAPI application"""
    print("\n=== Starting AKC Construction CRM ===")
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)

def main():
    """Main function to run the application with Supabase integration"""
    print("=== AKC Construction CRM with Supabase Integration ===\n")
    
    # Verify Supabase connection
    connection_result = verify_supabase()
    
    # Set up Supabase if needed
    setup_supabase_if_needed()
    
    # Run the application
    run_app()

if __name__ == "__main__":
    main() 