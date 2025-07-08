import requests
import json
import time
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://0095ed36-defa-4846-8f0c-28de1ed45b2c.preview.emergentagent.com/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123",
    "nom": "Admin",
    "prenom": "Test",
    "role": "administrateur"
}
MANAGER_USER = {
    "email": "manager@test.com",
    "password": "password123",
    "nom": "Manager",
    "prenom": "Test",
    "role": "manager"
}
NORMAL_USER = {
    "email": "user@test.com",
    "password": "password123",
    "nom": "User",
    "prenom": "Test",
    "role": "utilisateur"
}

# Test data
test_fournisseur = {
    "nom": "Fournisseur Test",
    "code_fournisseur": f"FOUR-{uuid.uuid4().hex[:6]}",
    "adresse": "123 Rue de Test",
    "ville": "Paris",
    "code_postal": "75001",
    "pays": "France",
    "telephone": "+33123456789",
    "email": f"contact_{uuid.uuid4().hex[:6]}@fournisseur-test.com",
    "site_web": "https://www.fournisseur-test.com",
    "conditions_paiement": "30 jours",
    "delai_livraison_moyen": 5,
    "contacts": [
        {
            "nom": "Dupont",
            "prenom": "Jean",
            "telephone": "+33612345678",
            "email": f"jean.dupont_{uuid.uuid4().hex[:6]}@fournisseur-test.com",
            "poste": "Responsable commercial"
        }
    ]
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

def test_commandes_pagination():
    print_header("TESTING COMMANDES PAGINATION API")
    
    # First, authenticate to get a token
    print("Authenticating to get access token...")
    admin_token = test_auth_login(ADMIN_USER)
    
    if not admin_token:
        print("❌ Authentication failed. Cannot proceed with commandes pagination tests.")
        print("Trying to register a new admin user...")
        
        # Try to register a new admin user
        admin_registered = test_auth_register(ADMIN_USER)
        if admin_registered:
            admin_token = test_auth_login(ADMIN_USER)
        else:
            print("❌ Failed to register admin user. Cannot proceed with commandes pagination tests.")
            return False
    
    print("✅ Authentication successful. Proceeding with commandes pagination tests.")
    
    # Create test data if needed
    print("\n--- Checking if we need to create test data ---")
    success, message, commandes_data = make_request("get", "/commandes", token=admin_token, expected_status=200)
    
    if not success:
        print("❌ Failed to retrieve commandes. Cannot proceed with pagination tests.")
        print(f"   Error: {message}")
        return False
    
    # Check if we have enough commandes for pagination testing
    if isinstance(commandes_data, dict) and "commandes" in commandes_data:
        commandes_count = len(commandes_data["commandes"])
        total_commandes = commandes_data.get("total", 0)
        print(f"Found {commandes_count} commandes in the response, total: {total_commandes}")
        
        # Create test data if we don't have enough commandes
        if total_commandes < 15:
            print("Creating additional test commandes for pagination testing...")
            
            # First, we need a fournisseur
            success, message, fournisseurs_data = make_request("get", "/fournisseurs", token=admin_token, expected_status=200)
            fournisseur_id = None
            
            if success and isinstance(fournisseurs_data, dict) and "fournisseurs" in fournisseurs_data and len(fournisseurs_data["fournisseurs"]) > 0:
                fournisseur_id = fournisseurs_data["fournisseurs"][0]["id"]
            else:
                # Create a fournisseur
                success, message, fournisseur_data = make_request("post", "/fournisseurs", test_fournisseur, token=admin_token, expected_status=200)
                if success and "id" in fournisseur_data:
                    fournisseur_id = fournisseur_data["id"]
                else:
                    print("❌ Failed to create a fournisseur for test commandes.")
                    return False
            
            # Now, we need an article
            success, message, articles_data = make_request("get", "/articles", token=admin_token, expected_status=200)
            article_id = None
            
            if success and isinstance(articles_data, dict) and "articles" in articles_data and len(articles_data["articles"]) > 0:
                article_id = articles_data["articles"][0]["id"]
            else:
                # Create an article
                article_data = {
                    "reference": f"ART-{uuid.uuid4().hex[:6]}",
                    "nom": "Article Test",
                    "description": "Description de l'article test",
                    "famille": "Test",
                    "fournisseur_id": fournisseur_id,
                    "prix_unitaire": 19.99,
                    "unite": "pièce",
                    "seuil_min": 10,
                    "seuil_max": 100,
                    "stock_actuel": 5,
                    "duree_vie": 365,
                    "emplacement_stockage": "Étagère A1"
                }
                
                success, message, article_data = make_request("post", "/articles", article_data, token=admin_token, expected_status=200)
                if success and "id" in article_data:
                    article_id = article_data["id"]
                else:
                    print("❌ Failed to create an article for test commandes.")
                    return False
            
            # Create 15 commandes
            for i in range(15):
                commande_data = {
                    "fournisseur_id": fournisseur_id,
                    "lignes": [
                        {
                            "article_id": article_id,
                            "quantite": 10 + i,
                            "prix_unitaire": 19.99,
                            "total": (10 + i) * 19.99
                        }
                    ],
                    "date_livraison_prevue": (datetime.now() + timedelta(days=7 + i)).isoformat(),
                    "notes": f"Commande test pagination {i+1}"
                }
                
                success, message, data = make_request("post", "/commandes", commande_data, token=admin_token, expected_status=200)
                if success and "id" in data:
                    print(f"Created commande {i+1}: {data['numero_commande']}")
                else:
                    print(f"❌ Failed to create commande {i+1}.")
                    print(f"   Error: {message}")
    
    # Test 1: GET /api/commandes with default pagination (limit=10, skip=0)
    print("\n--- Test 1: GET /api/commandes (default pagination) ---")
    success, message, data = make_request("get", "/commandes", token=admin_token, expected_status=200)
    
    if success and isinstance(data, dict):
        print(f"✅ Successfully retrieved commandes with default pagination")
        
        # Check if the response has the expected structure
        if "commandes" in data and "total" in data and "limit" in data and "skip" in data and "has_next" in data and "has_previous" in data:
            print("✅ Response has the expected structure with pagination metadata")
            print(f"   Total: {data['total']}, Limit: {data['limit']}, Skip: {data['skip']}")
            print(f"   Has Next: {data['has_next']}, Has Previous: {data['has_previous']}")
            print(f"   Commandes returned: {len(data['commandes'])}")
            
            # Check if the number of commandes matches the limit
            if len(data['commandes']) <= data['limit']:
                print(f"✅ Number of commandes ({len(data['commandes'])}) is less than or equal to the limit ({data['limit']})")
            else:
                print(f"❌ Number of commandes ({len(data['commandes'])}) exceeds the limit ({data['limit']})")
            
            # Check if has_previous is correct
            if data['skip'] == 0 and data['has_previous'] == False:
                print("✅ has_previous is correctly set to False for the first page")
            elif data['skip'] > 0 and data['has_previous'] == True:
                print("✅ has_previous is correctly set to True for non-first pages")
            else:
                print(f"❌ has_previous ({data['has_previous']}) is incorrect for skip={data['skip']}")
            
            # Check if has_next is correct
            if data['skip'] + data['limit'] < data['total'] and data['has_next'] == True:
                print("✅ has_next is correctly set to True when there are more results")
            elif data['skip'] + data['limit'] >= data['total'] and data['has_next'] == False:
                print("✅ has_next is correctly set to False when there are no more results")
            else:
                print(f"❌ has_next ({data['has_next']}) is incorrect for skip={data['skip']}, limit={data['limit']}, total={data['total']}")
            
            # Store first page commandes for comparison
            first_page_commandes = data['commandes']
        else:
            print("❌ Response does not have the expected structure with pagination metadata")
            print(f"   Response keys: {list(data.keys())}")
            return False
    else:
        print(f"❌ Failed to retrieve commandes with default pagination")
        print(f"   Error: {message}")
        return False
    
    # Test 2: GET /api/commandes with custom pagination (limit=5, skip=0)
    print("\n--- Test 2: GET /api/commandes?limit=5&skip=0 ---")
    success, message, data = make_request("get", "/commandes?limit=5&skip=0", token=admin_token, expected_status=200)
    
    if success and isinstance(data, dict) and "commandes" in data:
        print(f"✅ Successfully retrieved commandes with limit=5, skip=0")
        print(f"   Commandes returned: {len(data['commandes'])}")
        
        # Check if the number of commandes matches the limit
        if len(data['commandes']) <= 5:
            print(f"✅ Number of commandes ({len(data['commandes'])}) is less than or equal to the limit (5)")
        else:
            print(f"❌ Number of commandes ({len(data['commandes'])}) exceeds the limit (5)")
        
        # Store first page custom limit commandes for comparison
        custom_first_page = data['commandes']
    else:
        print(f"❌ Failed to retrieve commandes with limit=5, skip=0")
        print(f"   Error: {message}")
        return False
    
    # Test 3: GET /api/commandes with pagination (limit=5, skip=5)
    print("\n--- Test 3: GET /api/commandes?limit=5&skip=5 ---")
    success, message, data = make_request("get", "/commandes?limit=5&skip=5", token=admin_token, expected_status=200)
    
    if success and isinstance(data, dict) and "commandes" in data:
        print(f"✅ Successfully retrieved commandes with limit=5, skip=5")
        print(f"   Commandes returned: {len(data['commandes'])}")
        
        # Check if the number of commandes matches the limit
        if len(data['commandes']) <= 5:
            print(f"✅ Number of commandes ({len(data['commandes'])}) is less than or equal to the limit (5)")
        else:
            print(f"❌ Number of commandes ({len(data['commandes'])}) exceeds the limit (5)")
        
        # Check if has_previous is correct
        if data['has_previous'] == True:
            print("✅ has_previous is correctly set to True for skip=5")
        else:
            print(f"❌ has_previous ({data['has_previous']}) is incorrect for skip=5")
        
        # Check if commandes are different from first page
        if custom_first_page and len(data['commandes']) > 0:
            first_page_ids = [commande["id"] for commande in custom_first_page]
            second_page_ids = [commande["id"] for commande in data['commandes']]
            
            overlap = set(first_page_ids).intersection(set(second_page_ids))
            if not overlap:
                print("✅ No overlap between first and second page - pagination working correctly")
            else:
                print(f"❌ Found {len(overlap)} overlapping commandes between pages - pagination may not be working correctly")
    else:
        print(f"❌ Failed to retrieve commandes with limit=5, skip=5")
        print(f"   Error: {message}")
        return False
    
    # Test 4: GET /api/commandes with search and pagination
    print("\n--- Test 4: GET /api/commandes?search=test&limit=5&skip=0 ---")
    success, message, data = make_request("get", "/commandes?search=test&limit=5&skip=0", token=admin_token, expected_status=200)
    
    if success and isinstance(data, dict) and "commandes" in data:
        print(f"✅ Successfully retrieved commandes with search=test, limit=5, skip=0")
        print(f"   Commandes returned: {len(data['commandes'])}")
        print(f"   Total matching search: {data['total']}")
        
        # Check if the number of commandes matches the limit
        if len(data['commandes']) <= 5:
            print(f"✅ Number of commandes ({len(data['commandes'])}) is less than or equal to the limit (5)")
        else:
            print(f"❌ Number of commandes ({len(data['commandes'])}) exceeds the limit (5)")
        
        # Check if search worked
        if len(data['commandes']) > 0:
            search_term_found = any("test" in commande.get("notes", "").lower() or 
                                   "test" in commande.get("numero_commande", "").lower()
                                   for commande in data['commandes'])
            
            if search_term_found:
                print("✅ Search functionality working correctly with pagination")
            else:
                print("❌ Search may not be working correctly with pagination")
        else:
            print("ℹ️ No commandes found matching the search term")
    else:
        print(f"❌ Failed to retrieve commandes with search and pagination")
        print(f"   Error: {message}")
        return False
    
    # Test 5: GET /api/commandes with status filter and pagination
    print("\n--- Test 5: GET /api/commandes?status=brouillon&limit=5&skip=0 ---")
    success, message, data = make_request("get", "/commandes?status=brouillon&limit=5&skip=0", token=admin_token, expected_status=200)
    
    if success and isinstance(data, dict) and "commandes" in data:
        print(f"✅ Successfully retrieved commandes with status=brouillon, limit=5, skip=0")
        print(f"   Commandes returned: {len(data['commandes'])}")
        print(f"   Total matching status: {data['total']}")
        
        # Check if all commandes have the correct status
        if len(data['commandes']) > 0:
            all_match_status = all(commande.get("status") == "brouillon" for commande in data['commandes'])
            
            if all_match_status:
                print("✅ Status filter working correctly with pagination")
            else:
                print("❌ Status filter may not be working correctly with pagination")
        else:
            print("ℹ️ No commandes found with status=brouillon")
    else:
        print(f"❌ Failed to retrieve commandes with status filter and pagination")
        print(f"   Error: {message}")
        return False
    
    # Test 6: GET /api/commandes with fournisseur_id filter and pagination
    if len(first_page_commandes) > 0:
        fournisseur_id = first_page_commandes[0]["fournisseur_id"]
        print(f"\n--- Test 6: GET /api/commandes?fournisseur_id={fournisseur_id}&limit=5&skip=0 ---")
        success, message, data = make_request("get", f"/commandes?fournisseur_id={fournisseur_id}&limit=5&skip=0", token=admin_token, expected_status=200)
        
        if success and isinstance(data, dict) and "commandes" in data:
            print(f"✅ Successfully retrieved commandes with fournisseur_id filter, limit=5, skip=0")
            print(f"   Commandes returned: {len(data['commandes'])}")
            print(f"   Total matching fournisseur_id: {data['total']}")
            
            # Check if all commandes have the correct fournisseur_id
            if len(data['commandes']) > 0:
                all_match_fournisseur = all(commande.get("fournisseur_id") == fournisseur_id for commande in data['commandes'])
                
                if all_match_fournisseur:
                    print("✅ Fournisseur_id filter working correctly with pagination")
                else:
                    print("❌ Fournisseur_id filter may not be working correctly with pagination")
            else:
                print("ℹ️ No commandes found with the specified fournisseur_id")
        else:
            print(f"❌ Failed to retrieve commandes with fournisseur_id filter and pagination")
            print(f"   Error: {message}")
            return False
    
    # Test 7: GET /api/commandes with date range filter and pagination
    print("\n--- Test 7: GET /api/commandes with date range filter and pagination ---")
    date_from = (datetime.now() - timedelta(days=30)).isoformat()
    date_to = datetime.now().isoformat()
    
    success, message, data = make_request("get", f"/commandes?date_from={date_from}&date_to={date_to}&limit=5&skip=0", token=admin_token, expected_status=200)
    
    if success and isinstance(data, dict) and "commandes" in data:
        print(f"✅ Successfully retrieved commandes with date range filter, limit=5, skip=0")
        print(f"   Commandes returned: {len(data['commandes'])}")
        print(f"   Total matching date range: {data['total']}")
        
        # We can't easily verify the date filter without parsing the dates in the response
        # But we can check if the pagination metadata is correct
        if "total" in data and "limit" in data and "skip" in data and "has_next" in data and "has_previous" in data:
            print("✅ Response has the expected pagination metadata with date range filter")
        else:
            print("❌ Response does not have the expected pagination metadata with date range filter")
    else:
        print(f"❌ Failed to retrieve commandes with date range filter and pagination")
        print(f"   Error: {message}")
        return False
    
    # Test 8: GET /api/commandes with sort_by and sort_order
    print("\n--- Test 8: GET /api/commandes?sort_by=created_at&sort_order=asc&limit=5&skip=0 ---")
    success, message, data = make_request("get", "/commandes?sort_by=created_at&sort_order=asc&limit=5&skip=0", token=admin_token, expected_status=200)
    
    if success and isinstance(data, dict) and "commandes" in data:
        print(f"✅ Successfully retrieved commandes with sort parameters, limit=5, skip=0")
        print(f"   Commandes returned: {len(data['commandes'])}")
        
        # Check if commandes are sorted by created_at in ascending order
        if len(data['commandes']) > 1:
            is_sorted = all(data['commandes'][i]["created_at"] <= data['commandes'][i+1]["created_at"] 
                           for i in range(len(data['commandes'])-1))
            
            if is_sorted:
                print("✅ Sort by created_at in ascending order working correctly")
            else:
                print("❌ Sort by created_at in ascending order may not be working correctly")
        else:
            print("ℹ️ Not enough commandes to verify sorting")
    else:
        print(f"❌ Failed to retrieve commandes with sort parameters and pagination")
        print(f"   Error: {message}")
        return False
    
    print("\n--- COMMANDES PAGINATION TESTS COMPLETED ---")
    return True

if __name__ == "__main__":
    test_commandes_pagination()