import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://b4255a0c-7cf9-4505-b4ad-25fa82f32bc9.preview.emergentagent.com/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123"
}

# Test results
test_results = {
    "auth": {
        "login": {"success": False, "message": "Not tested"},
        "me": {"success": False, "message": "Not tested"}
    },
    "dashboard": {
        "stats": {"success": False, "message": "Not tested"}
    },
    "fournisseurs": {
        "list": {"success": False, "message": "Not tested"}
    },
    "articles": {
        "list": {"success": False, "message": "Not tested"}
    },
    "commandes": {
        "list": {"success": False, "message": "Not tested"}
    },
    "alertes": {
        "list": {"success": False, "message": "Not tested"}
    }
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
        test_results["auth"]["login"]["success"] = True
        test_results["auth"]["login"]["message"] = f"Successfully logged in as: {ADMIN_USER['email']}"
        return data["access_token"]
    else:
        print_test_result("Login user", False, message)
        test_results["auth"]["login"]["message"] = message
        return None

def test_auth_me(token):
    print_header("Testing Get Current User")
    success, message, data = make_request("get", "/auth/me", token=token, expected_status=200)
    
    if success and data and "email" in data:
        print_test_result("Get current user", True, f"Retrieved user: {data['email']}")
        test_results["auth"]["me"]["success"] = True
        test_results["auth"]["me"]["message"] = f"Successfully retrieved user info: {data['email']}"
        return True
    else:
        print_test_result("Get current user", False, message)
        test_results["auth"]["me"]["message"] = message
        return False

def test_dashboard_stats(token):
    print_header("Testing Dashboard Stats")
    success, message, data = make_request("get", "/dashboard/stats", token=token, expected_status=200)
    
    if success and data and isinstance(data, dict):
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
            print_test_result("Get dashboard stats", False, f"Missing fields in response: {', '.join(missing_fields)}")
            test_results["dashboard"]["stats"]["success"] = False
            test_results["dashboard"]["stats"]["message"] = f"Missing fields in response: {', '.join(missing_fields)}"
            return False
        
        print_test_result("Get dashboard stats", True, f"Retrieved dashboard stats with all required fields")
        print(f"  - total_fournisseurs: {data['total_fournisseurs']}")
        print(f"  - total_articles: {data['total_articles']}")
        print(f"  - total_commandes: {data['total_commandes']}")
        print(f"  - alertes_non_lues: {data['alertes_non_lues']}")
        print(f"  - articles_stock_bas: {data['articles_stock_bas']}")
        print(f"  - commandes_en_cours: {data['commandes_en_cours']}")
        
        test_results["dashboard"]["stats"]["success"] = True
        test_results["dashboard"]["stats"]["message"] = "Successfully retrieved dashboard stats with all required fields"
        return True
    else:
        print_test_result("Get dashboard stats", False, message)
        test_results["dashboard"]["stats"]["message"] = message
        return False

def test_fournisseurs(token):
    print_header("Testing Fournisseurs API")
    success, message, data = make_request("get", "/fournisseurs", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get fournisseurs", True, f"Retrieved {len(data)} fournisseurs")
        if len(data) > 0:
            print(f"  - First fournisseur: {data[0]['nom']}")
        test_results["fournisseurs"]["list"]["success"] = True
        test_results["fournisseurs"]["list"]["message"] = f"Successfully retrieved {len(data)} fournisseurs"
        return True
    else:
        print_test_result("Get fournisseurs", False, message)
        test_results["fournisseurs"]["list"]["message"] = message
        return False

def test_articles(token):
    print_header("Testing Articles API")
    success, message, data = make_request("get", "/articles", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get articles", True, f"Retrieved {len(data)} articles")
        if len(data) > 0:
            print(f"  - First article: {data[0]['nom']}")
        test_results["articles"]["list"]["success"] = True
        test_results["articles"]["list"]["message"] = f"Successfully retrieved {len(data)} articles"
        return True
    else:
        print_test_result("Get articles", False, message)
        test_results["articles"]["list"]["message"] = message
        return False

def test_commandes(token):
    print_header("Testing Commandes API")
    success, message, data = make_request("get", "/commandes", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get commandes", True, f"Retrieved {len(data)} commandes")
        if len(data) > 0:
            print(f"  - First commande: {data[0]['numero_commande']}")
        test_results["commandes"]["list"]["success"] = True
        test_results["commandes"]["list"]["message"] = f"Successfully retrieved {len(data)} commandes"
        return True
    else:
        print_test_result("Get commandes", False, message)
        test_results["commandes"]["list"]["message"] = message
        return False

def test_alertes(token):
    print_header("Testing Alertes API")
    success, message, data = make_request("get", "/alertes", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get alertes", True, f"Retrieved {len(data)} alertes")
        if len(data) > 0:
            print(f"  - First alerte: {data[0]['titre']}")
        test_results["alertes"]["list"]["success"] = True
        test_results["alertes"]["list"]["message"] = f"Successfully retrieved {len(data)} alertes"
        return True
    else:
        print_test_result("Get alertes", False, message)
        test_results["alertes"]["list"]["message"] = message
        return False

def check_mongodb_status():
    print_header("Checking MongoDB Status")
    try:
        # We'll use the login endpoint as a proxy to check if MongoDB is working
        # If login works, MongoDB is operational
        success, message, data = make_request("post", "/auth/login", ADMIN_USER, expected_status=200)
        
        if success and data and "access_token" in data:
            print_test_result("MongoDB status", True, "MongoDB is operational")
            return True
        else:
            print_test_result("MongoDB status", False, "MongoDB might be down or not responding correctly")
            return False
    except Exception as e:
        print_test_result("MongoDB status", False, f"Error checking MongoDB status: {str(e)}")
        return False

def print_summary():
    print("\n" + "=" * 80)
    print(" TEST SUMMARY ".center(80, "="))
    print("=" * 80)
    
    all_passed = True
    
    for category, tests in test_results.items():
        print(f"\n{category.upper()}:")
        for test_name, result in tests.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            print(f"  - {test_name}: {status}")
            if not result["success"]:
                all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print(" ALL TESTS PASSED SUCCESSFULLY ".center(80, "="))
    else:
        print(" SOME TESTS FAILED ".center(80, "="))
    print("=" * 80 + "\n")

def run_tests():
    print_header("STARTING BACKEND API TESTS AFTER DARK MODE CHANGES")
    
    # Check MongoDB status
    mongodb_ok = check_mongodb_status()
    if not mongodb_ok:
        print("MongoDB appears to be down or not responding correctly. Skipping further tests.")
        return
    
    # Login to get token
    token = test_auth_login()
    if not token:
        print("Authentication failed. Cannot proceed with API tests.")
        return
    
    # Test authentication endpoint
    test_auth_me(token)
    
    # Test dashboard stats
    test_dashboard_stats(token)
    
    # Test main APIs
    test_fournisseurs(token)
    test_articles(token)
    test_commandes(token)
    test_alertes(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_tests()