import requests
import sys
import time

def test_health_endpoint():
    url = "https://akc-crm-988587667075.us-east4.run.app/health"
    print(f"Testing health endpoint at {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_main_page():
    url = "https://akc-crm-988587667075.us-east4.run.app/"
    print(f"\nTesting main page at {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error testing main page: {e}")
        return False

def main():
    print("Starting deployment tests...")
    
    # Test health endpoint
    health_status = test_health_endpoint()
    print(f"Health endpoint test {'passed' if health_status else 'failed'}")
    
    # Wait a bit before testing main page
    time.sleep(2)
    
    # Test main page
    main_page_status = test_main_page()
    print(f"Main page test {'passed' if main_page_status else 'failed'}")
    
    # Overall status
    if health_status and main_page_status:
        print("\nAll tests passed! The application is running correctly.")
    else:
        print("\nSome tests failed. Please check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 