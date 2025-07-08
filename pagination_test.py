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

def create_test_data(token, entity_type, count=15):
    """Create test data for pagination testing"""
    print_header(f"Creating {count} test {entity_type} for pagination testing")
    
    created_ids = []
    
    if entity_type == "users":
        for i in range(count):
            # Alternate between different roles
            role = "utilisateur"
            if i % 5 == 0:
                role = "manager"
            elif i % 7 == 0:
                role = "administrateur"
                
            data = {
                "email": f"pagination.user{i+1}.{uuid.uuid4().hex[:6]}@example.com",
                "password": "Password123!",
                "nom": f"Pagination User {i+1}",
                "prenom": f"Test {i+1}",
                "role": role
            }
            success, message, response = make_request("post", f"/{entity_type}", data, token, expected_status=200)
            if success and response and "id" in response:
                created_ids.append(response["id"])
                print(f"Created {entity_type[:-1]} {i+1}/{count}: {response['email']}")
            else:
                print(f"Failed to create {entity_type[:-1]} {i+1}: {message}")
    
    elif entity_type == "fournisseurs":
        for i in range(count):
            data = {
                "nom": f"Pagination Test Supplier {i+1}",
                "code_fournisseur": f"PTS-{uuid.uuid4().hex[:6]}",
                "adresse": f"{i+1} Rue de Test",
                "ville": "Paris",
                "code_postal": "75001",
                "pays": "France",
                "telephone": f"+331234{i:05d}",
                "email": f"test{i+1}@pagination-test.com",
                "site_web": f"https://www.pagination-test-{i+1}.com",
                "conditions_paiement": "30 jours",
                "delai_livraison_moyen": i+1
            }
            success, message, response = make_request("post", f"/{entity_type}", data, token, expected_status=200)
            if success and response and "id" in response:
                created_ids.append(response["id"])
                print(f"Created {entity_type[:-1]} {i+1}/{count}: {response['nom']}")
            else:
                print(f"Failed to create {entity_type[:-1]} {i+1}: {message}")
    
    elif entity_type == "articles":
        # First get a supplier ID
        success, message, suppliers = make_request("get", "/fournisseurs", token, expected_status=200)
        if not success or not suppliers or not suppliers.get("fournisseurs") or len(suppliers["fournisseurs"]) == 0:
            print("No suppliers found. Creating a supplier first...")
            supplier_data = {
                "nom": "Test Supplier for Articles",
                "code_fournisseur": f"TSA-{uuid.uuid4().hex[:6]}",
                "adresse": "123 Test Street",
                "ville": "Paris",
                "code_postal": "75001",
                "pays": "France",
                "telephone": "+33123456789",
                "email": "test@supplier.com",
                "site_web": "https://www.test-supplier.com",
                "conditions_paiement": "30 jours",
                "delai_livraison_moyen": 5
            }
            success, message, response = make_request("post", "/fournisseurs", supplier_data, token, expected_status=200)
            if success and response and "id" in response:
                supplier_id = response["id"]
                print(f"Created supplier: {response['nom']}")
            else:
                print(f"Failed to create supplier: {message}")
                return []
        else:
            supplier_id = suppliers["fournisseurs"][0]["id"]
        
        for i in range(count):
            data = {
                "reference": f"PAG-{uuid.uuid4().hex[:6]}",
                "nom": f"Pagination Test Article {i+1}",
                "description": f"Test article for pagination {i+1}",
                "famille": "Test",
                "fournisseur_id": supplier_id,
                "prix_unitaire": 10.99 + i,
                "unite": "pièce",
                "seuil_min": 5,
                "seuil_max": 50,
                "stock_actuel": 10 + i,
                "duree_vie": 365,
                "emplacement_stockage": f"Étagère T{i+1}"
            }
            success, message, response = make_request("post", f"/{entity_type}", data, token, expected_status=200)
            if success and response and "id" in response:
                created_ids.append(response["id"])
                print(f"Created {entity_type[:-1]} {i+1}/{count}: {response['nom']}")
            else:
                print(f"Failed to create {entity_type[:-1]} {i+1}: {message}")
    
    return created_ids

