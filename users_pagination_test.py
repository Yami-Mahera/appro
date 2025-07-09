import requests
import json
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

def test_auth_login(user_data):
    print_header("Testing User Login")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Login user", True, f"Logged in as: {user_data['email']}")
        return data["access_token"]
    else:
        print_test_result("Login user", False, message)
        return None

def test_auth_register(user_data):
    print_header("Testing User Registration")
    success, message, data = make_request("post", "/auth/register", user_data, expected_status=200)
    
    if success:
        print_test_result("Register user", True, f"Created user: {user_data['email']}")
        return True
    else:
        print_test_result("Register user", False, message)
        return False

def create_test_users(token, count=15):
    print_header(f"Creating {count} Test Users for Pagination Testing")
    created_users = []
    
    for i in range(count):
        # Alternate between different roles
        role = "utilisateur"
        if i % 5 == 0:
            role = "manager"
        elif i % 7 == 0:
            role = "administrateur"
            
        unique_id = uuid.uuid4().hex[:6]
        user_data = {
            "email": f"pagination.user{i+1}.{unique_id}@example.com",
            "password": "Password123!",
            "nom": f"Pagination User {i+1}",
            "prenom": f"Test {i+1}",
            "role": role
        }
        
        success, message, data = make_request("post", "/users", user_data, token=token, expected_status=200)
        if success and data and "id" in data:
            print(f"Created user: {data['email']} with role {data['role']}")
            created_users.append(data)
    
    print(f"Successfully created {len(created_users)} test users")
    return created_users

