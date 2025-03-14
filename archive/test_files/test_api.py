#!/usr/bin/env python3
"""
Test the Supabase API endpoints.
"""

import requests
import json
import sys
import argparse
from datetime import datetime

OUTPUT_FILE = "api_test_results.txt"

def test_endpoint(endpoint, output_file, base_url):
    """Test an API endpoint."""
    url = f"{base_url}{endpoint}"
    output_file.write(f"Testing endpoint: {url}\n")
    
    try:
        response = requests.get(url)
        output_file.write(f"Status code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            output_file.write("Response data:\n")
            output_file.write(json.dumps(data, indent=2) + "\n")
        else:
            output_file.write(f"Error: {response.text}\n")
        
        output_file.write("-" * 80 + "\n")
        return response.status_code == 200
    except Exception as e:
        output_file.write(f"Exception: {str(e)}\n")
        output_file.write("-" * 80 + "\n")
        return False

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Supabase API endpoints")
    parser.add_argument("--url", default="http://localhost:8001", help="Base URL of the API")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output file for test results")
    args = parser.parse_args()
    
    base_url = args.url
    output_file_path = args.output
    
    with open(output_file_path, "w") as output_file:
        output_file.write("=" * 80 + "\n")
        output_file.write("Testing Supabase API Endpoints\n")
        output_file.write(f"Base URL: {base_url}\n")
        output_file.write(f"Timestamp: {datetime.now()}\n")
        output_file.write("=" * 80 + "\n\n")
        
        # Test root endpoint
        test_endpoint("/", output_file, base_url)
        
        # Test health check endpoint
        test_endpoint("/health", output_file, base_url)
        
        # Test get tables endpoint
        test_endpoint("/api/tables", output_file, base_url)
        
        # Test get users endpoint
        test_endpoint("/api/users", output_file, base_url)
        
        # Test get table schema endpoint for user_profiles
        test_endpoint("/api/tables/user_profiles/schema", output_file, base_url)
        
        # Test get table data endpoint for user_profiles
        test_endpoint("/api/tables/user_profiles/data", output_file, base_url)
        
        # Test client endpoints
        test_endpoint("/api/clients", output_file, base_url)
        
        # Test project endpoints
        test_endpoint("/api/projects", output_file, base_url)
        
        output_file.write("\nTesting complete!\n")
    
    print(f"Test results saved to {output_file_path}")

if __name__ == "__main__":
    main() 