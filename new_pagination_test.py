import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://0095ed36-defa-4846-8f0c-28de1ed45b2c.preview.emergentagent.com/api"

def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_test_result(test_name, success, message=""):
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{test_name}: {status}")
    if message:
        print(f"  - {message}")

def login():
    print_header("Authenticating")
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            print_test_result("Login", True, f"Logged in as: {login_data['email']}")
            return data["access_token"]
    
    print_test_result("Login", False, f"Failed to login: {response.text}")
    return None

def test_fournisseurs_pagination(token):
    print_header("Testing Fournisseurs Pagination")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Basic pagination with limit and skip
    print("\nTest 1: GET /api/fournisseurs?limit=5&skip=0")
    response = requests.get(f"{BASE_URL}/fournisseurs?limit=5&skip=0", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Check if response has the expected structure
        if isinstance(data, dict) and "fournisseurs" in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information")
            
            # Check if the correct number of items is returned
            items = data["fournisseurs"]
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
            return False
    else:
        print_test_result("API request", False, f"Failed with status {response.status_code}: {response.text}")
        return False
    
    # Test 2: Second page
    print("\nTest 2: GET /api/fournisseurs?limit=5&skip=5")
    response = requests.get(f"{BASE_URL}/fournisseurs?limit=5&skip=5", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if response has the expected structure
        if isinstance(data, dict) and "fournisseurs" in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information")
            
            # Check if the correct number of items is returned
            items = data["fournisseurs"]
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
                first_page_ids = [item["id"] for item in first_page["fournisseurs"]]
                second_page_ids = [item["id"] for item in items]
                
                overlap = set(first_page_ids).intersection(set(second_page_ids))
                if not overlap:
                    print_test_result("Page content", True, "No overlap between first and second page")
                else:
                    print_test_result("Page content", False, f"Found {len(overlap)} overlapping items between pages")
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            return False
    else:
        print_test_result("API request", False, f"Failed with status {response.status_code}: {response.text}")
        return False
    
    # Test 3: Search with pagination
    print("\nTest 3: GET /api/fournisseurs?search=test&limit=5&skip=0")
    response = requests.get(f"{BASE_URL}/fournisseurs?search=test&limit=5&skip=0", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if response has the expected structure
        if isinstance(data, dict) and "fournisseurs" in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information with search")
            
            # Check if the correct number of items is returned
            items = data["fournisseurs"]
            if len(items) <= 5:
                print_test_result("Item count", True, f"Returned {len(items)} items (limit=5)")
            else:
                print_test_result("Item count", False, f"Returned {len(items)} items (expected ≤5)")
            
            # Check pagination fields
            print(f"Total: {data['total']}, Limit: {data['limit']}, Skip: {data['skip']}")
            print(f"Has next: {data['has_next']}, Has previous: {data['has_previous']}")
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            return False
    else:
        print_test_result("API request", False, f"Failed with status {response.status_code}: {response.text}")
        return False
    
    return True

def test_articles_pagination(token):
    print_header("Testing Articles Pagination")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Basic pagination with limit and skip
    print("\nTest 1: GET /api/articles?limit=5&skip=0")
    response = requests.get(f"{BASE_URL}/articles?limit=5&skip=0", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Check if response has the expected structure
        if isinstance(data, dict) and "articles" in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information")
            
            # Check if the correct number of items is returned
            items = data["articles"]
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
            return False
    else:
        print_test_result("API request", False, f"Failed with status {response.status_code}: {response.text}")
        return False
    
    # Test 2: Second page
    print("\nTest 2: GET /api/articles?limit=5&skip=5")
    response = requests.get(f"{BASE_URL}/articles?limit=5&skip=5", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if response has the expected structure
        if isinstance(data, dict) and "articles" in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information")
            
            # Check if the correct number of items is returned
            items = data["articles"]
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
                first_page_ids = [item["id"] for item in first_page["articles"]]
                second_page_ids = [item["id"] for item in items]
                
                overlap = set(first_page_ids).intersection(set(second_page_ids))
                if not overlap:
                    print_test_result("Page content", True, "No overlap between first and second page")
                else:
                    print_test_result("Page content", False, f"Found {len(overlap)} overlapping items between pages")
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            return False
    else:
        print_test_result("API request", False, f"Failed with status {response.status_code}: {response.text}")
        return False
    
    # Test 3: Search with pagination
    print("\nTest 3: GET /api/articles?search=test&limit=5&skip=0")
    response = requests.get(f"{BASE_URL}/articles?search=test&limit=5&skip=0", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Check if response has the expected structure
        if isinstance(data, dict) and "articles" in data and "total" in data and "limit" in data and "skip" in data:
            print_test_result("Response structure", True, "Response contains pagination information with search")
            
            # Check if the correct number of items is returned
            items = data["articles"]
            if len(items) <= 5:
                print_test_result("Item count", True, f"Returned {len(items)} items (limit=5)")
            else:
                print_test_result("Item count", False, f"Returned {len(items)} items (expected ≤5)")
            
            # Check pagination fields
            print(f"Total: {data['total']}, Limit: {data['limit']}, Skip: {data['skip']}")
            print(f"Has next: {data['has_next']}, Has previous: {data['has_previous']}")
        else:
            print_test_result("Response structure", False, "Response does not contain expected pagination information")
            return False
    else:
        print_test_result("API request", False, f"Failed with status {response.status_code}: {response.text}")
        return False
    
    return True

def run_tests():
    print_header("STARTING PAGINATION API TESTS")
    
    # Login to get token
    token = login()
    if not token:
        print("Authentication failed. Cannot proceed with tests.")
        return
    
    # Test fournisseurs pagination
    fournisseurs_result = test_fournisseurs_pagination(token)
    
    # Test articles pagination
    articles_result = test_articles_pagination(token)
    
    print_header("PAGINATION API TESTS SUMMARY")
    print_test_result("Fournisseurs Pagination", fournisseurs_result)
    print_test_result("Articles Pagination", articles_result)
    
    if fournisseurs_result and articles_result:
        print("\nAll pagination tests passed successfully!")
    else:
        print("\nSome pagination tests failed. See details above.")

if __name__ == "__main__":
    run_tests()