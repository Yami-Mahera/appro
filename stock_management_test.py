import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123",
    "nom": "Admin",
    "prenom": "Test",
    "role": "administrateur"
}

# Test data
test_article = None
test_fournisseur = None

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
    print_header("Logging in as Admin")
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
        return None

def setup_test_data(token):
    global test_article, test_fournisseur
    
    print_header("Setting up test data")
    
    # Create a test supplier
    fournisseur_data = {
        "nom": "Fournisseur Test Stock",
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
    
    success, message, data = make_request("post", "/fournisseurs", fournisseur_data, token=token, expected_status=200)
    if success and data and "id" in data:
        print_test_result("Create test supplier", True, f"Created supplier: {data['nom']}")
        test_fournisseur = data
        
        # Create a test article
        article_data = {
            "reference": f"ART-{uuid.uuid4().hex[:6]}",
            "nom": "Article Test Stock",
            "description": "Article pour tester la gestion des stocks",
            "famille": "Test",
            "fournisseur_id": test_fournisseur["id"],
            "prix_unitaire": 19.99,
            "unite": "pièce",
            "seuil_min": 10,
            "seuil_max": 100,
            "stock_actuel": 50,
            "duree_vie": 365,
            "emplacement_stockage": "Étagère A1"
        }
        
        success, message, data = make_request("post", "/articles", article_data, token=token, expected_status=200)
        if success and data and "id" in data:
            print_test_result("Create test article", True, f"Created article: {data['nom']}")
            test_article = data
            return True
        else:
            print_test_result("Create test article", False, message)
            return False
    else:
        print_test_result("Create test supplier", False, message)
        return False

def test_create_mouvement_stock(token):
    print_header("Testing POST /api/stock/mouvements")
    
    if not test_article:
        print_test_result("Create mouvement stock", False, "No test article available")
        return False
    
    # Test with valid data - stock entry
    mouvement_data = {
        "article_id": test_article["id"],
        "type_mouvement": "entree",
        "quantite": 10,
        "stock_avant": test_article["stock_actuel"],
        "stock_apres": test_article["stock_actuel"] + 10,
        "reference_document": "BON-LIVRAISON-123",
        "commentaire": "Livraison standard"
    }
    
    success, message, data = make_request("post", "/stock/mouvements", mouvement_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Create stock entry movement", True, f"Created movement with ID: {data['id']}")
        
        # Test with valid data - stock exit
        mouvement_data = {
            "article_id": test_article["id"],
            "type_mouvement": "sortie",
            "quantite": 5,
            "stock_avant": test_article["stock_actuel"] + 10,
            "stock_apres": test_article["stock_actuel"] + 5,
            "reference_document": "BON-SORTIE-456",
            "commentaire": "Consommation interne"
        }
        
        success, message, data = make_request("post", "/stock/mouvements", mouvement_data, token=token, expected_status=200)
        
        if success and data and "id" in data:
            print_test_result("Create stock exit movement", True, f"Created movement with ID: {data['id']}")
            return True
        else:
            print_test_result("Create stock exit movement", False, message)
            return False
    else:
        print_test_result("Create stock entry movement", False, message)
        return False

def test_get_mouvements_stock(token):
    print_header("Testing GET /api/stock/mouvements/{article_id}")
    
    if not test_article:
        print_test_result("Get mouvements stock", False, "No test article available")
        return False
    
    success, message, data = make_request("get", f"/stock/mouvements/{test_article['id']}", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get stock movements", True, f"Retrieved {len(data)} movements")
        
        # Verify the format of the returned data
        if len(data) > 0:
            movement = data[0]
            required_fields = ["id", "article_id", "type_mouvement", "quantite", "stock_avant", "stock_apres", "date_mouvement"]
            all_fields_present = all(field in movement for field in required_fields)
            
            if all_fields_present:
                print_test_result("Movement data format", True, "All required fields are present")
            else:
                print_test_result("Movement data format", False, f"Missing fields: {[f for f in required_fields if f not in movement]}")
        
        return True
    else:
        print_test_result("Get stock movements", False, message)
        return False

def test_get_calcul_couverture(token):
    print_header("Testing GET /api/stock/couverture/{article_id}")
    
    if not test_article:
        print_test_result("Get calcul couverture", False, "No test article available")
        return False
    
    success, message, data = make_request("get", f"/stock/couverture/{test_article['id']}", token=token, expected_status=200)
    
    if success and isinstance(data, dict):
        print_test_result("Get stock coverage calculation", True, "Retrieved coverage metrics")
        
        # Verify the metrics
        required_metrics = [
            "couverture_minimale_securite", 
            "couverture_maximale_commande", 
            "quantite_maximale_commande",
            "couverture_actuelle",
            "variation_logistique",
            "variation_prevision",
            "horizon"
        ]
        
        all_metrics_present = all(metric in data for metric in required_metrics)
        
        if all_metrics_present:
            print_test_result("Coverage metrics", True, "All required metrics are present")
            
            # Check if the calculations make sense
            cms = data["couverture_minimale_securite"]
            cmc = data["couverture_maximale_commande"]
            qm = data["quantite_maximale_commande"]
            cr = data["couverture_actuelle"]
            
            # CMS should be positive
            if cms >= 0:
                print_test_result("CMS calculation", True, f"CMS = {cms}")
            else:
                print_test_result("CMS calculation", False, f"CMS is negative: {cms}")
            
            # CMC should be positive
            if cmc >= 0:
                print_test_result("CMC calculation", True, f"CMC = {cmc}")
            else:
                print_test_result("CMC calculation", False, f"CMC is negative: {cmc}")
            
            # QM should be positive
            if qm >= 0:
                print_test_result("QM calculation", True, f"QM = {qm}")
            else:
                print_test_result("QM calculation", False, f"QM is negative: {qm}")
            
            # CR should be positive
            if cr >= 0:
                print_test_result("CR calculation", True, f"CR = {cr}")
            else:
                print_test_result("CR calculation", False, f"CR is negative: {cr}")
            
            # QM should be CMC - CR
            if abs(qm - (cmc - cr)) < 0.01:  # Allow for small floating point differences
                print_test_result("QM formula verification", True, f"QM = CMC - CR: {qm} ≈ {cmc} - {cr}")
            else:
                print_test_result("QM formula verification", False, f"QM ≠ CMC - CR: {qm} ≠ {cmc} - {cr}")
        else:
            print_test_result("Coverage metrics", False, f"Missing metrics: {[m for m in required_metrics if m not in data]}")
        
        return True
    else:
        print_test_result("Get stock coverage calculation", False, message)
        return False

def test_get_evolution_stock(token):
    print_header("Testing GET /api/stock/evolution/{article_id}")
    
    if not test_article:
        print_test_result("Get evolution stock", False, "No test article available")
        return False
    
    # Test with default period (26 weeks)
    success, message, data = make_request("get", f"/stock/evolution/{test_article['id']}", token=token, expected_status=200)
    
    if success and isinstance(data, dict):
        print_test_result("Get stock evolution (default period)", True, f"Retrieved evolution data for {data.get('periode', 'unknown')} period")
        
        # Check if the evolution data is present
        if "evolution" in data and isinstance(data["evolution"], list):
            print_test_result("Evolution data format", True, f"Retrieved {len(data['evolution'])} data points")
        else:
            print_test_result("Evolution data format", False, "Missing evolution data")
        
        # Test with custom period (10 weeks)
        success, message, data = make_request("get", f"/stock/evolution/{test_article['id']}?semaines=10", token=token, expected_status=200)
        
        if success and isinstance(data, dict):
            print_test_result("Get stock evolution (custom period)", True, f"Retrieved evolution data for {data.get('periode', 'unknown')} period")
            
            # Check if the evolution data is present and has the correct number of data points
            if "evolution" in data and isinstance(data["evolution"], list):
                if len(data["evolution"]) == 10:
                    print_test_result("Custom period data points", True, f"Retrieved exactly 10 data points")
                else:
                    print_test_result("Custom period data points", False, f"Expected 10 data points, got {len(data['evolution'])}")
            else:
                print_test_result("Custom period data format", False, "Missing evolution data")
            
            return True
        else:
            print_test_result("Get stock evolution (custom period)", False, message)
            return False
    else:
        print_test_result("Get stock evolution (default period)", False, message)
        return False

def test_get_alertes_avancees(token):
    print_header("Testing GET /api/stock/alertes-avancees")
    
    success, message, data = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get advanced alerts", True, f"Retrieved {len(data)} alerts")
        return True
    else:
        print_test_result("Get advanced alerts", False, message)
        return False

def test_generer_alertes(token):
    print_header("Testing POST /api/stock/generer-alertes")
    
    success, message, data = make_request("post", "/stock/generer-alertes", {}, token=token, expected_status=200)
    
    if success and isinstance(data, dict):
        print_test_result("Generate alerts", True, f"Generated {data.get('message', 'unknown number of')} alerts")
        
        # Check if the generated alerts are returned
        if "alertes" in data and isinstance(data["alertes"], list):
            print_test_result("Generated alerts data", True, f"Returned {len(data['alertes'])} generated alerts")
        else:
            print_test_result("Generated alerts data", False, "Missing generated alerts data")
        
        return True
    else:
        print_test_result("Generate alerts", False, message)
        return False

def test_create_prevision(token):
    print_header("Testing POST /api/stock/previsions")
    
    if not test_article:
        print_test_result("Create prevision", False, "No test article available")
        return False
    
    # Get current week number and year
    today = datetime.now()
    week_number = today.isocalendar()[1]
    year = today.year
    
    # Calculate start and end of the week
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    prevision_data = {
        "article_id": test_article["id"],
        "semaine": week_number,
        "annee": year,
        "date_debut_semaine": start_of_week.isoformat(),
        "date_fin_semaine": end_of_week.isoformat(),
        "quantite_prevue": 15.0,
        "quantite_reelle": None,
        "ecart_absolu": None,
        "ecart_relatif": None
    }
    
    success, message, data = make_request("post", "/stock/previsions", prevision_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Create consumption forecast", True, f"Created forecast with ID: {data['id']}")
        return True
    else:
        print_test_result("Create consumption forecast", False, message)
        return False

def test_get_previsions(token):
    print_header("Testing GET /api/stock/previsions/{article_id}")
    
    if not test_article:
        print_test_result("Get previsions", False, "No test article available")
        return False
    
    success, message, data = make_request("get", f"/stock/previsions/{test_article['id']}", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get consumption forecasts", True, f"Retrieved {len(data)} forecasts")
        
        # Verify the format of the returned data
        if len(data) > 0:
            forecast = data[0]
            required_fields = ["id", "article_id", "semaine", "annee", "date_debut_semaine", "date_fin_semaine", "quantite_prevue"]
            all_fields_present = all(field in forecast for field in required_fields)
            
            if all_fields_present:
                print_test_result("Forecast data format", True, "All required fields are present")
            else:
                print_test_result("Forecast data format", False, f"Missing fields: {[f for f in required_fields if f not in forecast]}")
        
        # Test with custom period
        success, message, data = make_request("get", f"/stock/previsions/{test_article['id']}?semaines=10", token=token, expected_status=200)
        
        if success and isinstance(data, list):
            print_test_result("Get forecasts with custom period", True, f"Retrieved {len(data)} forecasts")
            return True
        else:
            print_test_result("Get forecasts with custom period", False, message)
            return False
    else:
        print_test_result("Get consumption forecasts", False, message)
        return False

def run_tests():
    print_header("STARTING STOCK MANAGEMENT API TESTS")
    
    # Login
    token = login()
    if not token:
        print("Authentication failed, cannot proceed with tests")
        return
    
    # Setup test data
    if not setup_test_data(token):
        print("Failed to set up test data, cannot proceed with tests")
        return
    
    # Run tests
    test_create_mouvement_stock(token)
    test_get_mouvements_stock(token)
    test_get_calcul_couverture(token)
    test_get_evolution_stock(token)
    test_get_alertes_avancees(token)
    test_generer_alertes(token)
    test_create_prevision(token)
    test_get_previsions(token)
    
    print_header("STOCK MANAGEMENT API TESTS COMPLETED")

if __name__ == "__main__":
    run_tests()