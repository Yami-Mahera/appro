import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BASE_URL = line.strip().split('=')[1].strip('"\'') + "/api"
            break
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123",
    "nom": "Admin",
    "prenom": "Test",
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
        "email": ADMIN_USER["email"],
        "password": ADMIN_USER["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Login", True, f"Logged in as: {ADMIN_USER['email']}")
        return data["access_token"]
    else:
        print_test_result("Login", False, message)
        # Try to register if login fails
        register_success, register_message, register_data = make_request("post", "/auth/register", ADMIN_USER, expected_status=200)
        if register_success:
            print_test_result("Register", True, f"Registered user: {ADMIN_USER['email']}")
            # Try login again
            success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
            if success and data and "access_token" in data:
                print_test_result("Login after register", True, f"Logged in as: {ADMIN_USER['email']}")
                return data["access_token"]
        
        print("Failed to authenticate. Cannot proceed with tests.")
        return None

def create_test_data(token):
    print_header("Creating Test Data")
    
    # Create a test supplier
    supplier_data = {
        "nom": f"Fournisseur Test Alertes {uuid.uuid4().hex[:6]}",
        "code_fournisseur": f"FTA-{uuid.uuid4().hex[:6]}",
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
    
    success, message, data = make_request("post", "/fournisseurs", supplier_data, token=token, expected_status=200)
    if success and data and "id" in data:
        print_test_result("Create supplier", True, f"Created supplier: {data['nom']}")
        supplier_id = data["id"]
    else:
        print_test_result("Create supplier", False, message)
        # Try to get an existing supplier
        success, message, suppliers = make_request("get", "/fournisseurs", token=token, expected_status=200)
        if success and suppliers and len(suppliers) > 0:
            supplier_id = suppliers[0]["id"]
            print_test_result("Use existing supplier", True, f"Using existing supplier: {suppliers[0]['nom']}")
        else:
            print("Failed to create or find a supplier. Cannot proceed with tests.")
            return None, None, None
    
    # Create a test article
    article_data = {
        "reference": f"ART-{uuid.uuid4().hex[:6]}",
        "nom": "Article Test Alertes",
        "description": "Article pour tester les alertes",
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
    
    success, message, data = make_request("post", "/articles", article_data, token=token, expected_status=200)
    if success and data and "id" in data:
        print_test_result("Create article", True, f"Created article: {data['nom']}")
        article_id = data["id"]
    else:
        print_test_result("Create article", False, message)
        # Try to get an existing article
        success, message, articles = make_request("get", "/articles", token=token, expected_status=200)
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
        "notes": "Commande test pour alertes"
    }
    
    success, message, data = make_request("post", "/commandes", order_data, token=token, expected_status=200)
    if success and data and "id" in data:
        print_test_result("Create order", True, f"Created order: {data['numero_commande']}")
        order_id = data["id"]
    else:
        print_test_result("Create order", False, message)
        # Try to get an existing order
        success, message, orders = make_request("get", "/commandes", token=token, expected_status=200)
        if success and orders and len(orders) > 0:
            order_id = orders[0]["id"]
            print_test_result("Use existing order", True, f"Using existing order: {orders[0]['numero_commande']}")
        else:
            print("Failed to create or find an order. Some tests may fail.")
            order_id = None
    
    return supplier_id, article_id, order_id

def test_basic_alerts(token, article_id, order_id):
    print_header("Testing Basic Alert System (/api/alertes)")
    
    # Create test alerts
    alerts_to_create = [
        {
            "type": "stock_bas",
            "priorite": "high",
            "titre": "Stock bas - Article test",
            "message": "Le stock de l'article test est en dessous du seuil minimum",
            "article_id": article_id,
            "lue": False
        },
        {
            "type": "retard_livraison",
            "priorite": "medium",
            "titre": "Retard de livraison",
            "message": "La commande est en retard de livraison",
            "commande_id": order_id,
            "lue": False
        }
    ]
    
    alert_ids = []
    for alert_data in alerts_to_create:
        success, message, data = make_request("post", "/alertes/test-create", alert_data, token=token, expected_status=200)
        if success and data and "id" in data:
            print_test_result(f"Create alert: {alert_data['type']}", True, f"Created alert: {data['titre']}")
            alert_ids.append(data["id"])
        else:
            print_test_result(f"Create alert: {alert_data['type']}", False, message)
    
    # Test 1: Get all alerts
    print("\n--- Test 1: Get All Alerts ---")
    success, message, data = make_request("get", "/alertes", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get all alerts", True, f"Retrieved {len(data)} alerts")
        
        # Check if alerts are sorted by date (newest first)
        is_sorted = all(data[i]["created_at"] >= data[i+1]["created_at"] for i in range(len(data)-1)) if len(data) > 1 else True
        print_test_result("Alerts sorted by date", is_sorted, 
                         "Alerts are correctly sorted by date (newest first)" if is_sorted 
                         else "Alerts are NOT sorted by date correctly")
    else:
        print_test_result("Get all alerts", False, message)
    
    # Test 2: Get unread alerts
    print("\n--- Test 2: Get Unread Alerts ---")
    success, message, data = make_request("get", "/alertes?lue=false", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get unread alerts", True, f"Retrieved {len(data)} unread alerts")
        
        # Verify all retrieved alerts are unread
        all_unread = all(not alert["lue"] for alert in data)
        print_test_result("All alerts unread", all_unread, 
                         "All retrieved alerts are correctly marked as unread" if all_unread 
                         else "Some retrieved alerts are incorrectly marked as read")
    else:
        print_test_result("Get unread alerts", False, message)
    
    # Test 3: Mark an alert as read
    print("\n--- Test 3: Mark Alert as Read ---")
    if alert_ids:
        # Mark the first alert as read
        success, message, data = make_request("put", f"/alertes/{alert_ids[0]}/marquer-lue", token=token, expected_status=200)
        
        if success:
            print_test_result("Mark alert as read", True, f"Successfully marked alert {alert_ids[0]} as read")
            
            # Verify it's now marked as read
            success, message, alerts = make_request("get", "/alertes", token=token, expected_status=200)
            if success:
                found_alert = next((a for a in alerts if a["id"] == alert_ids[0]), None)
                if found_alert and found_alert["lue"]:
                    print_test_result("Alert marked as read verification", True, "Alert is correctly marked as read in the database")
                else:
                    print_test_result("Alert marked as read verification", False, "Alert was not correctly marked as read in the database")
        else:
            print_test_result("Mark alert as read", False, message)
    else:
        print_test_result("Mark alert as read", False, "No alert IDs available for testing")
    
    return alert_ids

def test_advanced_alerts(token, article_id):
    print_header("Testing Advanced Alert System (/api/stock/alertes-avancees)")
    
    # Test 1: Get advanced alerts
    print("\n--- Test 1: Get Advanced Alerts ---")
    success, message, data = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get advanced alerts", True, f"Retrieved {len(data)} advanced alerts")
        print(f"Advanced alerts: {data}")
    else:
        print_test_result("Get advanced alerts", False, message)
    
    # Test 2: Generate alerts
    print("\n--- Test 2: Generate Alerts ---")
    success, message, data = make_request("post", "/stock/generer-alertes", token=token, expected_status=200)
    
    if success and "message" in data:
        print_test_result("Generate alerts", True, f"{data['message']}")
        print(f"Generated alerts: {data.get('alertes', [])}")
        
        # Check if any alerts were generated
        if "alertes" in data and len(data["alertes"]) > 0:
            print_test_result("Alerts generated", True, f"Generated {len(data['alertes'])} alerts")
        else:
            print_test_result("Alerts generated", False, "No alerts were generated. This might be expected if no conditions for alerts are met.")
    else:
        print_test_result("Generate alerts", False, message)
    
    # Test 3: Get advanced alerts again to see if any were generated
    print("\n--- Test 3: Get Advanced Alerts After Generation ---")
    success, message, data = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get advanced alerts after generation", True, f"Retrieved {len(data)} advanced alerts")
        print(f"Advanced alerts after generation: {data}")
    else:
        print_test_result("Get advanced alerts after generation", False, message)

def test_stock_coverage(token, article_id):
    print_header("Testing Stock Coverage Endpoints")
    
    # Test 1: Get stock coverage for an article
    print("\n--- Test 1: Get Stock Coverage ---")
    success, message, data = make_request("get", f"/stock/couverture/{article_id}", token=token, expected_status=200)
    
    if success and isinstance(data, dict):
        print_test_result("Get stock coverage", True, f"Retrieved stock coverage for article {article_id}")
        print(f"Stock coverage data: {data}")
        
        # Check if all required fields are present
        required_fields = [
            "couverture_minimale_securite",  # CMS
            "couverture_maximale_commande",  # CMC
            "quantite_maximale_commande",    # QM
            "couverture_actuelle"            # CR
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print_test_result("Coverage data completeness", False, f"Missing fields: {', '.join(missing_fields)}")
        else:
            print_test_result("Coverage data completeness", True, "All required fields are present")
            
            # Check the formula QM = CMC - CR
            cms = data["couverture_minimale_securite"]
            cmc = data["couverture_maximale_commande"]
            qm = data["quantite_maximale_commande"]
            cr = data["couverture_actuelle"]
            
            expected_qm = max(cmc - cr, 0)
            qm_formula_correct = abs(qm - expected_qm) < 0.01  # Allow for small floating point differences
            
            print_test_result("QM formula check", qm_formula_correct, 
                             f"QM formula is correct: {qm} ≈ max({cmc} - {cr}, 0) = {expected_qm}" if qm_formula_correct 
                             else f"QM formula is incorrect: {qm} ≠ max({cmc} - {cr}, 0) = {expected_qm}")
    else:
        print_test_result("Get stock coverage", False, message)

def test_stock_movements(token, article_id):
    print_header("Testing Stock Movements Endpoints")
    
    # Create a test stock movement
    movement_data = {
        "article_id": article_id,
        "type_mouvement": "entree",
        "quantite": 15,
        "stock_avant": 5,
        "stock_apres": 20,
        "reference_document": f"TEST-{uuid.uuid4().hex[:6]}",
        "commentaire": "Mouvement de test pour API"
    }
    
    # Test 1: Create a stock movement
    print("\n--- Test 1: Create Stock Movement ---")
    success, message, data = make_request("post", "/stock/mouvements", movement_data, token=token, expected_status=200)
    
    if success and isinstance(data, dict) and "id" in data:
        print_test_result("Create stock movement", True, f"Created stock movement with ID: {data['id']}")
        movement_id = data["id"]
    else:
        print_test_result("Create stock movement", False, message)
        movement_id = None
    
    # Test 2: Get stock movements for an article
    print("\n--- Test 2: Get Stock Movements ---")
    success, message, data = make_request("get", f"/stock/mouvements/{article_id}", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get stock movements", True, f"Retrieved {len(data)} stock movements for article {article_id}")
        print(f"First movement: {data[0] if data else 'No movements found'}")
    else:
        print_test_result("Get stock movements", False, message)

def run_all_tests():
    print_header("STARTING ALERT SYSTEM TESTS")
    
    # Login
    token = login()
    if not token:
        return
    
    # Create test data
    supplier_id, article_id, order_id = create_test_data(token)
    if not article_id:
        return
    
    # Run tests
    test_basic_alerts(token, article_id, order_id)
    test_advanced_alerts(token, article_id)
    test_stock_coverage(token, article_id)
    test_stock_movements(token, article_id)
    
    print_header("ALERT SYSTEM TESTS COMPLETED")

if __name__ == "__main__":
    run_all_tests()