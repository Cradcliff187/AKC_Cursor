#!/usr/bin/env python3
"""
Run Supabase API

This script runs the Supabase API directly, with support for Google Cloud Run.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("=" * 80)
    print("Running Supabase API")
    print("=" * 80)
    
    # Check if supabase_api.py exists
    if not os.path.exists('supabase_api.py'):
        print("Error: supabase_api.py file not found.")
        sys.exit(1)
    
    # Get port from environment variable (for Google Cloud Run compatibility)
    port = int(os.getenv("PORT", 8001))
    
    print(f"Starting Supabase API on port {port}...")
    
    # Run the application
    uvicorn.run("supabase_api:app", host="0.0.0.0", port=port, reload=False) 