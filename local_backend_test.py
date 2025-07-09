import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123",
    "nom": "Admin",
    "prenom": "Test",
    "role": "administrateur"
}

# Test results
test_results = {}

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

def test_auth_register():
    print_header("Testing User Registration")
    success, message, data = make_request("post", "/auth/register", ADMIN_USER, expected_status=200)
    
    if success:
        print_test_result("Register user", True, f"Created user: {ADMIN_USER['email']}")
        return True
    else:
        print_test_result("Register user", False, message)
        return False

def test_auth_login():
    print_header("Testing User Login")
    login_data = {
        "email": ADMIN_USER["email"],
        "password": ADMIN_USER["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Login user", True, f"Logged in as: {ADMIN_USER['email']}")
        return data["access_token"]
    else:
        print_test_result("Login user", False, message)
        return None

def test_auth_me(token):
    print_header("Testing Get Current User")
    success, message, data = make_request("get", "/auth/me", token=token, expected_status=200)
    
    if success and data and data.get("email") == ADMIN_USER["email"]:
        print_test_result("Get current user", True, f"Retrieved user: {data['email']}")
        return True
    else:
        print_test_result("Get current user", False, message)
        return False

def test_dashboard_stats(token):
    print_header("Testing Dashboard Stats")
    success, message, data = make_request("get", "/dashboard/stats", token=token, expected_status=200)
    
    if success and data and isinstance(data, dict):
        print_test_result("Get dashboard stats", True, f"Retrieved dashboard stats: {data}")
        return True
    else:
        print_test_result("Get dashboard stats", False, message)
        return False

def test_fournisseurs(token):
    print_header("Testing Fournisseurs API")
    success, message, data = make_request("get", "/fournisseurs", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get fournisseurs", True, f"Retrieved {len(data)} fournisseurs")
        return True
    else:
        print_test_result("Get fournisseurs", False, message)
        return False

def test_articles(token):
    print_header("Testing Articles API")
    success, message, data = make_request("get", "/articles", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get articles", True, f"Retrieved {len(data)} articles")
        return True
    else:
        print_test_result("Get articles", False, message)
        return False

def test_commandes(token):
    print_header("Testing Commandes API")
    success, message, data = make_request("get", "/commandes", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get commandes", True, f"Retrieved {len(data)} commandes")
        return True
    else:
        print_test_result("Get commandes", False, message)
        return False

def test_alertes(token):
    print_header("Testing Alertes API")
    success, message, data = make_request("get", "/alertes", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get alertes", True, f"Retrieved {len(data)} alertes")
        return True
    else:
        print_test_result("Get alertes", False, message)
        return False

def run_tests():
    print_header("STARTING BACKEND API TESTS")
    
    # Try to login first
    token = test_auth_login()
    
    # If login fails, try to register
    if not token:
        print("Login failed, trying to register...")
        registered = test_auth_register()
        if registered:
            token = test_auth_login()
    
    if not token:
        print("Authentication failed, cannot proceed with tests")
        return
    
    # Test authentication
    test_auth_me(token)
    
    # Test main APIs
    test_dashboard_stats(token)
    test_fournisseurs(token)
    test_articles(token)
    test_commandes(token)
    test_alertes(token)
    
    print_header("BACKEND API TESTS COMPLETED")

if __name__ == "__main__":
    run_tests()