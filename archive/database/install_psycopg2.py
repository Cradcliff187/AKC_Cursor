#!/usr/bin/env python3
"""
Install psycopg2 if not already installed.
"""

import subprocess
import sys
import importlib.util

def check_package(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name):
    """Install a package using pip."""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {str(e)}")
        return False

def main():
    """Main function."""
    # Check if psycopg2 is installed
    if check_package("psycopg2"):
        print("✅ psycopg2 is already installed")
    else:
        print("psycopg2 is not installed. Attempting to install...")
        try:
            # Try installing psycopg2-binary first (easier to install)
            if install_package("psycopg2-binary"):
                print("Using psycopg2-binary")
            else:
                # If that fails, try installing psycopg2
                print("Attempting to install psycopg2 instead...")
                if install_package("psycopg2"):
                    print("Using psycopg2")
                else:
                    print("❌ Failed to install either psycopg2 or psycopg2-binary")
                    print("Please install manually with:")
                    print("pip install psycopg2-binary")
                    sys.exit(1)
        except Exception as e:
            print(f"❌ Error during installation: {str(e)}")
            sys.exit(1)
    
    print("\nNext steps:")
    print("1. Run 'python create_exec_sql_direct.py' to create the required database functions")
    
if __name__ == "__main__":
    main() 