import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Configuration
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

API_BASE_URL = f"{BACKEND_URL}/api"

# Test user credentials
TEST_USER = {
    "email": "test_alertes_cliquables@example.com",
    "password": "Password123!",
    "nom": "Test",
    "prenom": "Alertes Cliquables",
    "role": "administrateur"
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
    
    url = f"{API_BASE_URL}{endpoint}"
    
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

def authenticate():
    print_header("Authenticating")
    
    # Try to login first
    success, message, data = make_request("post", "/auth/login", {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    
    if success and data and "access_token" in data:
        print_test_result("Login", True, f"Logged in as {TEST_USER['email']}")
        return data["access_token"]
    
    # If login fails, try to register
    print("Login failed, trying to register...")
    success, message, data = make_request("post", "/auth/register", TEST_USER)
    
    if success:
        print_test_result("Register", True, f"Registered as {TEST_USER['email']}")
        
        # Now try to login again
        success, message, data = make_request("post", "/auth/login", {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        
        if success and data and "access_token" in data:
            print_test_result("Login after register", True, f"Logged in as {TEST_USER['email']}")
            return data["access_token"]
    
    print_test_result("Authentication", False, "Failed to authenticate")
    return None

def create_test_data(token):
    print_header("Creating Test Data")
    
    # Create a test supplier
    supplier_data = {
        "nom": f"Fournisseur Test Alertes Cliquables {uuid.uuid4().hex[:6]}",
        "code_fournisseur": f"FTAC-{uuid.uuid4().hex[:6]}",
        "adresse": "123 Rue des Tests",
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
    
    success, message, data = make_request("post", "/fournisseurs", supplier_data, token=token)
    
    if success and data and "id" in data:
        print_test_result("Create supplier", True, f"Created supplier: {data['nom']}")
        supplier_id = data["id"]
    else:
        print_test_result("Create supplier", False, message)
        # Try to get an existing supplier
        success, message, suppliers = make_request("get", "/fournisseurs", token=token)
        if success and suppliers and len(suppliers) > 0:
            supplier_id = suppliers[0]["id"]
            print_test_result("Use existing supplier", True, f"Using existing supplier: {suppliers[0]['nom']}")
        else:
            print("Failed to create or find a supplier. Cannot proceed with tests.")
            return None, None, None
    
    # Create a test article
    article_data = {
        "reference": f"ART-{uuid.uuid4().hex[:6]}",
        "nom": "Article Test Alertes Cliquables",
        "description": "Article pour tester les alertes cliquables",
        "famille": "Test",
        "fournisseur_id": supplier_id,
        "prix_unitaire": 19.99,
        "unite": "pièce",
        "seuil_min": 10,
        "seuil_max": 100,
        "stock_actuel": 5,  # Below seuil_min to trigger stock_bas alert
        "duree_vie": 365,
        "emplacement_stockage": "Étagère A1"
    }
    
    success, message, data = make_request("post", "/articles", article_data, token=token)
    
    if success and data and "id" in data:
        print_test_result("Create article", True, f"Created article: {data['nom']}")
        article_id = data["id"]
    else:
        print_test_result("Create article", False, message)
        # Try to get an existing article
        success, message, articles = make_request("get", "/articles", token=token)
        if success and articles and len(articles) > 0:
            article_id = articles[0]["id"]
            print_test_result("Use existing article", True, f"Using existing article: {articles[0]['nom']}")
        else:
            print("Failed to create or find an article. Cannot proceed with tests.")
            return supplier_id, None, None
    
    # Create a test order
    order_data = {
        "fournisseur_id": supplier_id,
        "lignes": [
            {
                "article_id": article_id,
                "quantite": 20,
                "prix_unitaire": 19.99,
                "total": 399.80
            }
        ],
        "date_livraison_prevue": (datetime.now() + timedelta(days=7)).isoformat(),
        "date_production": (datetime.now() + timedelta(days=2)).isoformat(),
        "date_mise_disposition": (datetime.now() + timedelta(days=4)).isoformat(),
        "date_embarquement_cible": (datetime.now() + timedelta(days=5)).isoformat(),
        "notes": "Commande test pour alertes cliquables"
    }
    
    success, message, data = make_request("post", "/commandes", order_data, token=token)
    
    if success and data and "id" in data:
        print_test_result("Create order", True, f"Created order: {data['numero_commande']}")
        order_id = data["id"]
    else:
        print_test_result("Create order", False, message)
        # Try to get an existing order
        success, message, orders = make_request("get", "/commandes", token=token)
        if success and orders and len(orders) > 0:
            order_id = orders[0]["id"]
            print_test_result("Use existing order", True, f"Using existing order: {orders[0]['numero_commande']}")
        else:
            print("Failed to create or find an order. Some tests may fail.")
            order_id = None
    
    return supplier_id, article_id, order_id

def test_alertes_cliquables(token, article_id, order_id, supplier_id):
    print_header("Testing Alertes Cliquables Feature")
    
    # Test 1: Create an alert with all related entity IDs
    print("\n--- Test 1: Create Alert with Related Entities ---")
    
    alert_data = {
        "type": "stock_bas",
        "priorite": "high",
        "titre": "Alerte test cliquable",
        "message": "Cette alerte est utilisée pour tester la fonctionnalité des alertes cliquables",
        "article_id": article_id,
        "commande_id": order_id,
        "fournisseur_id": supplier_id,
        "lue": False
    }
    
    success, message, data = make_request("post", "/alertes/test-create", alert_data, token=token)
    
    if success and isinstance(data, dict) and "id" in data:
        print_test_result("Create alert with related entities", True, f"Created alert with ID: {data['id']}")
        alert_id = data["id"]
        
        # Test 2: Get the alert and verify it has all related entity IDs
        print("\n--- Test 2: Verify Alert Has Related Entity IDs ---")
        success, message, alerts = make_request("get", "/alertes", token=token)
        
        if success and isinstance(alerts, list):
            alert = next((a for a in alerts if a["id"] == alert_id), None)
            
            if alert:
                has_article_id = "article_id" in alert and alert["article_id"] == article_id
                has_commande_id = "commande_id" in alert and alert["commande_id"] == order_id
                has_fournisseur_id = "fournisseur_id" in alert and alert["fournisseur_id"] == supplier_id
                
                print_test_result("Alert has article_id", has_article_id, 
                                 f"article_id: {alert.get('article_id', 'missing')}")
                print_test_result("Alert has commande_id", has_commande_id, 
                                 f"commande_id: {alert.get('commande_id', 'missing')}")
                print_test_result("Alert has fournisseur_id", has_fournisseur_id, 
                                 f"fournisseur_id: {alert.get('fournisseur_id', 'missing')}")
            else:
                print_test_result("Find created alert", False, "Could not find the created alert")
        else:
            print_test_result("Get alerts", False, message)
        
        # Test 3: Test the mark-as-read API
        print("\n--- Test 3: Test Mark Alert as Read API ---")
        success, message, data = make_request("put", f"/alertes/{alert_id}/marquer-lue", token=token)
        
        if success:
            print_test_result("Mark alert as read", True, "Successfully marked alert as read")
            
            # Verify it's marked as read
            success, message, alerts = make_request("get", "/alertes", token=token)
            
            if success and isinstance(alerts, list):
                alert = next((a for a in alerts if a["id"] == alert_id), None)
                
                if alert and alert["lue"]:
                    print_test_result("Verify alert is marked as read", True, "Alert is correctly marked as read")
                else:
                    print_test_result("Verify alert is marked as read", False, "Alert was not correctly marked as read")
            else:
                print_test_result("Get alerts after marking as read", False, message)
        else:
            print_test_result("Mark alert as read", False, message)
    else:
        print_test_result("Create alert with related entities", False, message)
    
    # Test 4: Verify the related entity APIs work
    print("\n--- Test 4: Verify Related Entity APIs ---")
    
    # Test article API
    success, message, data = make_request("get", f"/articles/{article_id}", token=token)
    print_test_result("Get article by ID", success, 
                     f"Successfully retrieved article: {data['nom'] if success and 'nom' in data else ''}" if success 
                     else message)
    
    # Test commande API
    if order_id:
        success, message, data = make_request("get", f"/commandes/{order_id}", token=token)
        print_test_result("Get commande by ID", success, 
                         f"Successfully retrieved commande: {data['numero_commande'] if success and 'numero_commande' in data else ''}" if success 
                         else message)
    
    # Test fournisseur API
    success, message, data = make_request("get", f"/fournisseurs/{supplier_id}", token=token)
    print_test_result("Get fournisseur by ID", success, 
                     f"Successfully retrieved fournisseur: {data['nom'] if success and 'nom' in data else ''}" if success 
                     else message)
    
    print("\n--- Alertes Cliquables Feature Tests Completed ---")
    return True

def run_tests():
    print_header("STARTING ALERTES CLIQUABLES BACKEND TESTS")
    
    # Authenticate
    token = authenticate()
    if not token:
        print("Authentication failed, cannot proceed with tests")
        return False
    
    # Create test data
    supplier_id, article_id, order_id = create_test_data(token)
    if not article_id:
        print("Failed to create test data, cannot proceed with tests")
        return False
    
    # Run tests
    test_alertes_cliquables(token, article_id, order_id, supplier_id)
    
    print_header("ALERTES CLIQUABLES BACKEND TESTS COMPLETED")
    return True

if __name__ == "__main__":
    run_tests()