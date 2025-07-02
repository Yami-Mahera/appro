import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://69cb1958-5549-4794-bc43-3b9b3f8e2dd7.preview.emergentagent.com/api"
ADMIN_USER = {
    "email": f"admin_{uuid.uuid4()}@test.com",
    "password": "Admin@123456",
    "nom": "Admin",
    "prenom": "Test",
    "role": "administrateur"
}
MANAGER_USER = {
    "email": f"manager_{uuid.uuid4()}@test.com",
    "password": "Manager@123456",
    "nom": "Manager",
    "prenom": "Test",
    "role": "manager"
}
NORMAL_USER = {
    "email": f"user_{uuid.uuid4()}@test.com",
    "password": "User@123456",
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
        "update": {"success": False, "message": "Not tested"}
    },
    "articles": {
        "create": {"success": False, "message": "Not tested"},
        "list": {"success": False, "message": "Not tested"},
        "stock_bas": {"success": False, "message": "Not tested"}
    },
    "commandes": {
        "create": {"success": False, "message": "Not tested"},
        "list": {"success": False, "message": "Not tested"}
    },
    "alertes": {
        "list": {"success": False, "message": "Not tested"},
        "marquer_lue": {"success": False, "message": "Not tested"}
    },
    "dashboard": {
        "stats": {"success": False, "message": "Not tested"}
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
    success, message, data = make_request("post", "/auth/register", user_data, expected_status=200)
    
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
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
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
    success, message, data = make_request("post", "/fournisseurs", test_fournisseur, token=token, expected_status=200)
    
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
    
    success, message, data = make_request("put", f"/fournisseurs/{fournisseur_id}", updated_data, token=token, expected_status=200)
    
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
    
    success, message, data = make_request("post", "/articles", article_data, token=token, expected_status=200)
    
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
    
    success, message, data = make_request("post", "/commandes", commande_data, token=token, expected_status=200)
    
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
        success, message, data = make_request("post", "/alertes/test-create", alerte_data, token=token, expected_status=200)
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
                {
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
    success, message, data = make_request("post", "/fournisseurs", test_fournisseur, token=tokens["user"], expected_status=403)
    
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
    
    # Test authentication
    admin_registered = test_auth_register(ADMIN_USER)
    if admin_registered:
        admin_token = test_auth_login(ADMIN_USER)
        if admin_token:
            test_auth_me(admin_token, ADMIN_USER["email"])
    
    # Register a normal user for role-based access testing
    user_registered = test_auth_register(NORMAL_USER)
    if user_registered:
        user_token = test_auth_login(NORMAL_USER)
    
    # Test role-based access control
    if tokens["user"]:
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
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_all_tests()