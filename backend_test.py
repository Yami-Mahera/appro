import requests
import json
import time
import uuid
import re
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

# Test results
test_results = {
    "auth": {
        "register": {"success": False, "message": "Not tested"},
        "login": {"success": False, "message": "Not tested"},
        "me": {"success": False, "message": "Not tested"}
    },
    "users": {
        "list": {"success": False, "message": "Not tested"},
        "create": {"success": False, "message": "Not tested"},
        "get": {"success": False, "message": "Not tested"},
        "update": {"success": False, "message": "Not tested"},
        "reset_password": {"success": False, "message": "Not tested"},
        "delete": {"success": False, "message": "Not tested"}
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
        "role_based": {"success": False, "message": "Not tested"},
        "admin_self_delete": {"success": False, "message": "Not tested"}
    },
    "validations": {
        "email_uniqueness": {"success": False, "message": "Not tested"},
        "invalid_email": {"success": False, "message": "Not tested"},
        "password_validation": {"success": False, "message": "Not tested"}
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
    "user": None,
    "user_admin": None,
    "user_manager": None,
    "user_normal": None,
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

def test_alertes_system():
    print_header("TESTING ALERT SYSTEM")
    
    # Login as admin
    admin_token = test_auth_login(ADMIN_USER)
    if not admin_token:
        print("Admin authentication failed, cannot proceed with alert system tests")
        return False
    
    # Create multiple test alerts with different dates to test sorting
    print_header("Creating Test Alerts")
    alert_ids = []
    
    # Create 15 alerts with different timestamps to test sorting and limit
    for i in range(15):
        # Create alerts with timestamps spaced 1 hour apart
        hours_ago = 15 - i  # Newest alerts will have smaller hours_ago values
        timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
        
        alerte_data = {
            "type": "stock_bas",
            "priorite": "high",
            "titre": f"Test Alert {i+1}",
            "message": f"This is test alert {i+1} created for testing",
            "lue": i < 5,  # First 5 will be marked as read, rest unread
            "created_at": timestamp.isoformat()
        }
        
        success, message, data = make_request("post", "/alertes/test-create", alerte_data, token=admin_token, expected_status=200)
        if success and data and "id" in data:
            print(f"Created alert: {data['titre']} (Read: {data['lue']})")
            alert_ids.append(data["id"])
    
    # Test 1: Get all alerts and verify sorting by date (newest first)
    print_header("Test 1: Get All Alerts (Sorted by Date)")
    success, message, data = make_request("get", "/alertes", token=admin_token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get all alerts", True, f"Retrieved {len(data)} alerts")
        
        # Check if alerts are sorted by date (newest first)
        is_sorted = all(data[i]["created_at"] >= data[i+1]["created_at"] for i in range(len(data)-1))
        print_test_result("Alerts sorted by date", is_sorted, 
                         "Alerts are correctly sorted by date (newest first)" if is_sorted 
                         else "Alerts are NOT sorted by date correctly")
        
        # Store the first alert ID for testing mark-read functionality
        if data and len(data) > 0:
            first_alert_id = data[0]["id"]
    else:
        print_test_result("Get all alerts", False, message)
        return False
    
    # Test 2: Test limit parameter (should be 100 by default based on the implementation)
    print_header("Test 2: Test Default Limit (100)")
    success, message, data = make_request("get", "/alertes", token=admin_token, expected_status=200)
    
    if success and isinstance(data, list):
        default_limit_correct = len(data) <= 100
        print_test_result("Default limit (100)", default_limit_correct, 
                         f"Default limit works correctly, got {len(data)} alerts" if default_limit_correct 
                         else f"Default limit not working, got {len(data)} alerts instead of 100 or fewer")
    else:
        print_test_result("Test default limit", False, message)
    
    # Test 3: Get only unread alerts
    print_header("Test 3: Get Unread Alerts")
    success, message, data = make_request("get", "/alertes?lue=false", token=admin_token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get unread alerts", True, f"Retrieved {len(data)} unread alerts")
        
        # Verify all retrieved alerts are unread
        all_unread = all(not alert["lue"] for alert in data)
        print_test_result("All alerts unread", all_unread, 
                         "All retrieved alerts are correctly marked as unread" if all_unread 
                         else "Some retrieved alerts are incorrectly marked as read")
    else:
        print_test_result("Get unread alerts", False, message)
    
    # Test 4: Mark an alert as read
    print_header("Test 4: Mark Alert as Read")
    if alert_ids:
        # Get an unread alert
        success, message, unread_alerts = make_request("get", "/alertes?lue=false", token=admin_token, expected_status=200)
        if success and unread_alerts and len(unread_alerts) > 0:
            unread_alert_id = unread_alerts[0]["id"]
            
            # Mark it as read
            success, message, data = make_request("put", f"/alertes/{unread_alert_id}/marquer-lue", token=admin_token, expected_status=200)
            
            if success:
                print_test_result("Mark alert as read", True, f"Successfully marked alert {unread_alert_id} as read")
                
                # Verify it's now marked as read
                success, message, updated_alert = make_request("get", "/alertes", token=admin_token, expected_status=200)
                if success:
                    found_alert = next((a for a in updated_alert if a["id"] == unread_alert_id), None)
                    if found_alert and found_alert["lue"]:
                        print_test_result("Alert marked as read verification", True, "Alert is correctly marked as read in the database")
                    else:
                        print_test_result("Alert marked as read verification", False, "Alert was not correctly marked as read in the database")
            else:
                print_test_result("Mark alert as read", False, message)
        else:
            print_test_result("Get unread alert for marking", False, "No unread alerts available for testing")
    else:
        print_test_result("Mark alert as read", False, "No alert IDs available for testing")
    
    print_header("ALERT SYSTEM TESTS COMPLETED")
    return True

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
# User Management Test Functions
def test_list_users(token):
    print_header("Testing List Users")
    success, message, data = make_request("get", "/users", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("List users", True, f"Retrieved {len(data)} users")
        test_results["users"]["list"]["success"] = True
        test_results["users"]["list"]["message"] = f"Successfully retrieved {len(data)} users"
        return True
    else:
        print_test_result("List users", False, message)
        test_results["users"]["list"]["message"] = message
        return False

def test_create_user(token, role="utilisateur"):
    print_header(f"Testing Create User with role: {role}")
    
    # Generate a unique email to avoid conflicts
    unique_id = uuid.uuid4().hex[:6]
    user_data = {
        "email": f"test.{role}.{unique_id}@example.com",
        "password": "Password123!",
        "nom": f"Test {role.capitalize()}",
        "prenom": f"User {unique_id}",
        "role": role
    }
    
    success, message, data = make_request("post", "/users", user_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Create user", True, f"Created user: {data['email']} with role {data['role']}")
        test_results["users"]["create"]["success"] = True
        test_results["users"]["create"]["message"] = f"Successfully created user with role {role}"
        
        # Store the user ID based on role
        if role == "administrateur":
            created_ids["user_admin"] = data["id"]
        elif role == "manager":
            created_ids["user_manager"] = data["id"]
        elif role == "utilisateur":
            created_ids["user_normal"] = data["id"]
        
        # Store the latest user ID regardless of role
        created_ids["user"] = data["id"]
        
        return data["id"]
    else:
        print_test_result("Create user", False, message)
        test_results["users"]["create"]["message"] = message
        return None

def test_get_user(token, user_id):
    print_header("Testing Get User")
    success, message, data = make_request("get", f"/users/{user_id}", token=token, expected_status=200)
    
    if success and data and data["id"] == user_id:
        print_test_result("Get user", True, f"Retrieved user: {data['email']}")
        test_results["users"]["get"]["success"] = True
        test_results["users"]["get"]["message"] = f"Successfully retrieved user: {data['email']}"
        return True
    else:
        print_test_result("Get user", False, message)
        test_results["users"]["get"]["message"] = message
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
        test_results["users"]["update"]["success"] = True
        test_results["users"]["update"]["message"] = f"Successfully updated user: {data['email']}"
        return True
    else:
        print_test_result("Update user", False, message)
        test_results["users"]["update"]["message"] = message
        return False

def test_reset_user_password(token, user_id):
    print_header("Testing Reset User Password")
    password_data = {
        "new_password": "NewPassword123!"
    }
    
    success, message, data = make_request("put", f"/users/{user_id}/reset-password", password_data, token=token, expected_status=200)
    
    if success:
        print_test_result("Reset user password", True, "Password reset successful")
        test_results["users"]["reset_password"]["success"] = True
        test_results["users"]["reset_password"]["message"] = "Successfully reset user password"
        return True
    else:
        print_test_result("Reset user password", False, message)
        test_results["users"]["reset_password"]["message"] = message
        return False

def test_delete_user(token, user_id):
    print_header("Testing Delete User")
    success, message, data = make_request("delete", f"/users/{user_id}", token=token, expected_status=200)
    
    if success:
        print_test_result("Delete user", True, "User deleted successfully")
        test_results["users"]["delete"]["success"] = True
        test_results["users"]["delete"]["message"] = "Successfully deleted user"
        return True
    else:
        print_test_result("Delete user", False, message)
        test_results["users"]["delete"]["message"] = message
        return False

def test_admin_self_delete(token, admin_id):
    print_header("Testing Admin Self-Delete Prevention")
    # For this test, we expect a 400 error when an admin tries to delete their own account
    success, message, data = make_request("delete", f"/users/{admin_id}", token=token, expected_status=400)
    
    if success:
        print_test_result("Admin self-delete prevention", True, "Correctly prevented admin from deleting own account")
        test_results["access_control"]["admin_self_delete"]["success"] = True
        test_results["access_control"]["admin_self_delete"]["message"] = "Correctly prevented admin from deleting own account"
        return True
    else:
        # Check if the error message indicates that self-deletion is not allowed
        if "Cannot delete your own account" in message:
            print_test_result("Admin self-delete prevention", True, "Correctly prevented admin from deleting own account")
            test_results["access_control"]["admin_self_delete"]["success"] = True
            test_results["access_control"]["admin_self_delete"]["message"] = "Correctly prevented admin from deleting own account"
            return True
        else:
            print_test_result("Admin self-delete prevention", False, "Admin was able to delete own account or unexpected error")
            test_results["access_control"]["admin_self_delete"]["message"] = message
            return False

def test_email_uniqueness(token):
    print_header("Testing Email Uniqueness Validation")
    
    # First create a user
    user_data = {
        "email": f"unique.test.{uuid.uuid4().hex[:6]}@example.com",
        "password": "Password123!",
        "nom": "Unique",
        "prenom": "Test",
        "role": "utilisateur"
    }
    
    success, message, data = make_request("post", "/users", user_data, token=token, expected_status=200)
    
    if not success:
        print_test_result("Email uniqueness", False, "Failed to create initial test user")
        test_results["validations"]["email_uniqueness"]["message"] = "Failed to create initial test user"
        return False
    
    # Now try to create another user with the same email
    duplicate_data = user_data.copy()
    duplicate_data["nom"] = "Duplicate"
    
    success, message, data = make_request("post", "/users", duplicate_data, token=token, expected_status=400)
    
    # For this test, success means we got the expected 400 error
    if success:
        print_test_result("Email uniqueness", True, "Correctly rejected duplicate email")
        test_results["validations"]["email_uniqueness"]["success"] = True
        test_results["validations"]["email_uniqueness"]["message"] = "Correctly rejected duplicate email"
        return True
    else:
        print_test_result("Email uniqueness", False, "Duplicate email was not rejected properly")
        test_results["validations"]["email_uniqueness"]["message"] = "Duplicate email was not rejected properly"
        return False

def test_invalid_email(token):
    print_header("Testing Invalid Email Validation")
    
    invalid_emails = [
        "not-an-email",
        "missing@domain",
        "@missing-local.com",
        "spaces in@email.com",
        "missing.domain@",
        "two@symbols@email.com"
    ]
    
    all_rejected = True
    for invalid_email in invalid_emails:
        user_data = {
            "email": invalid_email,
            "password": "Password123!",
            "nom": "Invalid",
            "prenom": "Email",
            "role": "utilisateur"
        }
        
        success, message, data = make_request("post", "/users", user_data, token=token, expected_status=422)
        
        if not success:
            all_rejected = False
            print_test_result(f"Invalid email: {invalid_email}", False, "Was not rejected properly")
    
    if all_rejected:
        print_test_result("Invalid email validation", True, "All invalid emails were correctly rejected")
        test_results["validations"]["invalid_email"]["success"] = True
        test_results["validations"]["invalid_email"]["message"] = "All invalid emails were correctly rejected"
        return True
    else:
        print_test_result("Invalid email validation", False, "Some invalid emails were not rejected")
        test_results["validations"]["invalid_email"]["message"] = "Some invalid emails were not rejected"
        return False

def test_password_validation(token):
    print_header("Testing Password Validation")
    
    # This test is a bit tricky since the backend might not have strict password validation
    # We'll test with an empty password which should definitely be rejected
    
    user_data = {
        "email": f"password.test.{uuid.uuid4().hex[:6]}@example.com",
        "password": "",  # Empty password
        "nom": "Password",
        "prenom": "Test",
        "role": "utilisateur"
    }
    
    success, message, data = make_request("post", "/users", user_data, token=token, expected_status=422)
    
    # For this test, success means we got the expected 422 error for validation
    # But the API might return 400 for bad request instead
    if success:
        print_test_result("Password validation", True, "Correctly rejected empty password")
        test_results["validations"]["password_validation"]["success"] = True
        test_results["validations"]["password_validation"]["message"] = "Correctly rejected empty password"
        return True
    else:
        # Check if we got a 400 error instead of 422
        success, message, data = make_request("post", "/users", user_data, token=token, expected_status=400)
        if success:
            print_test_result("Password validation", True, "Correctly rejected empty password (400 status)")
            test_results["validations"]["password_validation"]["success"] = True
            test_results["validations"]["password_validation"]["message"] = "Correctly rejected empty password"
            return True
        else:
            print_test_result("Password validation", False, "Empty password was not rejected properly")
            test_results["validations"]["password_validation"]["message"] = "Empty password was not rejected properly"
            return False
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
    
    # Try to login with existing users first
    print_header("Testing Authentication with Existing Users")
    admin_token = test_auth_login(ADMIN_USER)
    manager_token = test_auth_login(MANAGER_USER)
    user_token = test_auth_login(NORMAL_USER)
    
    # Register users only if login failed
    if not admin_token:
        print_header("Registering Admin User")
        admin_registered = test_auth_register(ADMIN_USER)
        if admin_registered:
            admin_token = test_auth_login(ADMIN_USER)
    
    if not manager_token:
        print_header("Registering Manager User")
        manager_registered = test_auth_register(MANAGER_USER)
        if manager_registered:
            manager_token = test_auth_login(MANAGER_USER)
    
    if not user_token:
        print_header("Registering Normal User")
        user_registered = test_auth_register(NORMAL_USER)
        if user_registered:
            user_token = test_auth_login(NORMAL_USER)
    
    # Store tokens
    if admin_token:
        tokens["admin"] = admin_token
        test_auth_me(admin_token, ADMIN_USER["email"])
    else:
        print("Admin authentication failed, cannot proceed with further tests")
        print_summary()
        return
    
    if manager_token:
        tokens["manager"] = manager_token
        test_auth_me(manager_token, MANAGER_USER["email"])
    
    if user_token:
        tokens["user"] = user_token
        test_auth_me(user_token, NORMAL_USER["email"])
    
    # Test role-based access control
    if tokens["user"]:
        test_role_based_access()
    
    # Test user management APIs
    print_header("Testing User Management APIs")
    
    # Test listing users (admin only)
    test_list_users(tokens["admin"])
    
    # Test creating users with different roles
    admin_user_id = test_create_user(tokens["admin"], "administrateur")
    manager_user_id = test_create_user(tokens["admin"], "manager")
    normal_user_id = test_create_user(tokens["admin"], "utilisateur")
    
    # Test getting a specific user
    if normal_user_id:
        test_get_user(tokens["admin"], normal_user_id)
    
    # Test updating a user
    if manager_user_id:
        test_update_user(tokens["admin"], manager_user_id)
    
    # Test resetting a user's password
    if normal_user_id:
        test_reset_user_password(tokens["admin"], normal_user_id)
    
    # Test admin self-delete prevention
    if tokens["admin"]:
        # Get the current admin's ID from /auth/me
        success, message, admin_data = make_request("get", "/auth/me", token=tokens["admin"], expected_status=200)
        if success and admin_data and "id" in admin_data:
            test_admin_self_delete(tokens["admin"], admin_data["id"])
    
    # Test deleting a user
    if normal_user_id:
        test_delete_user(tokens["admin"], normal_user_id)
    
    # Test validations
    test_email_uniqueness(tokens["admin"])
    test_invalid_email(tokens["admin"])
    test_password_validation(tokens["admin"])
    
    # Test access control with non-admin users
    if tokens["manager"]:
        print_header("Testing Access Control with Manager User")
        success, message, data = make_request("get", "/users", token=tokens["manager"], expected_status=403)
        if success:
            print_test_result("Manager access to users API", True, "Correctly rejected manager access to users API")
        else:
            print_test_result("Manager access to users API", False, "Manager was able to access users API or unexpected error")
    
    if tokens["user"]:
        print_header("Testing Access Control with Normal User")
        success, message, data = make_request("get", "/users", token=tokens["user"], expected_status=403)
        if success:
            print_test_result("Normal user access to users API", True, "Correctly rejected normal user access to users API")
        else:
            print_test_result("Normal user access to users API", False, "Normal user was able to access users API or unexpected error")
    
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
        success, message, data = make_request("post", "/fournisseurs", supplier_data, token=admin_token, expected_status=200)
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
            success, message, data = make_request("post", "/articles", article_data, token=admin_token, expected_status=200)
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
                
                success, message, data = make_request("post", "/commandes", commande_data, token=admin_token, expected_status=200)
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
        
        success, message, data = make_request("post", "/alertes/test-create", alerte_data, token=admin_token, expected_status=200)
        if success and data and "id" in data:
            print(f"Created alert: {data['titre']}")
    
    print("Test data creation completed")

def test_specific_endpoints():
    print_header("TESTING SPECIFIC ENDPOINTS REPORTED WITH ISSUES")
    
    # First, authenticate to get a token
    print("Authenticating to get access token...")
    admin_token = test_auth_login(ADMIN_USER)
    
    if not admin_token:
        print("❌ Authentication failed. Cannot proceed with endpoint tests.")
        print("Trying to register a new admin user...")
        
        # Try to register a new admin user
        admin_registered = test_auth_register(ADMIN_USER)
        if admin_registered:
            admin_token = test_auth_login(ADMIN_USER)
        else:
            print("❌ Failed to register admin user. Cannot proceed with endpoint tests.")
            return False
    
    print("✅ Authentication successful. Proceeding with endpoint tests.")
    
    # Test 1: /api/fournisseurs endpoint
    print("\n--- Testing /api/fournisseurs endpoint ---")
    success, message, fournisseurs_data = make_request("get", "/fournisseurs", token=admin_token, expected_status=200)
    
    if success and isinstance(fournisseurs_data, list):
        print(f"✅ Successfully retrieved {len(fournisseurs_data)} suppliers from /api/fournisseurs")
        print(f"   Response contains {len(fournisseurs_data)} suppliers")
        if len(fournisseurs_data) > 0:
            print(f"   First supplier: {fournisseurs_data[0]['nom']} (ID: {fournisseurs_data[0]['id']})")
        test_results["fournisseurs"]["list"]["success"] = True
        test_results["fournisseurs"]["list"]["message"] = f"Successfully retrieved {len(fournisseurs_data)} suppliers"
    else:
        print(f"❌ Failed to retrieve suppliers from /api/fournisseurs")
        print(f"   Error: {message}")
        test_results["fournisseurs"]["list"]["success"] = False
        test_results["fournisseurs"]["list"]["message"] = message
    
    # Test 2: /api/articles endpoint
    print("\n--- Testing /api/articles endpoint ---")
    success, message, articles_data = make_request("get", "/articles", token=admin_token, expected_status=200)
    
    if success and isinstance(articles_data, list):
        print(f"✅ Successfully retrieved {len(articles_data)} articles from /api/articles")
        print(f"   Response contains {len(articles_data)} articles")
        if len(articles_data) > 0:
            print(f"   First article: {articles_data[0]['nom']} (ID: {articles_data[0]['id']})")
        test_results["articles"]["list"]["success"] = True
        test_results["articles"]["list"]["message"] = f"Successfully retrieved {len(articles_data)} articles"
    else:
        print(f"❌ Failed to retrieve articles from /api/articles")
        print(f"   Error: {message}")
        test_results["articles"]["list"]["success"] = False
        test_results["articles"]["list"]["message"] = message
    
    # Create test data if no suppliers or articles were found
    fournisseur_id = None
    if (not test_results["fournisseurs"]["list"]["success"] or 
        (test_results["fournisseurs"]["list"]["success"] and len(fournisseurs_data) == 0)):
        print("\n--- No suppliers found. Creating test data... ---")
        fournisseur_id = test_create_fournisseur(admin_token)
        if fournisseur_id:
            print(f"✅ Created test supplier with ID: {fournisseur_id}")
            # Test the endpoint again
            success, message, fournisseurs_data = make_request("get", "/fournisseurs", token=admin_token, expected_status=200)
            if success and isinstance(fournisseurs_data, list) and len(fournisseurs_data) > 0:
                print(f"✅ Successfully retrieved {len(fournisseurs_data)} suppliers after creating test data")
                test_results["fournisseurs"]["list"]["success"] = True
                test_results["fournisseurs"]["list"]["message"] = f"Successfully retrieved {len(fournisseurs_data)} suppliers after creating test data"
    else:
        # Use the first supplier from the list
        if len(fournisseurs_data) > 0:
            fournisseur_id = fournisseurs_data[0]['id']
    
    if (not test_results["articles"]["list"]["success"] or 
        (test_results["articles"]["list"]["success"] and len(articles_data) == 0)):
        print("\n--- No articles found. Creating test data... ---")
        # First ensure we have a supplier
        if not fournisseur_id:
            if created_ids["fournisseur"]:
                fournisseur_id = created_ids["fournisseur"]
            else:
                fournisseur_id = test_create_fournisseur(admin_token)
                if not fournisseur_id:
                    print("❌ Failed to create test supplier. Cannot create test article.")
                    return False
        
        # Create a test article
        article_id = test_create_article(admin_token, fournisseur_id)
        if article_id:
            print(f"✅ Created test article with ID: {article_id}")
            # Test the endpoint again
            success, message, articles_data = make_request("get", "/articles", token=admin_token, expected_status=200)
            if success and isinstance(articles_data, list) and len(articles_data) > 0:
                print(f"✅ Successfully retrieved {len(articles_data)} articles after creating test data")
                test_results["articles"]["list"]["success"] = True
                test_results["articles"]["list"]["message"] = f"Successfully retrieved {len(articles_data)} articles after creating test data"
    
    # Summary
    print("\n--- ENDPOINT TESTS SUMMARY ---")
    fournisseurs_status = "✅ PASSED" if test_results["fournisseurs"]["list"]["success"] else "❌ FAILED"
    articles_status = "✅ PASSED" if test_results["articles"]["list"]["success"] else "❌ FAILED"
    
    print(f"Fournisseurs endpoint: {fournisseurs_status}")
    print(f"Articles endpoint: {articles_status}")
    
    return test_results["fournisseurs"]["list"]["success"] and test_results["articles"]["list"]["success"]

def test_dashboard_stats_detailed():
    print_header("TESTING DASHBOARD STATS API")
    
    # First, authenticate to get a token
    print("Authenticating to get access token...")
    admin_token = test_auth_login(ADMIN_USER)
    
    if not admin_token:
        print("❌ Authentication failed. Cannot proceed with dashboard stats test.")
        print("Trying to register a new admin user...")
        
        # Try to register a new admin user
        admin_registered = test_auth_register(ADMIN_USER)
        if admin_registered:
            admin_token = test_auth_login(ADMIN_USER)
        else:
            print("❌ Failed to register admin user. Cannot proceed with dashboard stats test.")
            return False
    
    print("✅ Authentication successful. Proceeding with dashboard stats test.")
    
    # Test the dashboard stats endpoint
    print("\n--- Testing /api/dashboard/stats endpoint ---")
    success, message, stats_data = make_request("get", "/dashboard/stats", token=admin_token, expected_status=200)
    
    if success and isinstance(stats_data, dict):
        print(f"✅ Successfully retrieved dashboard stats from /api/dashboard/stats")
        print(f"   Response: {stats_data}")
        
        # Check if all required fields are present
        required_fields = [
            "total_fournisseurs", 
            "total_articles", 
            "total_commandes", 
            "alertes_non_lues", 
            "articles_stock_bas", 
            "commandes_en_cours"
        ]
        
        missing_fields = [field for field in required_fields if field not in stats_data]
        
        if missing_fields:
            print(f"❌ Missing fields in dashboard stats response: {', '.join(missing_fields)}")
            test_results["dashboard"]["stats"]["success"] = False
            test_results["dashboard"]["stats"]["message"] = f"Missing fields in response: {', '.join(missing_fields)}"
            return False
        
        # Check if all values are non-zero
        zero_fields = [field for field in required_fields if stats_data.get(field, 0) == 0]
        
        if zero_fields:
            print(f"⚠️ The following fields have zero values: {', '.join(zero_fields)}")
            print("Creating test data to populate these fields...")
            
            # Create test data
            create_test_data(admin_token)
            
            # Test the endpoint again
            print("\n--- Testing /api/dashboard/stats endpoint after creating test data ---")
            success, message, stats_data = make_request("get", "/dashboard/stats", token=admin_token, expected_status=200)
            
            if success and isinstance(stats_data, dict):
                print(f"✅ Successfully retrieved dashboard stats after creating test data")
                print(f"   Response: {stats_data}")
                
                # Check if values are now non-zero
                zero_fields_after = [field for field in required_fields if stats_data.get(field, 0) == 0]
                
                if zero_fields_after:
                    print(f"⚠️ The following fields still have zero values after creating test data: {', '.join(zero_fields_after)}")
                    print("This might indicate an issue with the dashboard stats calculation.")
                else:
                    print("✅ All fields now have non-zero values after creating test data.")
            else:
                print(f"❌ Failed to retrieve dashboard stats after creating test data")
                print(f"   Error: {message}")
                test_results["dashboard"]["stats"]["success"] = False
                test_results["dashboard"]["stats"]["message"] = message
                return False
        else:
            print("✅ All fields have non-zero values.")
        
        test_results["dashboard"]["stats"]["success"] = True
        test_results["dashboard"]["stats"]["message"] = "Successfully retrieved dashboard stats with all required fields"
        return True
    else:
        print(f"❌ Failed to retrieve dashboard stats from /api/dashboard/stats")
        print(f"   Error: {message}")
        test_results["dashboard"]["stats"]["success"] = False
        test_results["dashboard"]["stats"]["message"] = message
        return False

if __name__ == "__main__":
    # Test dashboard stats API
    test_dashboard_stats_detailed()