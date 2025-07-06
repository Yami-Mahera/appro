import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://56c87e94-4851-4276-b125-51277abeb343.preview.emergentagent.com/api"
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

def create_test_data_for_advanced_alerts(token):
    print_header("Creating Test Data for Advanced Alerts")
    
    # Create a test supplier with specific delivery delay
    supplier_data = {
        "nom": f"Fournisseur Alertes Avancées {uuid.uuid4().hex[:6]}",
        "code_fournisseur": f"FAA-{uuid.uuid4().hex[:6]}",
        "adresse": "456 Avenue des Tests",
        "ville": "Lyon",
        "code_postal": "69002",
        "pays": "France",
        "telephone": "+33478901234",
        "email": f"contact_{uuid.uuid4().hex[:6]}@fournisseur-alertes.com",
        "site_web": "https://www.fournisseur-alertes.com",
        "conditions_paiement": "45 jours",
        "delai_livraison_moyen": 14,  # 14 days delivery delay
        "contacts": [
            {
                "nom": "Martin",
                "prenom": "Sophie",
                "telephone": "+33612345678",
                "email": f"s.martin_{uuid.uuid4().hex[:6]}@fournisseur-alertes.com",
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
            return None, [], []
    
    # Create multiple test articles with different stock levels
    articles_data = [
        {
            "reference": f"ART-LOW-{uuid.uuid4().hex[:6]}",
            "nom": "Article Stock Très Bas",
            "description": "Article avec stock très bas pour tester les alertes",
            "famille": "Test Alertes",
            "fournisseur_id": supplier_id,
            "prix_unitaire": 29.99,
            "unite": "pièce",
            "seuil_min": 20,
            "seuil_max": 100,
            "stock_actuel": 2,  # Very low stock
            "duree_vie": 365,
            "emplacement_stockage": "Étagère B1"
        },
        {
            "reference": f"ART-MED-{uuid.uuid4().hex[:6]}",
            "nom": "Article Stock Moyen",
            "description": "Article avec stock moyen pour tester les alertes",
            "famille": "Test Alertes",
            "fournisseur_id": supplier_id,
            "prix_unitaire": 39.99,
            "unite": "pièce",
            "seuil_min": 15,
            "seuil_max": 80,
            "stock_actuel": 16,  # Just above threshold
            "duree_vie": 365,
            "emplacement_stockage": "Étagère B2"
        },
        {
            "reference": f"ART-HIGH-{uuid.uuid4().hex[:6]}",
            "nom": "Article Stock Élevé",
            "description": "Article avec stock élevé pour tester les alertes",
            "famille": "Test Alertes",
            "fournisseur_id": supplier_id,
            "prix_unitaire": 49.99,
            "unite": "pièce",
            "seuil_min": 10,
            "seuil_max": 50,
            "stock_actuel": 45,  # High stock
            "duree_vie": 365,
            "emplacement_stockage": "Étagère B3"
        }
    ]
    
    article_ids = []
    for article_data in articles_data:
        success, message, data = make_request("post", "/articles", article_data, token=token, expected_status=200)
        if success and data and "id" in data:
            print_test_result(f"Create article: {article_data['nom']}", True, f"Created article with ID: {data['id']}")
            article_ids.append(data["id"])
        else:
            print_test_result(f"Create article: {article_data['nom']}", False, message)
    
    if not article_ids:
        print("Failed to create any articles. Cannot proceed with tests.")
        return supplier_id, [], []
    
    # Create orders with different dates
    orders_data = [
        {
            "fournisseur_id": supplier_id,
            "lignes": [
                {
                    "article_id": article_ids[0] if article_ids else None,
                    "quantite": 30,
                    "prix_unitaire": 29.99,
                    "total": 899.70
                }
            ],
            "date_livraison_prevue": (datetime.now() + timedelta(days=20)).isoformat(),
            "date_production": (datetime.now() + timedelta(days=5)).isoformat(),
            "date_mise_disposition": (datetime.now() + timedelta(days=10)).isoformat(),
            "date_embarquement_cible": (datetime.now() + timedelta(days=15)).isoformat(),
            "notes": "Commande normale pour tests alertes"
        },
        {
            "fournisseur_id": supplier_id,
            "lignes": [
                {
                    "article_id": article_ids[1] if len(article_ids) > 1 else article_ids[0],
                    "quantite": 20,
                    "prix_unitaire": 39.99,
                    "total": 799.80
                }
            ],
            "date_livraison_prevue": (datetime.now() - timedelta(days=2)).isoformat(),  # Late delivery
            "date_production": (datetime.now() - timedelta(days=10)).isoformat(),
            "date_mise_disposition": (datetime.now() - timedelta(days=7)).isoformat(),
            "date_embarquement_cible": (datetime.now() - timedelta(days=5)).isoformat(),
            "notes": "Commande en retard pour tests alertes"
        }
    ]
    
    order_ids = []
    for order_data in orders_data:
        if None in [item["article_id"] for item in order_data["lignes"]]:
            continue  # Skip if article_id is None
            
        success, message, data = make_request("post", "/commandes", order_data, token=token, expected_status=200)
        if success and data and "id" in data:
            print_test_result("Create order", True, f"Created order: {data['numero_commande']}")
            order_ids.append(data["id"])
        else:
            print_test_result("Create order", False, message)
    
    # Create stock movements to simulate consumption
    if article_ids:
        for article_id in article_ids:
            # Get current stock
            success, message, article_data = make_request("get", f"/articles/{article_id}", token=token, expected_status=200)
            if success and article_data:
                current_stock = article_data.get("stock_actuel", 0)
                
                # Create a consumption movement
                movement_data = {
                    "article_id": article_id,
                    "type_mouvement": "sortie",
                    "quantite": 5,  # Consume 5 units
                    "stock_avant": current_stock,
                    "stock_apres": max(current_stock - 5, 0),
                    "reference_document": f"TEST-CONS-{uuid.uuid4().hex[:6]}",
                    "commentaire": "Consommation pour test alertes avancées"
                }
                
                success, message, data = make_request("post", "/stock/mouvements", movement_data, token=token, expected_status=200)
                if success and data and "id" in data:
                    print_test_result(f"Create consumption movement for article {article_id}", True, f"Created movement with ID: {data['id']}")
                else:
                    print_test_result(f"Create consumption movement for article {article_id}", False, message)
    
    # Create consumption forecasts
    if article_ids:
        for article_id in article_ids:
            # Create weekly forecasts for the next 10 weeks
            for week in range(1, 11):
                date_start = datetime.now() + timedelta(weeks=week-1)
                date_end = date_start + timedelta(weeks=1)
                
                forecast_data = {
                    "article_id": article_id,
                    "semaine": week,
                    "annee": date_start.year,
                    "date_debut_semaine": date_start.isoformat(),
                    "date_fin_semaine": date_end.isoformat(),
                    "quantite_prevue": 10 + week,  # Increasing consumption
                    "quantite_reelle": None if week > 1 else 10,  # Only first week has actual data
                    "ecart_absolu": None,
                    "ecart_relatif": None
                }
                
                success, message, data = make_request("post", "/stock/previsions", forecast_data, token=token, expected_status=200)
                if success and data and "id" in data:
                    if week == 1:  # Only print for first week to avoid too much output
                        print_test_result(f"Create forecast for article {article_id}, week {week}", True, f"Created forecast with ID: {data['id']}")
                else:
                    print_test_result(f"Create forecast for article {article_id}, week {week}", False, message)
    
    return supplier_id, article_ids, order_ids

def test_stock_evolution(token, article_id):
    print_header("Testing Stock Evolution Endpoint")
    
    # Test with different week parameters
    week_params = [13, 26, 52]
    
    for weeks in week_params:
        print(f"\n--- Testing Stock Evolution with {weeks} weeks ---")
        success, message, data = make_request("get", f"/stock/evolution/{article_id}?semaines={weeks}", token=token, expected_status=200)
        
        if success and isinstance(data, dict):
            print_test_result(f"Get stock evolution ({weeks} weeks)", True, f"Retrieved evolution data for {weeks} weeks")
            
            # Check if the response has the expected structure
            if "article_id" in data and "periode" in data and "evolution" in data:
                print_test_result("Evolution data structure", True, "Response has the expected structure")
                
                # Check if the number of weeks matches the request
                if f"{weeks} semaines" == data["periode"]:
                    print_test_result("Period matches request", True, f"Period is correctly set to {weeks} weeks")
                else:
                    print_test_result("Period matches request", False, f"Period is {data['periode']}, expected {weeks} semaines")
                
                # Check if evolution data is present
                if isinstance(data["evolution"], list):
                    print_test_result("Evolution data present", True, f"Evolution data contains {len(data['evolution'])} entries")
                else:
                    print_test_result("Evolution data present", False, "Evolution data is not a list")
            else:
                print_test_result("Evolution data structure", False, "Response does not have the expected structure")
        else:
            print_test_result(f"Get stock evolution ({weeks} weeks)", False, message)

def test_generate_alerts_with_data(token, article_ids):
    print_header("Testing Alert Generation with Test Data")
    
    # First, get the current state of advanced alerts
    print("\n--- Current Advanced Alerts Before Generation ---")
    success, message, before_data = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if success and isinstance(before_data, list):
        print_test_result("Get advanced alerts before generation", True, f"Retrieved {len(before_data)} advanced alerts")
        print(f"Advanced alerts before generation: {before_data}")
    else:
        print_test_result("Get advanced alerts before generation", False, message)
    
    # Generate alerts
    print("\n--- Generating Alerts ---")
    success, message, data = make_request("post", "/stock/generer-alertes", token=token, expected_status=200)
    
    if success and "message" in data:
        print_test_result("Generate alerts", True, f"{data['message']}")
        
        # Check if any alerts were generated
        if "alertes" in data and len(data["alertes"]) > 0:
            print_test_result("Alerts generated", True, f"Generated {len(data['alertes'])} alerts")
            
            # Print details of generated alerts
            for i, alert in enumerate(data["alertes"]):
                print(f"\nAlert {i+1}:")
                print(f"  Type: {alert.get('type_alerte', 'N/A')}")
                print(f"  Niveau: {alert.get('niveau_alerte', 'N/A')}")
                print(f"  Message: {alert.get('message', 'N/A')}")
                print(f"  Recommandation: {alert.get('recommandation', 'N/A')}")
        else:
            print_test_result("Alerts generated", False, "No alerts were generated. This might be expected if no conditions for alerts are met.")
    else:
        print_test_result("Generate alerts", False, message)
    
    # Get advanced alerts after generation
    print("\n--- Advanced Alerts After Generation ---")
    success, message, after_data = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if success and isinstance(after_data, list):
        print_test_result("Get advanced alerts after generation", True, f"Retrieved {len(after_data)} advanced alerts")
        
        # Check if new alerts were added
        new_alerts_count = len(after_data) - len(before_data) if isinstance(before_data, list) else len(after_data)
        if new_alerts_count > 0:
            print_test_result("New alerts added", True, f"{new_alerts_count} new alerts were added")
            
            # Print details of the new alerts
            for i, alert in enumerate(after_data[:new_alerts_count]):
                print(f"\nNew Alert {i+1}:")
                print(f"  Article ID: {alert.get('article_id', 'N/A')}")
                print(f"  Niveau: {alert.get('niveau_alerte', 'N/A')}")
                print(f"  Message: {alert.get('message', 'N/A')}")
                print(f"  Recommandation: {alert.get('recommandation', 'N/A')}")
        else:
            print_test_result("New alerts added", False, "No new alerts were added to the database")
    else:
        print_test_result("Get advanced alerts after generation", False, message)

def run_advanced_tests():
    print_header("STARTING ADVANCED ALERT SYSTEM TESTS")
    
    # Login
    token = login()
    if not token:
        return
    
    # Create test data specifically for advanced alerts
    supplier_id, article_ids, order_ids = create_test_data_for_advanced_alerts(token)
    if not article_ids:
        return
    
    # Test stock evolution endpoint
    if article_ids:
        test_stock_evolution(token, article_ids[0])
    
    # Test alert generation with the created test data
    test_generate_alerts_with_data(token, article_ids)
    
    print_header("ADVANCED ALERT SYSTEM TESTS COMPLETED")

if __name__ == "__main__":
    run_advanced_tests()