def test_pagination_api(token, endpoint, entity_name):
    """Test pagination for a specific API endpoint"""
    print_header(f"Testing Pagination for {entity_name} API")
    
    # Test 1: Basic pagination with limit and skip
    print(f"\nTest 1: GET {endpoint}?limit=5&skip=0")
    success, message, data = make_request("get", f"{endpoint}?limit=5&skip=0", token=token, expected_status=200)
    
    if success and data:
        # Check if response has the expected structure
        if isinstance(data, dict) and entity_name in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information")
            
            # Check if the correct number of items is returned
            items = data[entity_name]
            if len(items) <= 5:
                print_test_result("Item count", True, f"Returned {len(items)} items (limit=5)")
            else:
                print_test_result("Item count", False, f"Returned {len(items)} items (expected ≤5)")
            
            # Check pagination fields
            print(f"Total: {data['total']}, Limit: {data['limit']}, Skip: {data['skip']}")
            print(f"Has next: {data['has_next']}, Has previous: {data['has_previous']}")
            
            # Verify has_previous is False for first page
            if data['skip'] == 0 and data['has_previous'] == False:
                print_test_result("has_previous flag", True, "has_previous is False for first page")
            else:
                print_test_result("has_previous flag", False, f"has_previous is {data['has_previous']} for first page (expected False)")
            
            # Store first page data for comparison
            first_page = data
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            print(f"Response: {data}")
            return False
    else:
        print_test_result("API request", False, message)
        return False
    
    # Test 2: Second page
    print(f"\nTest 2: GET {endpoint}?limit=5&skip=5")
    success, message, data = make_request("get", f"{endpoint}?limit=5&skip=5", token=token, expected_status=200)
    
    if success and data:
        # Check if response has the expected structure
        if isinstance(data, dict) and entity_name in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information")
            
            # Check if the correct number of items is returned
            items = data[entity_name]
            if len(items) <= 5:
                print_test_result("Item count", True, f"Returned {len(items)} items (limit=5)")
            else:
                print_test_result("Item count", False, f"Returned {len(items)} items (expected ≤5)")
            
            # Check pagination fields
            print(f"Total: {data['total']}, Limit: {data['limit']}, Skip: {data['skip']}")
            print(f"Has next: {data['has_next']}, Has previous: {data['has_previous']}")
            
            # Verify has_previous is True for second page
            if data['skip'] > 0 and data['has_previous'] == True:
                print_test_result("has_previous flag", True, "has_previous is True for second page")
            else:
                print_test_result("has_previous flag", False, f"has_previous is {data['has_previous']} for second page (expected True)")
            
            # Check if total count is consistent
            if data['total'] == first_page['total']:
                print_test_result("Total count consistency", True, f"Total count is consistent: {data['total']}")
            else:
                print_test_result("Total count consistency", False, f"Total count is inconsistent: {data['total']} vs {first_page['total']}")
            
            # Check if items are different from first page
            if first_page and len(items) > 0:
                first_page_ids = [item["id"] for item in first_page[entity_name]]
                second_page_ids = [item["id"] for item in items]
                
                overlap = set(first_page_ids).intersection(set(second_page_ids))
                if not overlap:
                    print_test_result("Page content", True, "No overlap between first and second page")
                else:
                    print_test_result("Page content", False, f"Found {len(overlap)} overlapping items between pages")
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            print(f"Response: {data}")
            return False
    else:
        print_test_result("API request", False, message)
        return False
    
    # Test 3: Search with pagination
    print(f"\nTest 3: GET {endpoint}?search=test&limit=5&skip=0")
    success, message, data = make_request("get", f"{endpoint}?search=test&limit=5&skip=0", token=token, expected_status=200)
    
    if success and data:
        # Check if response has the expected structure
        if isinstance(data, dict) and entity_name in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information with search")
            
            # Check if the correct number of items is returned
            items = data[entity_name]
            if len(items) <= 5:
                print_test_result("Item count", True, f"Returned {len(items)} items (limit=5)")
            else:
                print_test_result("Item count", False, f"Returned {len(items)} items (expected ≤5)")
            
            # Check pagination fields
            print(f"Total: {data['total']}, Limit: {data['limit']}, Skip: {data['skip']}")
            print(f"Has next: {data['has_next']}, Has previous: {data['has_previous']}")
            
            # Check if search worked (items should contain "test" in their name)
            if len(items) > 0:
                search_term_found = any("test" in item["nom"].lower() for item in items)
                if search_term_found:
                    print_test_result("Search functionality", True, "Search term found in results")
                else:
                    print_test_result("Search functionality", False, "Search term not found in results")
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            print(f"Response: {data}")
            return False
    else:
        print_test_result("API request", False, message)
        return False
    
    # Test 4: Last page (has_next should be False)
    # First, get the total count
    total_count = first_page['total']
    last_page_skip = max(0, total_count - 5)  # Ensure skip is not negative
    
    print(f"\nTest 4: GET {endpoint}?limit=5&skip={last_page_skip}")
    success, message, data = make_request("get", f"{endpoint}?limit=5&skip={last_page_skip}", token=token, expected_status=200)
    
    if success and data:
        # Check if response has the expected structure
        if isinstance(data, dict) and entity_name in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information")
            
            # Check if has_next is False for last page
            if data['has_next'] == False:
                print_test_result("has_next flag", True, "has_next is False for last page")
            else:
                print_test_result("has_next flag", False, f"has_next is {data['has_next']} for last page (expected False)")
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            print(f"Response: {data}")
            return False
    else:
        print_test_result("API request", False, message)
        return False
    
    return True

def run_tests():
    print_header("STARTING PAGINATION API TESTS")
    
    # Login to get token
    token = login()
    if not token:
        print("Authentication failed. Cannot proceed with tests.")
        return
    
    # Test users pagination
    test_pagination_api(token, "/users", "users")
    
    # Test fournisseurs pagination
    test_pagination_api(token, "/fournisseurs", "fournisseurs")
    
    # Test articles pagination
    test_pagination_api(token, "/articles", "articles")
    
    print_header("PAGINATION API TESTS COMPLETED")

if __name__ == "__main__":
    run_tests()