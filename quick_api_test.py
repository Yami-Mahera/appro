import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123"
}

# Test results
test_results = {
    "dashboard_stats": {"success": False, "message": "Not tested"},
    "articles": {"success": False, "message": "Not tested"},
    "auth_login": {"success": False, "message": "Not tested"},
    "services": {"success": False, "message": "Not tested"}
}

# Helper functions
def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_test_result(test_name, success, message=""):
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{test_name}: {status}")
    if message:
        print(f"  - {message}")

def make_request(method, endpoint, data=None, token=None, expected_status=200):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            return False, f"Unsupported method: {method}", None
        
        if response.status_code == expected_status:
            try:
                return True, "Success", response.json() if response.text else None
            except json.JSONDecodeError:
                return True, "Success (no JSON response)", response.text
        else:
            return False, f"Expected status {expected_status}, got {response.status_code}: {response.text}", None
    except Exception as e:
        return False, f"Request error: {str(e)}", None

def test_auth_login():
    print_header("Testing User Login")
    login_data = {
        "email": ADMIN_USER["email"],
        "password": ADMIN_USER["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Login user", True, f"Logged in as: {ADMIN_USER['email']}")
        test_results["auth_login"]["success"] = True
        test_results["auth_login"]["message"] = f"Successfully logged in as: {ADMIN_USER['email']}"
        return data["access_token"]
    else:
        print_test_result("Login user", False, message)
        test_results["auth_login"]["message"] = message
        return None

def test_dashboard_stats(token):
    print_header("Testing Dashboard Stats API")
    success, message, data = make_request("get", "/dashboard/stats", token=token, expected_status=200)
    
    if success and data and isinstance(data, dict):
        print_test_result("Get dashboard stats", True, f"Retrieved dashboard stats successfully")
        print(f"Dashboard stats: {json.dumps(data, indent=2)}")
        
        # Check if all required fields are present
        required_fields = [
            "total_fournisseurs", 
            "total_articles", 
            "total_commandes", 
            "alertes_non_lues", 
            "articles_stock_bas", 
            "commandes_en_cours"
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print_test_result("Dashboard stats fields", False, f"Missing fields: {', '.join(missing_fields)}")
            test_results["dashboard_stats"]["success"] = False
            test_results["dashboard_stats"]["message"] = f"Missing fields in response: {', '.join(missing_fields)}"
            return False
        
        print_test_result("Dashboard stats fields", True, "All required fields are present")
        test_results["dashboard_stats"]["success"] = True
        test_results["dashboard_stats"]["message"] = "Successfully retrieved dashboard stats with all required fields"
        return True
    else:
        print_test_result("Get dashboard stats", False, message)
        test_results["dashboard_stats"]["message"] = message
        return False

def test_articles(token):
    print_header("Testing Articles API")
    success, message, data = make_request("get", "/articles", token=token, expected_status=200)
    
    if success and data:
        if isinstance(data, dict) and "articles" in data:
            articles = data["articles"]
            print_test_result("Get articles", True, f"Retrieved {len(articles)} articles")
            
            # Print the first article if available
            if articles and len(articles) > 0:
                print(f"First article: {json.dumps(articles[0], indent=2)}")
            
            test_results["articles"]["success"] = True
            test_results["articles"]["message"] = f"Successfully retrieved {len(articles)} articles"
            return True
        elif isinstance(data, list):
            print_test_result("Get articles", True, f"Retrieved {len(data)} articles")
            
            # Print the first article if available
            if data and len(data) > 0:
                print(f"First article: {json.dumps(data[0], indent=2)}")
            
            test_results["articles"]["success"] = True
            test_results["articles"]["message"] = f"Successfully retrieved {len(data)} articles"
            return True
        else:
            print_test_result("Get articles", False, "Unexpected response format")
            test_results["articles"]["message"] = "Unexpected response format"
            return False
    else:
        print_test_result("Get articles", False, message)
        test_results["articles"]["message"] = message
        return False

def check_services():
    print_header("Checking Backend Services")
    try:
        # Try to access the root endpoint to check if the backend is running
        response = requests.get(f"{BASE_URL}")
        
        if response.status_code == 200:
            print_test_result("Backend service", True, "Backend service is running")
            test_results["services"]["success"] = True
            test_results["services"]["message"] = "Backend service is running"
            return True
        else:
            print_test_result("Backend service", False, f"Backend service returned status code {response.status_code}")
            test_results["services"]["message"] = f"Backend service returned status code {response.status_code}"
            return False
    except Exception as e:
        print_test_result("Backend service", False, f"Error connecting to backend service: {str(e)}")
        test_results["services"]["message"] = f"Error connecting to backend service: {str(e)}"
        return False

def print_summary():
    print("\n" + "=" * 80)
    print(" TEST SUMMARY ".center(80, "="))
    print("=" * 80)
    
    all_passed = True
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{test_name}: {status}")
        print(f"  - {result['message']}")
        if not result["success"]:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print(" ALL TESTS PASSED SUCCESSFULLY ".center(80, "="))
    else:
        print(" SOME TESTS FAILED ".center(80, "="))
    print("=" * 80 + "\n")

def run_tests():
    print_header("STARTING BACKEND API TESTS")
    
    # Check if backend services are running
    services_running = check_services()
    if not services_running:
        print("Backend services are not running. Cannot proceed with tests.")
        print_summary()
        return
    
    # Login to get token
    token = test_auth_login()
    if not token:
        print("Authentication failed. Cannot proceed with tests.")
        print_summary()
        return
    
    # Test dashboard stats API
    test_dashboard_stats(token)
    
    # Test articles API
    test_articles(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_tests()