def test_users_pagination(token):
    print_header("TESTING USERS PAGINATION API")
    
    # Check if we need to create test data
    print("\n--- Checking if we need to create test data ---")
    success, message, users_data = make_request("get", "/users", token=token, expected_status=200)
    
    if not success:
        print("❌ Failed to retrieve users. Cannot proceed with pagination tests.")
        print(f"   Error: {message}")
        return False
    
    # Check if the response has the expected structure with pagination
    if isinstance(users_data, dict) and "users" in users_data and "total" in users_data:
        print("✅ Users API returns paginated response with metadata")
        print(f"   Found {users_data['total']} total users, {len(users_data['users'])} in current page")
        
        # Create more test users if needed
        if users_data['total'] < 15:
            print(f"Creating additional test users for pagination testing...")
            create_test_users(token, 15 - users_data['total'])
    else:
        print("❌ Users API does not return paginated response with metadata")
        print("   Creating test users and proceeding with tests...")
        create_test_users(token, 15)
    
    # Test 1: GET /api/users with pagination parameters (limit=5, skip=0)
    print("\n--- Test 1: GET /api/users?limit=5&skip=0 ---")
    success, message, data = make_request("get", "/users?limit=5&skip=0", token=token, expected_status=200)
    
    if success and isinstance(data, dict) and "users" in data:
        print(f"✅ Successfully retrieved users with limit=5, skip=0")
        print(f"   Response contains {len(data['users'])} users")
        
        # Check if pagination metadata is present
        pagination_fields = ["total", "limit", "skip", "has_next", "has_previous"]
        missing_fields = [field for field in pagination_fields if field not in data]
        
        if not missing_fields:
            print("✅ Response includes all required pagination metadata fields")
            print(f"   total: {data['total']}, limit: {data['limit']}, skip: {data['skip']}")
            print(f"   has_next: {data['has_next']}, has_previous: {data['has_previous']}")
        else:
            print(f"❌ Response is missing pagination metadata fields: {', '.join(missing_fields)}")
            return False
        
        if len(data['users']) == 5:
            print("✅ Correct number of users returned (5)")
        else:
            print(f"❌ Incorrect number of users returned: {len(data['users'])} (expected 5)")
        
        # Store first page users for comparison with next page
        first_page_users = data['users']
    else:
        print(f"❌ Failed to retrieve users with limit=5, skip=0")
        print(f"   Error: {message}")
        return False
    
    # Test 2: GET /api/users with pagination parameters (limit=5, skip=5)
    print("\n--- Test 2: GET /api/users?limit=5&skip=5 ---")
    success, message, data = make_request("get", "/users?limit=5&skip=5", token=token, expected_status=200)
    
    if success and isinstance(data, dict) and "users" in data:
        print(f"✅ Successfully retrieved users with limit=5, skip=5")
        print(f"   Response contains {len(data['users'])} users")
        
        # Check pagination metadata
        if data['skip'] == 5:
            print("✅ Skip parameter is correctly set to 5")
        else:
            print(f"❌ Skip parameter is incorrect: {data['skip']} (expected 5)")
        
        if data['limit'] == 5:
            print("✅ Limit parameter is correctly set to 5")
        else:
            print(f"❌ Limit parameter is incorrect: {data['limit']} (expected 5)")
        
        # Check has_previous flag
        if data['has_previous']:
            print("✅ has_previous flag is correctly set to true")
        else:
            print("❌ has_previous flag is incorrectly set to false")
        
        # Check if users are different from first page
        if first_page_users and len(data['users']) > 0:
            first_page_ids = [user["id"] for user in first_page_users]
            second_page_ids = [user["id"] for user in data['users']]
            
            overlap = set(first_page_ids).intersection(set(second_page_ids))
            if not overlap:
                print("✅ No overlap between first and second page - pagination working correctly")
            else:
                print(f"❌ Found {len(overlap)} overlapping users between pages - pagination may not be working correctly")
    else:
        print(f"❌ Failed to retrieve users with limit=5, skip=5")
        print(f"   Error: {message}")
        return False
    
    # Test 3: GET /api/users with search and pagination
    print("\n--- Test 3: GET /api/users?search=pagination&limit=5&skip=0 ---")
    success, message, data = make_request("get", "/users?search=pagination&limit=5&skip=0", token=token, expected_status=200)
    
    if success and isinstance(data, dict) and "users" in data:
        print(f"✅ Successfully retrieved users with search=pagination, limit=5, skip=0")
        print(f"   Response contains {len(data['users'])} users")
        print(f"   Total matching users: {data['total']}")
        
        # Check if search worked
        search_term_found = any("pagination" in user["nom"].lower() or 
                               "pagination" in user["prenom"].lower() or
                               "pagination" in user["email"].lower()
                               for user in data['users'])
        
        if search_term_found or len(data['users']) == 0:
            print("✅ Search functionality working correctly with pagination")
        else:
            print("❌ Search may not be working correctly with pagination")
    else:
        print(f"❌ Failed to retrieve users with search and pagination")
        print(f"   Error: {message}")
        return False
    
    # Test 4: GET /api/users with role filter and pagination
    print("\n--- Test 4: GET /api/users?role=manager&limit=5&skip=0 ---")
    success, message, data = make_request("get", "/users?role=manager&limit=5&skip=0", token=token, expected_status=200)
    
    if success and isinstance(data, dict) and "users" in data:
        print(f"✅ Successfully retrieved users with role=manager, limit=5, skip=0")
        print(f"   Response contains {len(data['users'])} users")
        print(f"   Total matching users: {data['total']}")
        
        # Check if role filter worked
        all_managers = all(user["role"] == "manager" for user in data['users'])
        
        if all_managers or len(data['users']) == 0:
            print("✅ Role filter working correctly with pagination")
        else:
            print("❌ Role filter may not be working correctly with pagination")
    else:
        print(f"❌ Failed to retrieve users with role filter and pagination")
        print(f"   Error: {message}")
        return False
    
    # Test 5: GET /api/users with active filter and pagination
    print("\n--- Test 5: GET /api/users?active=true&limit=5&skip=0 ---")
    success, message, data = make_request("get", "/users?active=true&limit=5&skip=0", token=token, expected_status=200)
    
    if success and isinstance(data, dict) and "users" in data:
        print(f"✅ Successfully retrieved users with active=true, limit=5, skip=0")
        print(f"   Response contains {len(data['users'])} users")
        print(f"   Total matching users: {data['total']}")
        
        # Check if active filter worked
        all_active = all(user["active"] for user in data['users'])
        
        if all_active or len(data['users']) == 0:
            print("✅ Active filter working correctly with pagination")
        else:
            print("❌ Active filter may not be working correctly with pagination")
    else:
        print(f"❌ Failed to retrieve users with active filter and pagination")
        print(f"   Error: {message}")
        return False
    
    # Test 6: Test has_next and has_previous flags
    print("\n--- Test 6: Testing has_next and has_previous flags ---")
    
    # Get total count
    success, message, data = make_request("get", "/users?limit=1&skip=0", token=token, expected_status=200)
    if success and isinstance(data, dict) and "total" in data:
        total_users = data["total"]
        print(f"Total users: {total_users}")
        
        # Test first page
        success, message, data = make_request("get", f"/users?limit=5&skip=0", token=token, expected_status=200)
        if success and isinstance(data, dict):
            if not data["has_previous"]:
                print("✅ First page has_previous is correctly false")
            else:
                print("❌ First page has_previous is incorrectly true")
                
            expected_has_next = total_users > 5
            if data["has_next"] == expected_has_next:
                print(f"✅ First page has_next is correctly {expected_has_next}")
            else:
                print(f"❌ First page has_next is incorrectly {data['has_next']}, expected {expected_has_next}")
        
        # Test middle page
        if total_users > 10:
            success, message, data = make_request("get", f"/users?limit=5&skip=5", token=token, expected_status=200)
            if success and isinstance(data, dict):
                if data["has_previous"]:
                    print("✅ Middle page has_previous is correctly true")
                else:
                    print("❌ Middle page has_previous is incorrectly false")
                    
                expected_has_next = total_users > 10
                if data["has_next"] == expected_has_next:
                    print(f"✅ Middle page has_next is correctly {expected_has_next}")
                else:
                    print(f"❌ Middle page has_next is incorrectly {data['has_next']}, expected {expected_has_next}")
        
        # Test last page
        last_page_skip = (total_users // 5) * 5
        if last_page_skip > 0:
            success, message, data = make_request("get", f"/users?limit=5&skip={last_page_skip}", token=token, expected_status=200)
            if success and isinstance(data, dict):
                if data["has_previous"]:
                    print("✅ Last page has_previous is correctly true")
                else:
                    print("❌ Last page has_previous is incorrectly false")
                    
                if not data["has_next"] or (total_users % 5 == 0 and data["has_next"]):
                    print("✅ Last page has_next is correctly set")
                else:
                    print(f"❌ Last page has_next is incorrectly {data['has_next']}")
    
    print("\n--- USERS PAGINATION TESTS COMPLETED ---")
    return True

def main():
    print_header("TESTING USERS PAGINATION API")
    
    # First, authenticate to get a token
    print("Authenticating to get access token...")
    admin_token = test_auth_login(ADMIN_USER)
    
    if not admin_token:
        print("❌ Authentication failed. Cannot proceed with users pagination tests.")
        print("Trying to register a new admin user...")
        
        # Try to register a new admin user
        admin_registered = test_auth_register(ADMIN_USER)
        if admin_registered:
            admin_token = test_auth_login(ADMIN_USER)
        else:
            print("❌ Failed to register admin user. Cannot proceed with users pagination tests.")
            return False
    
    print("✅ Authentication successful. Proceeding with users pagination tests.")
    
    # Test users pagination
    test_users_pagination(admin_token)
    
    return True

if __name__ == "__main__":
    main()