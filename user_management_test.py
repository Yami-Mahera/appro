import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "admin123"
}

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

def login():
    print_header("Authenticating")
    login_data = {
        "email": ADMIN_CREDENTIALS["email"],
        "password": ADMIN_CREDENTIALS["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Login", True, f"Logged in as: {ADMIN_CREDENTIALS['email']}")
        return data["access_token"]
    else:
        print_test_result("Login", False, message)
        return None

def test_create_user(token):
    print_header("Testing Create User")
    
    # Generate a unique email to avoid conflicts
    unique_id = uuid.uuid4().hex[:6]
    user_data = {
        "email": f"test.user.{unique_id}@example.com",
        "password": "Password123!",
        "nom": "Test User",
        "prenom": f"User {unique_id}",
        "role": "utilisateur"
    }
    
    success, message, data = make_request("post", "/users", user_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Create user", True, f"Created user: {data['email']} with role {data['role']}")
        return data["id"]
    else:
        print_test_result("Create user", False, message)
        return None

def test_get_user(token, user_id):
    print_header("Testing Get User")
    success, message, data = make_request("get", f"/users/{user_id}", token=token, expected_status=200)
    
    if success and data and data["id"] == user_id:
        print_test_result("Get user", True, f"Retrieved user: {data['email']}")
        return True
    else:
        print_test_result("Get user", False, message)
        return False

def test_update_user(token, user_id):
    print_header("Testing Update User")
    update_data = {
        "nom": f"Updated Name {uuid.uuid4().hex[:6]}",
        "prenom": f"Updated Firstname {uuid.uuid4().hex[:6]}"
    }
    
    success, message, data = make_request("put", f"/users/{user_id}", update_data, token=token, expected_status=200)
    
    if success and data and data["nom"] == update_data["nom"]:
        print_test_result("Update user", True, f"Updated user: {data['email']}")
        return True
    else:
        print_test_result("Update user", False, message)
        return False

def test_reset_user_password(token, user_id):
    print_header("Testing Reset User Password")
    password_data = {
        "new_password": "NewPassword123!"
    }
    
    success, message, data = make_request("put", f"/users/{user_id}/reset-password", password_data, token=token, expected_status=200)
    
    if success:
        print_test_result("Reset user password", True, "Password reset successful")
        return True
    else:
        print_test_result("Reset user password", False, message)
        return False

def test_delete_user(token, user_id):
    print_header("Testing Delete User")
    success, message, data = make_request("delete", f"/users/{user_id}", token=token, expected_status=200)
    
    if success:
        print_test_result("Delete user", True, "User deleted successfully")
        return True
    else:
        print_test_result("Delete user", False, message)
        return False

def run_tests():
    print_header("STARTING USER MANAGEMENT API TESTS")
    
    # Login to get token
    token = login()
    if not token:
        print("Authentication failed. Cannot proceed with tests.")
        return
    
    # Test user creation
    user_id = test_create_user(token)
    if not user_id:
        print("Failed to create test user. Cannot proceed with further tests.")
        return
    
    # Test getting user details
    test_get_user(token, user_id)
    
    # Test updating user
    test_update_user(token, user_id)
    
    # Test resetting user password
    test_reset_user_password(token, user_id)
    
    # Test deleting user
    test_delete_user(token, user_id)
    
    print_header("USER MANAGEMENT API TESTS COMPLETED")

if __name__ == "__main__":
    run_tests()