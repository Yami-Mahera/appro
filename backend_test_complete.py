import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://e7ff3110-a20a-49f6-83a2-e11e89d0803f.preview.emergentagent.com/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123",
    "nom": "Admin",
    "prenom": "Test",
    "role": "administrateur"
}
MANAGER_USER = {
    "email": "manager@test.com",
    "password": "manager123",
    "nom": "Manager",
    "prenom": "Test",
    "role": "manager"
}
NORMAL_USER = {
    "email": "user@test.com",
    "password": "user123",
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

# Test results
test_results = {
    "auth": {
        "register": {"success": False, "message": "Not tested"},
        "login": {"success": False, "message": "Not tested"},
        "me": {"success": False, "message": "Not tested"}
    },
    "fournisseurs": {
        "create": {"success": False, "message": "Not tested"},
        "list": {"success": False, "message": "Not tested"},
        "get": {"success": False, "message": "Not tested"},
        "update": {"success": False, "message": "Not tested"},
        "search": {"success": False, "message": "Not tested"},
        "sort": {"success": False, "message": "Not tested"},
        "filter": {"success": False, "message": "Not tested"}
    },
    "articles": {
        "create": {"success": False, "message": "Not tested"},
        "list": {"success": False, "message": "Not tested"},
        "stock_bas": {"success": False, "message": "Not tested"},
        "search": {"success": False, "message": "Not tested"},
        "sort": {"success": False, "message": "Not tested"},
        "filter": {"success": False, "message": "Not tested"}
    },
    "commandes": {
        "create": {"success": False, "message": "Not tested"},
        "list": {"success": False, "message": "Not tested"},
        "search": {"success": False, "message": "Not tested"},
        "sort": {"success": False, "message": "Not tested"},
        "filter": {"success": False, "message": "Not tested"},
        "date_filter": {"success": False, "message": "Not tested"}
    },
    "alertes": {
        "list": {"success": False, "message": "Not tested"},
        "marquer_lue": {"success": False, "message": "Not tested"}
    },
    "dashboard": {
        "stats": {"success": False, "message": "Not tested"}
    },
    "reports": {
        "fournisseurs": {"success": False, "message": "Not tested"},
        "articles": {"success": False, "message": "Not tested"},
        "commandes": {"success": False, "message": "Not tested"},
        "synthese": {"success": False, "message": "Not tested"}
    },
    "access_control": {
        "unauthorized": {"success": False, "message": "Not tested"},
        "role_based": {"success": False, "message": "Not tested"}
    }
}

# Tokens for authenticated requests
tokens = {
    "admin": None,
    "manager": None,
    "user": None
}

# IDs for created resources
created_ids = {
    "fournisseur": None,
    "article": None,
    "commande": None,
    "alerte": None
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

def make_request(method, endpoint, params=None, data=None, token=None, expected_status=200):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.lower() == "get":
            response = requests.get(url, params=params, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
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

# Test functions
def test_auth_register(user_data):
    print_header("Testing User Registration")
    success, message, data = make_request("post", "/auth/register", data=user_data, expected_status=200)
    
    if success:
        print_test_result("Register user", True, f"Created user: {user_data['email']}")
        test_results["auth"]["register"]["success"] = True
        test_results["auth"]["register"]["message"] = f"Successfully registered user: {user_data['email']}"
        return True
    else:
        print_test_result("Register user", False, message)
        test_results["auth"]["register"]["message"] = message
        return False

def test_auth_login(user_data):
    print_header("Testing User Login")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", data=login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Login user", True, f"Logged in as: {user_data['email']}")
        test_results["auth"]["login"]["success"] = True
        test_results["auth"]["login"]["message"] = f"Successfully logged in as: {user_data['email']}"
        
        # Store token for later use
        if user_data["role"] == "administrateur":
            tokens["admin"] = data["access_token"]
        elif user_data["role"] == "manager":
            tokens["manager"] = data["access_token"]
        else:
            tokens["user"] = data["access_token"]
            
        return data["access_token"]
    else:
        print_test_result("Login user", False, message)
        test_results["auth"]["login"]["message"] = message
        return None

def test_auth_me(token, expected_email):
    print_header("Testing Get Current User")
    success, message, data = make_request("get", "/auth/me", token=token, expected_status=200)
    
    if success and data and data.get("email") == expected_email:
        print_test_result("Get current user", True, f"Retrieved user: {data['email']}")
        test_results["auth"]["me"]["success"] = True
        test_results["auth"]["me"]["message"] = f"Successfully retrieved user info: {data['email']}"
        return True
    else:
        print_test_result("Get current user", False, message)
        test_results["auth"]["me"]["message"] = message
        return False

def test_create_fournisseur(token):
    print_header("Testing Create Fournisseur")
    success, message, data = make_request("post", "/fournisseurs", data=test_fournisseur, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Create fournisseur", True, f"Created fournisseur: {data['nom']}")
        test_results["fournisseurs"]["create"]["success"] = True
        test_results["fournisseurs"]["create"]["message"] = f"Successfully created fournisseur: {data['nom']}"
        created_ids["fournisseur"] = data["id"]
        return data["id"]
    else:
        print_test_result("Create fournisseur", False, message)
        test_results["fournisseurs"]["create"]["message"] = message
        return None

def test_list_fournisseurs(token):
    print_header("Testing List Fournisseurs")
    success, message, data = make_request("get", "/fournisseurs", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("List fournisseurs", True, f"Retrieved {len(data)} fournisseurs")
        test_results["fournisseurs"]["list"]["success"] = True
        test_results["fournisseurs"]["list"]["message"] = f"Successfully retrieved {len(data)} fournisseurs"
        return True
    else:
        print_test_result("List fournisseurs", False, message)
        test_results["fournisseurs"]["list"]["message"] = message
        return False

def test_get_fournisseur(token, fournisseur_id):
    print_header("Testing Get Fournisseur")
    success, message, data = make_request("get", f"/fournisseurs/{fournisseur_id}", token=token, expected_status=200)
    
    if success and data and data["id"] == fournisseur_id:
        print_test_result("Get fournisseur", True, f"Retrieved fournisseur: {data['nom']}")
        test_results["fournisseurs"]["get"]["success"] = True
        test_results["fournisseurs"]["get"]["message"] = f"Successfully retrieved fournisseur: {data['nom']}"
        return True
    else:
        print_test_result("Get fournisseur", False, message)
        test_results["fournisseurs"]["get"]["message"] = message
        return False

def test_update_fournisseur(token, fournisseur_id):
    print_header("Testing Update Fournisseur")
    updated_data = test_fournisseur.copy()
    updated_data["nom"] = f"Fournisseur Test Updated {uuid.uuid4().hex[:6]}"
    
    success, message, data = make_request("put", f"/fournisseurs/{fournisseur_id}", data=updated_data, token=token, expected_status=200)
    
    if success and data and data["nom"] == updated_data["nom"]:
        print_test_result("Update fournisseur", True, f"Updated fournisseur: {data['nom']}")
        test_results["fournisseurs"]["update"]["success"] = True
        test_results["fournisseurs"]["update"]["message"] = f"Successfully updated fournisseur: {data['nom']}"
        return True
    else:
        print_test_result("Update fournisseur", False, message)
        test_results["fournisseurs"]["update"]["message"] = message
        return False

def test_create_article(token, fournisseur_id):
    print_header("Testing Create Article")
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
        "stock_actuel": 5,  # Below seuil_min to test stock_bas
        "duree_vie": 365,
        "emplacement_stockage": "Étagère A1"
    }
    
    success, message, data = make_request("post", "/articles", data=article_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Create article", True, f"Created article: {data['nom']}")
        test_results["articles"]["create"]["success"] = True
        test_results["articles"]["create"]["message"] = f"Successfully created article: {data['nom']}"
        created_ids["article"] = data["id"]
        return data["id"]
    else:
        print_test_result("Create article", False, message)
        test_results["articles"]["create"]["message"] = message
        return None

def test_list_articles(token):
    print_header("Testing List Articles")
    success, message, data = make_request("get", "/articles", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("List articles", True, f"Retrieved {len(data)} articles")
        test_results["articles"]["list"]["success"] = True
        test_results["articles"]["list"]["message"] = f"Successfully retrieved {len(data)} articles"
        return True
    else:
        print_test_result("List articles", False, message)
        test_results["articles"]["list"]["message"] = message
        return False

def test_articles_stock_bas(token):
    print_header("Testing Articles Stock Bas")
    success, message, data = make_request("get", "/articles/stock-bas", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get articles stock bas", True, f"Retrieved {len(data)} articles with low stock")
        test_results["articles"]["stock_bas"]["success"] = True
        test_results["articles"]["stock_bas"]["message"] = f"Successfully retrieved {len(data)} articles with low stock"
        return True
    else:
        print_test_result("Get articles stock bas", False, message)
        test_results["articles"]["stock_bas"]["message"] = message
        return False

def test_create_commande(token, fournisseur_id, article_id):
    print_header("Testing Create Commande")
    commande_data = {
        "fournisseur_id": fournisseur_id,
        "lignes": [
            {
                "article_id": article_id,
                "quantite": 10,
                "prix_unitaire": 19.99,
                "total": 199.90
            }
        ],
        "date_livraison_prevue": (datetime.now() + timedelta(days=7)).isoformat(),
        "notes": "Commande test"
    }
    
    success, message, data = make_request("post", "/commandes", data=commande_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Create commande", True, f"Created commande: {data['numero_commande']}")
        test_results["commandes"]["create"]["success"] = True
        test_results["commandes"]["create"]["message"] = f"Successfully created commande: {data['numero_commande']}"
        created_ids["commande"] = data["id"]
        return data["id"]
    else:
        print_test_result("Create commande", False, message)
        test_results["commandes"]["create"]["message"] = message
        return None

def test_list_commandes(token):
    print_header("Testing List Commandes")
    success, message, data = make_request("get", "/commandes", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("List commandes", True, f"Retrieved {len(data)} commandes")
        test_results["commandes"]["list"]["success"] = True
        test_results["commandes"]["list"]["message"] = f"Successfully retrieved {len(data)} commandes"
        return True
    else:
        print_test_result("List commandes", False, message)
        test_results["commandes"]["list"]["message"] = message
        return False

def test_list_alertes(token):
    print_header("Testing List Alertes")
    
    # First, create an alert for testing
    if created_ids["article"]:
        alerte_data = {
            "type": "stock_bas",
            "priorite": "high",
            "titre": "Stock bas pour article test",
            "message": "Le stock de l'article test est en dessous du seuil minimum",
            "article_id": created_ids["article"],
            "lue": False
        }
        
        # Insert alert directly into the database using a custom endpoint
        success, message, data = make_request("post", "/alertes/test-create", data=alerte_data, token=token, expected_status=200)
        if success and data and "id" in data:
            created_ids["alerte"] = data["id"]
    
    # Now get the list of alerts
    success, message, data = make_request("get", "/alertes", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("List alertes", True, f"Retrieved {len(data)} alertes")
        test_results["alertes"]["list"]["success"] = True
        test_results["alertes"]["list"]["message"] = f"Successfully retrieved {len(data)} alertes"
        
        # Store an alerte ID if available for the next test
        if data and len(data) > 0:
            created_ids["alerte"] = data[0]["id"]
            return True
        
        # If no alerts were found but we have an article, create a test alert manually
        if not created_ids["alerte"] and created_ids["article"]:
            # Create a test alert directly in MongoDB
            print("Creating a test alert manually...")
            success, message, _ = make_request(
                "post", 
                "/alertes/test-create", 
                data={
                    "type": "stock_bas",
                    "priorite": "high",
                    "titre": "Test Alert",
                    "message": "This is a test alert",
                    "article_id": created_ids["article"]
                },
                token=token
            )
            
            # Try to get alerts again
            success, message, data = make_request("get", "/alertes", token=token, expected_status=200)
            if success and isinstance(data, list) and len(data) > 0:
                created_ids["alerte"] = data[0]["id"]
                print_test_result("Create test alert", True, f"Created test alert with ID: {created_ids['alerte']}")
                return True
        
        return True
    else:
        print_test_result("List alertes", False, message)
        test_results["alertes"]["list"]["message"] = message
        return False

def test_marquer_alerte_lue(token, alerte_id):
    if not alerte_id:
        print_test_result("Mark alerte as read", False, "No alerte ID available")
        test_results["alertes"]["marquer_lue"]["message"] = "No alerte ID available"
        return False
        
    print_header("Testing Mark Alerte as Read")
    success, message, data = make_request("put", f"/alertes/{alerte_id}/marquer-lue", token=token, expected_status=200)
    
    if success:
        print_test_result("Mark alerte as read", True, "Successfully marked alerte as read")
        test_results["alertes"]["marquer_lue"]["success"] = True
        test_results["alertes"]["marquer_lue"]["message"] = "Successfully marked alerte as read"
        return True
    else:
        print_test_result("Mark alerte as read", False, message)
        test_results["alertes"]["marquer_lue"]["message"] = message
        return False

def test_dashboard_stats(token):
    print_header("Testing Dashboard Stats")
    success, message, data = make_request("get", "/dashboard/stats", token=token, expected_status=200)
    
    if success and data and isinstance(data, dict):
        print_test_result("Get dashboard stats", True, f"Retrieved dashboard stats: {data}")
        test_results["dashboard"]["stats"]["success"] = True
        test_results["dashboard"]["stats"]["message"] = "Successfully retrieved dashboard stats"
        return True
    else:
        print_test_result("Get dashboard stats", False, message)
        test_results["dashboard"]["stats"]["message"] = message
        return False

def test_unauthorized_access():
    print_header("Testing Unauthorized Access")
    # For this test, we expect a 401 or 403 error when accessing a protected endpoint without a token
    success, message, data = make_request("get", "/fournisseurs", expected_status=401)
    
    if not success:
        # Try with 403 status code as an alternative
        success, message, data = make_request("get", "/fournisseurs", expected_status=403)
    
    if success:
        print_test_result("Unauthorized access", True, "Correctly rejected request without token")
        test_results["access_control"]["unauthorized"]["success"] = True
        test_results["access_control"]["unauthorized"]["message"] = "Correctly rejected request without token"
        return True
    else:
        print_test_result("Unauthorized access", False, "Request without token was not rejected properly")
        test_results["access_control"]["unauthorized"]["message"] = "Request without token was not rejected properly"
        return False

def test_role_based_access():
    print_header("Testing Role-Based Access Control")
    # Try to create a fournisseur with a normal user (should be forbidden)
    success, message, data = make_request("post", "/fournisseurs", data=test_fournisseur, token=tokens["user"], expected_status=403)
    
    # For this test, success means we got the expected 403 error
    if success:
        print_test_result("Role-based access", True, "Correctly rejected request from user without proper role")
        test_results["access_control"]["role_based"]["success"] = True
        test_results["access_control"]["role_based"]["message"] = "Correctly rejected request from user without proper role"
        return True
    else:
        print_test_result("Role-based access", False, "Request from user without proper role was not rejected properly")
        test_results["access_control"]["role_based"]["message"] = "Request from user without proper role was not rejected properly"
        return False

# Enhanced API test functions
def test_fournisseurs_search(token):
    print_header("Testing Fournisseurs Search")
    
    # Test search functionality
    params = {"search": "test"}
    success, message, data = make_request("get", "/fournisseurs", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Fournisseurs search", True, f"Found {len(data)} fournisseurs matching 'test'")
        test_results["fournisseurs"]["search"]["success"] = True
        test_results["fournisseurs"]["search"]["message"] = f"Successfully searched fournisseurs with term 'test'"
        return True
    else:
        print_test_result("Fournisseurs search", False, message)
        test_results["fournisseurs"]["search"]["message"] = message
        return False

def test_fournisseurs_sort(token):
    print_header("Testing Fournisseurs Sort")
    
    # Test sorting functionality (ascending)
    params_asc = {"sort_by": "nom", "sort_order": "asc"}
    success_asc, message_asc, data_asc = make_request("get", "/fournisseurs", params=params_asc, token=token, expected_status=200)
    
    # Test sorting functionality (descending)
    params_desc = {"sort_by": "nom", "sort_order": "desc"}
    success_desc, message_desc, data_desc = make_request("get", "/fournisseurs", params=params_desc, token=token, expected_status=200)
    
    if success_asc and success_desc and isinstance(data_asc, list) and isinstance(data_desc, list):
        # Verify that the order is different between ascending and descending
        if len(data_asc) > 1 and len(data_desc) > 1:
            is_different_order = data_asc[0]["nom"] != data_desc[0]["nom"]
            if is_different_order:
                print_test_result("Fournisseurs sort", True, "Sorting works correctly in both directions")
                test_results["fournisseurs"]["sort"]["success"] = True
                test_results["fournisseurs"]["sort"]["message"] = "Successfully sorted fournisseurs by nom in both directions"
                return True
            else:
                print_test_result("Fournisseurs sort", False, "Sorting doesn't seem to change the order")
                test_results["fournisseurs"]["sort"]["message"] = "Sorting doesn't seem to change the order"
                return False
        else:
            print_test_result("Fournisseurs sort", True, "Not enough data to verify sort order, but API returned successfully")
            test_results["fournisseurs"]["sort"]["success"] = True
            test_results["fournisseurs"]["sort"]["message"] = "Not enough data to verify sort order, but API returned successfully"
            return True
    else:
        print_test_result("Fournisseurs sort", False, message_asc if not success_asc else message_desc)
        test_results["fournisseurs"]["sort"]["message"] = message_asc if not success_asc else message_desc
        return False

def test_fournisseurs_filter(token):
    print_header("Testing Fournisseurs Filter")
    
    # Test filtering by ville
    params = {"ville": "Lyon"}
    success, message, data = make_request("get", "/fournisseurs", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Check if all returned fournisseurs have ville = Lyon
        all_match = all(f.get("ville", "").lower() == "lyon" for f in data) if data else True
        
        if all_match:
            print_test_result("Fournisseurs filter by ville", True, f"Found {len(data)} fournisseurs in Lyon")
            test_results["fournisseurs"]["filter"]["success"] = True
            test_results["fournisseurs"]["filter"]["message"] = f"Successfully filtered fournisseurs by ville=Lyon"
            return True
        else:
            print_test_result("Fournisseurs filter by ville", False, "Filter returned fournisseurs not in Lyon")
            test_results["fournisseurs"]["filter"]["message"] = "Filter returned fournisseurs not in Lyon"
            return False
    else:
        print_test_result("Fournisseurs filter by ville", False, message)
        test_results["fournisseurs"]["filter"]["message"] = message
        return False

def test_articles_search(token):
    print_header("Testing Articles Search")
    
    # Test search functionality
    params = {"search": "test"}
    success, message, data = make_request("get", "/articles", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Articles search", True, f"Found {len(data)} articles matching 'test'")
        test_results["articles"]["search"]["success"] = True
        test_results["articles"]["search"]["message"] = f"Successfully searched articles with term 'test'"
        return True
    else:
        print_test_result("Articles search", False, message)
        test_results["articles"]["search"]["message"] = message
        return False

def test_articles_sort(token):
    print_header("Testing Articles Sort")
    
    # Test sorting functionality (ascending)
    params_asc = {"sort_by": "prix_unitaire", "sort_order": "asc"}
    success_asc, message_asc, data_asc = make_request("get", "/articles", params=params_asc, token=token, expected_status=200)
    
    # Test sorting functionality (descending)
    params_desc = {"sort_by": "prix_unitaire", "sort_order": "desc"}
    success_desc, message_desc, data_desc = make_request("get", "/articles", params=params_desc, token=token, expected_status=200)
    
    if success_asc and success_desc and isinstance(data_asc, list) and isinstance(data_desc, list):
        # Verify that the order is different between ascending and descending
        if len(data_asc) > 1 and len(data_desc) > 1:
            is_different_order = data_asc[0]["prix_unitaire"] != data_desc[0]["prix_unitaire"]
            if is_different_order:
                print_test_result("Articles sort", True, "Sorting works correctly in both directions")
                test_results["articles"]["sort"]["success"] = True
                test_results["articles"]["sort"]["message"] = "Successfully sorted articles by prix_unitaire in both directions"
                return True
            else:
                print_test_result("Articles sort", False, "Sorting doesn't seem to change the order")
                test_results["articles"]["sort"]["message"] = "Sorting doesn't seem to change the order"
                return False
        else:
            print_test_result("Articles sort", True, "Not enough data to verify sort order, but API returned successfully")
            test_results["articles"]["sort"]["success"] = True
            test_results["articles"]["sort"]["message"] = "Not enough data to verify sort order, but API returned successfully"
            return True
    else:
        print_test_result("Articles sort", False, message_asc if not success_asc else message_desc)
        test_results["articles"]["sort"]["message"] = message_asc if not success_asc else message_desc
        return False

def test_articles_filter(token):
    print_header("Testing Articles Filter")
    
    # Test filtering by famille
    params = {"famille": "Test"}
    success, message, data = make_request("get", "/articles", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Articles filter by famille", True, f"Found {len(data)} articles in famille Test")
        test_results["articles"]["filter"]["success"] = True
        test_results["articles"]["filter"]["message"] = f"Successfully filtered articles by famille=Test"
        return True
    else:
        print_test_result("Articles filter by famille", False, message)
        test_results["articles"]["filter"]["message"] = message
        return False

def test_commandes_search(token):
    print_header("Testing Commandes Search")
    
    # Test search functionality
    params = {"search": "test"}
    success, message, data = make_request("get", "/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Commandes search", True, f"Found {len(data)} commandes matching 'test'")
        test_results["commandes"]["search"]["success"] = True
        test_results["commandes"]["search"]["message"] = f"Successfully searched commandes with term 'test'"
        return True
    else:
        print_test_result("Commandes search", False, message)
        test_results["commandes"]["search"]["message"] = message
        return False

def test_commandes_sort(token):
    print_header("Testing Commandes Sort")
    
    # Test sorting functionality (ascending)
    params_asc = {"sort_by": "total_ttc", "sort_order": "asc"}
    success_asc, message_asc, data_asc = make_request("get", "/commandes", params=params_asc, token=token, expected_status=200)
    
    # Test sorting functionality (descending)
    params_desc = {"sort_by": "total_ttc", "sort_order": "desc"}
    success_desc, message_desc, data_desc = make_request("get", "/commandes", params=params_desc, token=token, expected_status=200)
    
    if success_asc and success_desc and isinstance(data_asc, list) and isinstance(data_desc, list):
        # Verify that the order is different between ascending and descending
        if len(data_asc) > 1 and len(data_desc) > 1:
            is_different_order = data_asc[0]["total_ttc"] != data_desc[0]["total_ttc"]
            if is_different_order:
                print_test_result("Commandes sort", True, "Sorting works correctly in both directions")
                test_results["commandes"]["sort"]["success"] = True
                test_results["commandes"]["sort"]["message"] = "Successfully sorted commandes by total_ttc in both directions"
                return True
            else:
                print_test_result("Commandes sort", False, "Sorting doesn't seem to change the order")
                test_results["commandes"]["sort"]["message"] = "Sorting doesn't seem to change the order"
                return False
        else:
            print_test_result("Commandes sort", True, "Not enough data to verify sort order, but API returned successfully")
            test_results["commandes"]["sort"]["success"] = True
            test_results["commandes"]["sort"]["message"] = "Not enough data to verify sort order, but API returned successfully"
            return True
    else:
        print_test_result("Commandes sort", False, message_asc if not success_asc else message_desc)
        test_results["commandes"]["sort"]["message"] = message_asc if not success_asc else message_desc
        return False

def test_commandes_filter(token):
    print_header("Testing Commandes Filter")
    
    # Test filtering by status
    params = {"status": "brouillon"}
    success, message, data = make_request("get", "/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Check if all returned commandes have status = brouillon
        all_match = all(c.get("status") == "brouillon" for c in data) if data else True
        
        if all_match:
            print_test_result("Commandes filter by status", True, f"Found {len(data)} commandes with status brouillon")
            test_results["commandes"]["filter"]["success"] = True
            test_results["commandes"]["filter"]["message"] = f"Successfully filtered commandes by status=brouillon"
            return True
        else:
            print_test_result("Commandes filter by status", False, "Filter returned commandes with wrong status")
            test_results["commandes"]["filter"]["message"] = "Filter returned commandes with wrong status"
            return False
    else:
        print_test_result("Commandes filter by status", False, message)
        test_results["commandes"]["filter"]["message"] = message
        return False

def test_commandes_date_filter(token):
    print_header("Testing Commandes Date Filter")
    
    # Test date range filtering
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    one_year_future = today + timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": one_year_future.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Commandes date filter", True, f"Found {len(data)} commandes in date range")
        test_results["commandes"]["date_filter"]["success"] = True
        test_results["commandes"]["date_filter"]["message"] = f"Successfully filtered commandes by date range"
        return True
    else:
        print_test_result("Commandes date filter", False, message)
        test_results["commandes"]["date_filter"]["message"] = message
        return False

# Test functions for reporting APIs
def test_report_fournisseurs(token):
    print_header("Testing Fournisseurs Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/fournisseurs", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Fournisseurs report", True, f"Retrieved report for {len(data)} fournisseurs")
        test_results["reports"]["fournisseurs"]["success"] = True
        test_results["reports"]["fournisseurs"]["message"] = f"Successfully retrieved fournisseurs report"
        
        # Print a sample of the data for debugging
        if data:
            print(f"  - Sample data: {data[0]}")
        return True
    else:
        print_test_result("Fournisseurs report", False, message)
        test_results["reports"]["fournisseurs"]["message"] = message
        return False

def test_report_articles(token):
    print_header("Testing Articles Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/articles", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Articles report", True, f"Retrieved report for {len(data)} articles")
        test_results["reports"]["articles"]["success"] = True
        test_results["reports"]["articles"]["message"] = f"Successfully retrieved articles report"
        
        # Print a sample of the data for debugging
        if data:
            print(f"  - Sample data: {data[0]}")
        return True
    else:
        print_test_result("Articles report", False, message)
        test_results["reports"]["articles"]["message"] = message
        return False

def test_report_commandes(token):
    print_header("Testing Commandes Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Commandes report", True, f"Retrieved report for {len(data)} commandes")
        test_results["reports"]["commandes"]["success"] = True
        test_results["reports"]["commandes"]["message"] = f"Successfully retrieved commandes report"
        
        # Print a sample of the data for debugging
        if data:
            print(f"  - Sample data: {data[0]}")
        return True
    else:
        print_test_result("Commandes report", False, message)
        test_results["reports"]["commandes"]["message"] = message
        return False

def test_report_synthese(token):
    print_header("Testing Synthese Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/synthese", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, dict):
        # Check if the report contains the expected fields
        required_fields = [
            "total_fournisseurs", "total_articles", "articles_stock_bas", 
            "total_commandes", "valeur_totale_commandes", "valeur_totale_stock"
        ]
        
        if all(field in data for field in required_fields):
            print_test_result("Synthese report", True, "Retrieved synthesis report with all required fields")
            test_results["reports"]["synthese"]["success"] = True
            test_results["reports"]["synthese"]["message"] = "Successfully retrieved synthesis report with all required fields"
            return True
        else:
            print_test_result("Synthese report", False, "Report missing required fields")
            test_results["reports"]["synthese"]["message"] = "Report missing required fields"
            return False
    else:
        print_test_result("Synthese report", False, message)
        test_results["reports"]["synthese"]["message"] = message
        return False

def create_test_data(admin_token):
    print_header("Creating Additional Test Data")
    
    # Create additional suppliers
    suppliers = [
        {
            "nom": "Fournitures Bureau Express",
            "code_fournisseur": f"FBE-{uuid.uuid4().hex[:6]}",
            "adresse": "45 Rue du Commerce",
            "ville": "Lyon",
            "code_postal": "69002",
            "pays": "France",
            "telephone": "+33472456789",
            "email": f"contact@fournitures-bureau-express.fr",
            "site_web": "https://www.fournitures-bureau-express.fr",
            "conditions_paiement": "45 jours",
            "delai_livraison_moyen": 3,
            "contacts": [
                {
                    "nom": "Martin",
                    "prenom": "Sophie",
                    "telephone": "+33612345678",
                    "email": "s.martin@fournitures-bureau-express.fr",
                    "poste": "Directrice commerciale"
                }
            ]
        },
        {
            "nom": "Tech Solutions Pro",
            "code_fournisseur": f"TSP-{uuid.uuid4().hex[:6]}",
            "adresse": "123 Avenue de l'Innovation",
            "ville": "Bordeaux",
            "code_postal": "33000",
            "pays": "France",
            "telephone": "+33556789012",
            "email": f"contact@techsolutionspro.com",
            "site_web": "https://www.techsolutionspro.com",
            "conditions_paiement": "30 jours",
            "delai_livraison_moyen": 7,
            "contacts": [
                {
                    "nom": "Dubois",
                    "prenom": "Thomas",
                    "telephone": "+33678901234",
                    "email": "t.dubois@techsolutionspro.com",
                    "poste": "Responsable grands comptes"
                }
            ]
        }
    ]
    
    supplier_ids = []
    for supplier_data in suppliers:
        success, message, data = make_request("post", "/fournisseurs", data=supplier_data, token=admin_token, expected_status=200)
        if success and data and "id" in data:
            print(f"Created supplier: {data['nom']}")
            supplier_ids.append(data["id"])
    
    # Create additional articles for each supplier
    article_ids = []
    for supplier_id in supplier_ids:
        articles = [
            {
                "reference": f"PAP-{uuid.uuid4().hex[:6]}",
                "nom": "Papier A4 Premium",
                "description": "Ramette de papier A4 80g/m² haute qualité",
                "famille": "Papeterie",
                "fournisseur_id": supplier_id,
                "prix_unitaire": 4.99,
                "unite": "ramette",
                "seuil_min": 20,
                "seuil_max": 100,
                "stock_actuel": 15,
                "duree_vie": 730,
                "emplacement_stockage": "Étagère B2"
            },
            {
                "reference": f"STY-{uuid.uuid4().hex[:6]}",
                "nom": "Stylos à bille",
                "description": "Lot de 50 stylos à bille bleus",
                "famille": "Écriture",
                "fournisseur_id": supplier_id,
                "prix_unitaire": 12.50,
                "unite": "lot",
                "seuil_min": 5,
                "seuil_max": 30,
                "stock_actuel": 3,
                "duree_vie": 365,
                "emplacement_stockage": "Tiroir C3"
            },
            {
                "reference": f"INF-{uuid.uuid4().hex[:6]}",
                "nom": "Disque dur externe 1TB",
                "description": "Disque dur externe USB 3.0 1TB",
                "famille": "Informatique",
                "fournisseur_id": supplier_id,
                "prix_unitaire": 79.99,
                "unite": "pièce",
                "seuil_min": 3,
                "seuil_max": 15,
                "stock_actuel": 2,
                "duree_vie": 1095,
                "emplacement_stockage": "Armoire sécurisée D1"
            }
        ]
        
        for article_data in articles:
            success, message, data = make_request("post", "/articles", data=article_data, token=admin_token, expected_status=200)
            if success and data and "id" in data:
                print(f"Created article: {data['nom']}")
                article_ids.append(data["id"])
    
    # Create orders using the articles
    if article_ids and supplier_ids:
        for i, supplier_id in enumerate(supplier_ids):
            # Select 2 articles for this supplier
            order_articles = article_ids[i*3:(i+1)*3]
            if order_articles:
                commande_data = {
                    "fournisseur_id": supplier_id,
                    "lignes": [
                        {
                            "article_id": article_ids[0],
                            "quantite": 30,
                            "prix_unitaire": 4.99,
                            "total": 149.70
                        },
                        {
                            "article_id": article_ids[1] if len(article_ids) > 1 else article_ids[0],
                            "quantite": 10,
                            "prix_unitaire": 12.50,
                            "total": 125.00
                        }
                    ],
                    "date_livraison_prevue": (datetime.now() + timedelta(days=5)).isoformat(),
                    "notes": "Commande urgente pour réapprovisionnement"
                }
                
                success, message, data = make_request("post", "/commandes", data=commande_data, token=admin_token, expected_status=200)
                if success and data and "id" in data:
                    print(f"Created order: {data['numero_commande']}")
    
    # Create some alerts
    for article_id in article_ids[:2]:  # Use first 2 articles
        alerte_data = {
            "type": "stock_bas",
            "priorite": "high",
            "titre": f"Stock bas - Réapprovisionnement urgent",
            "message": f"Le stock de l'article est en dessous du seuil minimum. Veuillez commander rapidement.",
            "article_id": article_id,
            "lue": False
        }
        
        success, message, data = make_request("post", "/alertes/test-create", data=alerte_data, token=admin_token, expected_status=200)
        if success and data and "id" in data:
            print(f"Created alert: {data['titre']}")
    
    print("Test data creation completed")

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

def run_all_tests():
    print_header("STARTING BACKEND API TESTS")
    
    # Test unauthorized access first
    test_unauthorized_access()
    
    # Test authentication - skip registration if users already exist
    admin_token = test_auth_login(ADMIN_USER)
    if not admin_token:
        # Try to register if login fails
        admin_registered = test_auth_register(ADMIN_USER)
        if admin_registered:
            admin_token = test_auth_login(ADMIN_USER)
    
    if admin_token:
        test_auth_me(admin_token, ADMIN_USER["email"])
        
    # Manager user
    manager_token = test_auth_login(MANAGER_USER)
    if not manager_token:
        # Try to register if login fails
        manager_registered = test_auth_register(MANAGER_USER)
        if manager_registered:
            manager_token = test_auth_login(MANAGER_USER)
    
    if manager_token:
        test_auth_me(manager_token, MANAGER_USER["email"])
    
    # Normal user
    user_token = test_auth_login(NORMAL_USER)
    if not user_token:
        # Try to register if login fails
        user_registered = test_auth_register(NORMAL_USER)
        if user_registered:
            user_token = test_auth_login(NORMAL_USER)
    
    if user_token:
        test_auth_me(user_token, NORMAL_USER["email"])
    
    # Test role-based access control
    if tokens["user"] and tokens["admin"]:
        test_role_based_access()
    
    # If admin authentication failed, we can't test the rest
    if not tokens["admin"]:
        print("Admin authentication failed, cannot proceed with further tests")
        print_summary()
        return
    
    # Test fournisseurs
    fournisseur_id = test_create_fournisseur(tokens["admin"])
    if fournisseur_id:
        test_list_fournisseurs(tokens["admin"])
        test_get_fournisseur(tokens["admin"], fournisseur_id)
        test_update_fournisseur(tokens["admin"], fournisseur_id)
    
    # Test articles
    if fournisseur_id:
        article_id = test_create_article(tokens["admin"], fournisseur_id)
        if article_id:
            test_list_articles(tokens["admin"])
            test_articles_stock_bas(tokens["admin"])
            
            # Test commandes
            commande_id = test_create_commande(tokens["admin"], fournisseur_id, article_id)
            if commande_id:
                test_list_commandes(tokens["admin"])
    
    # Test alertes
    test_list_alertes(tokens["admin"])
    if created_ids["alerte"]:
        test_marquer_alerte_lue(tokens["admin"], created_ids["alerte"])
    
    # Test dashboard
    test_dashboard_stats(tokens["admin"])
    
    # Create additional test data
    create_test_data(tokens["admin"])
    
    # Test enhanced APIs
    test_fournisseurs_search(tokens["admin"])
    test_fournisseurs_sort(tokens["admin"])
    test_fournisseurs_filter(tokens["admin"])
    
    test_articles_search(tokens["admin"])
    test_articles_sort(tokens["admin"])
    test_articles_filter(tokens["admin"])
    
    test_commandes_search(tokens["admin"])
    test_commandes_sort(tokens["admin"])
    test_commandes_filter(tokens["admin"])
    test_commandes_date_filter(tokens["admin"])
    
    # Test reporting APIs
    test_report_fournisseurs(tokens["admin"])
    test_report_articles(tokens["admin"])
    test_report_commandes(tokens["admin"])
    test_report_synthese(tokens["admin"])
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_all_tests()