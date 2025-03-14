#!/usr/bin/env python
"""
Supabase Connection Checker

This script tests the connection to Supabase and verifies that all required
environment variables are set correctly. It can be run as a standalone script
or imported and used in other scripts.
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

def check_supabase_connection():
    """Test the connection to Supabase and verify environment variables."""
    results = {
        "timestamp": str(datetime.now()),
        "environment_variables": {},
        "connection_test": None,
        "auth_test": None,
        "query_test": None
    }
    
    # Check required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_SERVICE_ROLE_KEY"]
    for var in required_vars:
        value = os.getenv(var)
        results["environment_variables"][var] = {
            "present": value is not None,
            "length": len(value) if value else 0
        }
    
    try:
        # Only import supabase client if we have the necessary variables
        from supabase import create_client
        
        # Get environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Test with anonymous key first
        print(f"Testing connection to Supabase at {supabase_url} with anon key...")
        try:
            start_time = datetime.now()
            client = create_client(supabase_url, supabase_key)
            results["connection_test"] = {
                "status": "success",
                "key_type": "anon",
                "elapsed_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
            
            # Test authentication
            print("Testing authentication...")
            try:
                start_time = datetime.now()
                auth_response = client.auth.get_session()
                results["auth_test"] = {
                    "status": "success",
                    "elapsed_ms": (datetime.now() - start_time).total_seconds() * 1000
                }
            except Exception as e:
                results["auth_test"] = {
                    "status": "error",
                    "message": str(e),
                    "error_type": type(e).__name__
                }
                print(f"Auth test failed: {str(e)}")
            
            # Test simple query
            print("Testing database query...")
            try:
                start_time = datetime.now()
                query_response = client.table('user_profiles').select('id').limit(1).execute()
                results["query_test"] = {
                    "status": "success",
                    "has_data": hasattr(query_response, 'data'),
                    "elapsed_ms": (datetime.now() - start_time).total_seconds() * 1000
                }
            except Exception as e:
                results["query_test"] = {
                    "status": "error",
                    "message": str(e),
                    "error_type": type(e).__name__
                }
                print(f"Query test failed: {str(e)}")
                
        except Exception as e:
            results["connection_test"] = {
                "status": "error",
                "key_type": "anon",
                "message": str(e),
                "error_type": type(e).__name__
            }
            print(f"Connection test with anon key failed: {str(e)}")
        
        # Test with service role key
        if service_key:
            print(f"Testing connection with service role key...")
            try:
                start_time = datetime.now()
                service_client = create_client(supabase_url, service_key)
                results["service_role_test"] = {
                    "status": "success",
                    "elapsed_ms": (datetime.now() - start_time).total_seconds() * 1000
                }
                
                # Test query with service role
                print("Testing service role query...")
                try:
                    start_time = datetime.now()
                    service_query = service_client.table('user_profiles').select('id').limit(1).execute()
                    results["service_query_test"] = {
                        "status": "success",
                        "has_data": hasattr(service_query, 'data'),
                        "elapsed_ms": (datetime.now() - start_time).total_seconds() * 1000
                    }
                except Exception as e:
                    results["service_query_test"] = {
                        "status": "error",
                        "message": str(e),
                        "error_type": type(e).__name__
                    }
                    print(f"Service role query failed: {str(e)}")
            except Exception as e:
                results["service_role_test"] = {
                    "status": "error",
                    "message": str(e),
                    "error_type": type(e).__name__
                }
                print(f"Service role connection test failed: {str(e)}")
    
    except ImportError as e:
        results["import_error"] = str(e)
        print(f"Failed to import supabase client: {str(e)}")
    except Exception as e:
        results["unexpected_error"] = {
            "message": str(e),
            "error_type": type(e).__name__
        }
        print(f"Unexpected error: {str(e)}")
    
    return results

if __name__ == "__main__":
    print("Starting Supabase connection check...")
    results = check_supabase_connection()
    
    # Print results in a readable format
    print("\n=== Supabase Connection Check Results ===")
    print(f"Timestamp: {results['timestamp']}")
    
    print("\nEnvironment Variables:")
    for var, info in results["environment_variables"].items():
        status = "✅" if info["present"] else "❌"
        print(f"  {var}: {status} (length: {info['length']})")
    
    print("\nConnection Tests:")
    for test_name in ["connection_test", "auth_test", "query_test", "service_role_test", "service_query_test"]:
        if test_name in results:
            test = results[test_name]
            status = "✅" if test.get("status") == "success" else "❌"
            print(f"  {test_name}: {status}")
            if test.get("status") == "error":
                print(f"    Error: {test.get('message')}")
    
    # Save results to file
    with open("supabase_check_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nComplete results saved to supabase_check_results.json")
    
    # Exit with error code if any tests failed
    if any(test.get("status") == "error" 
           for test in [results.get(t) for t in 
                       ["connection_test", "auth_test", "query_test"]] 
           if test is not None):
        print("\nSome tests failed. See details above.")
        sys.exit(1)
    else:
        print("\nAll basic tests passed!")
        sys.exit(0) 