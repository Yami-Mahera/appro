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
    "password": "admin123"
}

# Test results
test_results = {
    "stock_evolution": {
        "default": {"success": False, "message": "Not tested"},
        "13_weeks": {"success": False, "message": "Not tested"},
        "26_weeks": {"success": False, "message": "Not tested"},
        "52_weeks": {"success": False, "message": "Not tested"}
    },
    "stock_couverture": {
        "metrics": {"success": False, "message": "Not tested"}
    },
    "commandes_validation": {
        "basic": {"success": False, "message": "Not tested"},
        "constraints": {"success": False, "message": "Not tested"}
    },
    "articles_filters": {
        "search": {"success": False, "message": "Not tested"},
        "famille": {"success": False, "message": "Not tested"},
        "fournisseur": {"success": False, "message": "Not tested"},
        "stock_bas": {"success": False, "message": "Not tested"}
    },
    "fournisseurs_filters": {
        "search": {"success": False, "message": "Not tested"},
        "ville": {"success": False, "message": "Not tested"},
        "pays": {"success": False, "message": "Not tested"}
    },
    "commandes_filters": {
        "status": {"success": False, "message": "Not tested"},
        "fournisseur": {"success": False, "message": "Not tested"},
        "date_range": {"success": False, "message": "Not tested"}
    }
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

def make_request(method, endpoint, data=None, params=None, token=None, expected_status=200):
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

def get_test_article_id(token):
    """Get an article ID for testing"""
    success, message, data = make_request("get", "/articles", token=token, expected_status=200)
    
    if success and isinstance(data, list) and len(data) > 0:
        return data[0]["id"]
    else:
        # Create a test article if none exists
        print("No articles found, creating a test article...")
        
        # First get a supplier
        success, message, suppliers = make_request("get", "/fournisseurs", token=token, expected_status=200)
        if not success or not suppliers or len(suppliers) == 0:
            # Create a supplier if none exists
            supplier_data = {
                "nom": f"Test Supplier {uuid.uuid4().hex[:6]}",
                "code_fournisseur": f"SUP-{uuid.uuid4().hex[:6]}",
                "adresse": "123 Test Street",
                "ville": "Test City",
                "code_postal": "12345",
                "pays": "Test Country",
                "delai_livraison_moyen": 7
            }
            success, message, supplier = make_request("post", "/fournisseurs", supplier_data, token=token, expected_status=200)
            if not success:
                print(f"Failed to create supplier: {message}")
                return None
            supplier_id = supplier["id"]
        else:
            supplier_id = suppliers[0]["id"]
        
        # Create an article
        article_data = {
            "reference": f"ART-{uuid.uuid4().hex[:6]}",
            "nom": "Test Article",
            "description": "Test article for API testing",
            "famille": "Test",
            "fournisseur_id": supplier_id,
            "prix_unitaire": 19.99,
            "unite": "pièce",
            "seuil_min": 10,
            "seuil_max": 100,
            "stock_actuel": 15,
            "duree_vie": 365
        }
        
        success, message, article = make_request("post", "/articles", article_data, token=token, expected_status=200)
        if success and article and "id" in article:
            return article["id"]
    
    return None

def get_test_fournisseur_id(token):
    """Get a supplier ID for testing"""
    success, message, data = make_request("get", "/fournisseurs", token=token, expected_status=200)
    
    if success and isinstance(data, list) and len(data) > 0:
        return data[0]["id"]
    
    return None

def get_test_commande_id(token):
    """Get an order ID for testing"""
    success, message, data = make_request("get", "/commandes", token=token, expected_status=200)
    
    if success and isinstance(data, list) and len(data) > 0:
        return data[0]["id"]
    
    return None

def test_stock_evolution(token, article_id):
    print_header("Testing Stock Evolution API")
    
    # Test with default parameters
    success, message, data = make_request("get", f"/stock/evolution/{article_id}", token=token, expected_status=200)
    
    if success and data and "evolution" in data:
        print_test_result("Stock evolution (default)", True, f"Retrieved evolution data with {len(data['evolution'])} entries")
        test_results["stock_evolution"]["default"]["success"] = True
        test_results["stock_evolution"]["default"]["message"] = f"Successfully retrieved evolution data with {len(data['evolution'])} entries"
    else:
        print_test_result("Stock evolution (default)", False, message)
        test_results["stock_evolution"]["default"]["message"] = message
    
    # Test with 13 weeks
    success, message, data = make_request("get", f"/stock/evolution/{article_id}", params={"semaines": 13}, token=token, expected_status=200)
    
    if success and data and "evolution" in data:
        print_test_result("Stock evolution (13 weeks)", True, f"Retrieved evolution data with {len(data['evolution'])} entries")
        test_results["stock_evolution"]["13_weeks"]["success"] = True
        test_results["stock_evolution"]["13_weeks"]["message"] = f"Successfully retrieved evolution data with {len(data['evolution'])} entries"
    else:
        print_test_result("Stock evolution (13 weeks)", False, message)
        test_results["stock_evolution"]["13_weeks"]["message"] = message
    
    # Test with 26 weeks
    success, message, data = make_request("get", f"/stock/evolution/{article_id}", params={"semaines": 26}, token=token, expected_status=200)
    
    if success and data and "evolution" in data:
        print_test_result("Stock evolution (26 weeks)", True, f"Retrieved evolution data with {len(data['evolution'])} entries")
        test_results["stock_evolution"]["26_weeks"]["success"] = True
        test_results["stock_evolution"]["26_weeks"]["message"] = f"Successfully retrieved evolution data with {len(data['evolution'])} entries"
    else:
        print_test_result("Stock evolution (26 weeks)", False, message)
        test_results["stock_evolution"]["26_weeks"]["message"] = message
    
    # Test with 52 weeks
    success, message, data = make_request("get", f"/stock/evolution/{article_id}", params={"semaines": 52}, token=token, expected_status=200)
    
    if success and data and "evolution" in data:
        print_test_result("Stock evolution (52 weeks)", True, f"Retrieved evolution data with {len(data['evolution'])} entries")
        test_results["stock_evolution"]["52_weeks"]["success"] = True
        test_results["stock_evolution"]["52_weeks"]["message"] = f"Successfully retrieved evolution data with {len(data['evolution'])} entries"
    else:
        print_test_result("Stock evolution (52 weeks)", False, message)
        test_results["stock_evolution"]["52_weeks"]["message"] = message

def test_stock_couverture(token, article_id):
    print_header("Testing Stock Couverture API")
    
    success, message, data = make_request("get", f"/stock/couverture/{article_id}", token=token, expected_status=200)
    
    if success and data:
        # Check if all required metrics are present
        required_metrics = ["couverture_minimale_securite", "couverture_maximale_commande", "quantite_maximale_commande", "couverture_actuelle"]
        missing_metrics = [metric for metric in required_metrics if metric not in data]
        
        if not missing_metrics:
            print_test_result("Stock couverture metrics", True, f"Retrieved all required metrics: CMS={data['couverture_minimale_securite']}, CMC={data['couverture_maximale_commande']}, QM={data['quantite_maximale_commande']}, CR={data['couverture_actuelle']}")
            test_results["stock_couverture"]["metrics"]["success"] = True
            test_results["stock_couverture"]["metrics"]["message"] = f"Successfully retrieved all required metrics"
        else:
            print_test_result("Stock couverture metrics", False, f"Missing metrics: {', '.join(missing_metrics)}")
            test_results["stock_couverture"]["metrics"]["message"] = f"Missing metrics: {', '.join(missing_metrics)}"
    else:
        print_test_result("Stock couverture metrics", False, message)
        test_results["stock_couverture"]["metrics"]["message"] = message

def test_commandes_validation(token, article_id, fournisseur_id):
    print_header("Testing Commandes Validation API")
    
    # Create a basic validation request
    validation_data = {
        "article_id": article_id,
        "fournisseur_id": fournisseur_id,
        "quantite": 20,
        "date_livraison_prevue": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    # Test basic validation
    success, message, data = make_request("post", "/commandes/validation-avancee", validation_data, token=token, expected_status=200)
    
    if success and data:
        print_test_result("Commandes validation (basic)", True, f"Validation successful")
        test_results["commandes_validation"]["basic"]["success"] = True
        test_results["commandes_validation"]["basic"]["message"] = "Successfully validated order"
    else:
        print_test_result("Commandes validation (basic)", False, message)
        test_results["commandes_validation"]["basic"]["message"] = message
    
    # Test with constraints
    # Create a validation request with constraints
    validation_data_constraints = {
        "article_id": article_id,
        "fournisseur_id": fournisseur_id,
        "quantite": 5,  # Small quantity to potentially trigger minimum quantity constraint
        "date_livraison_prevue": (datetime.now() + timedelta(days=30)).isoformat(),  # Far future date to potentially trigger delivery time constraint
        "check_constraints": True
    }
    
    success, message, data = make_request("post", "/commandes/validation-avancee", validation_data_constraints, token=token, expected_status=200)
    
    if success and data:
        # Check if constraints were evaluated
        constraints_evaluated = False
        if "contraintes" in data or "recommandations" in data or "validation_status" in data:
            constraints_evaluated = True
        
        if constraints_evaluated:
            print_test_result("Commandes validation (constraints)", True, f"Constraints evaluated successfully")
            test_results["commandes_validation"]["constraints"]["success"] = True
            test_results["commandes_validation"]["constraints"]["message"] = "Successfully evaluated constraints"
        else:
            print_test_result("Commandes validation (constraints)", False, "Constraints were not evaluated")
            test_results["commandes_validation"]["constraints"]["message"] = "Constraints were not evaluated"
    else:
        print_test_result("Commandes validation (constraints)", False, message)
        test_results["commandes_validation"]["constraints"]["message"] = message

def test_articles_filters(token):
    print_header("Testing Articles Filters")
    
    # Test search filter
    search_term = "test"
    success, message, data = make_request("get", "/articles", params={"search": search_term}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Articles search filter", True, f"Retrieved {len(data)} articles matching search term '{search_term}'")
        test_results["articles_filters"]["search"]["success"] = True
        test_results["articles_filters"]["search"]["message"] = f"Successfully retrieved articles with search filter"
    else:
        print_test_result("Articles search filter", False, message)
        test_results["articles_filters"]["search"]["message"] = message
    
    # Test famille filter
    famille = "Test"
    success, message, data = make_request("get", "/articles", params={"famille": famille}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Articles famille filter", True, f"Retrieved {len(data)} articles in famille '{famille}'")
        test_results["articles_filters"]["famille"]["success"] = True
        test_results["articles_filters"]["famille"]["message"] = f"Successfully retrieved articles with famille filter"
    else:
        print_test_result("Articles famille filter", False, message)
        test_results["articles_filters"]["famille"]["message"] = message
    
    # Test fournisseur filter
    fournisseur_id = get_test_fournisseur_id(token)
    if fournisseur_id:
        success, message, data = make_request("get", "/articles", params={"fournisseur_id": fournisseur_id}, token=token, expected_status=200)
        
        if success and isinstance(data, list):
            print_test_result("Articles fournisseur filter", True, f"Retrieved {len(data)} articles from fournisseur '{fournisseur_id}'")
            test_results["articles_filters"]["fournisseur"]["success"] = True
            test_results["articles_filters"]["fournisseur"]["message"] = f"Successfully retrieved articles with fournisseur filter"
        else:
            print_test_result("Articles fournisseur filter", False, message)
            test_results["articles_filters"]["fournisseur"]["message"] = message
    
    # Test stock_bas filter
    success, message, data = make_request("get", "/articles", params={"stock_bas": True}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Articles stock_bas filter", True, f"Retrieved {len(data)} articles with low stock")
        test_results["articles_filters"]["stock_bas"]["success"] = True
        test_results["articles_filters"]["stock_bas"]["message"] = f"Successfully retrieved articles with stock_bas filter"
    else:
        print_test_result("Articles stock_bas filter", False, message)
        test_results["articles_filters"]["stock_bas"]["message"] = message

def test_fournisseurs_filters(token):
    print_header("Testing Fournisseurs Filters")
    
    # Test search filter
    search_term = "test"
    success, message, data = make_request("get", "/fournisseurs", params={"search": search_term}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Fournisseurs search filter", True, f"Retrieved {len(data)} fournisseurs matching search term '{search_term}'")
        test_results["fournisseurs_filters"]["search"]["success"] = True
        test_results["fournisseurs_filters"]["search"]["message"] = f"Successfully retrieved fournisseurs with search filter"
    else:
        print_test_result("Fournisseurs search filter", False, message)
        test_results["fournisseurs_filters"]["search"]["message"] = message
    
    # Test ville filter
    ville = "Test"
    success, message, data = make_request("get", "/fournisseurs", params={"ville": ville}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Fournisseurs ville filter", True, f"Retrieved {len(data)} fournisseurs in ville '{ville}'")
        test_results["fournisseurs_filters"]["ville"]["success"] = True
        test_results["fournisseurs_filters"]["ville"]["message"] = f"Successfully retrieved fournisseurs with ville filter"
    else:
        print_test_result("Fournisseurs ville filter", False, message)
        test_results["fournisseurs_filters"]["ville"]["message"] = message
    
    # Test pays filter
    pays = "France"
    success, message, data = make_request("get", "/fournisseurs", params={"pays": pays}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Fournisseurs pays filter", True, f"Retrieved {len(data)} fournisseurs in pays '{pays}'")
        test_results["fournisseurs_filters"]["pays"]["success"] = True
        test_results["fournisseurs_filters"]["pays"]["message"] = f"Successfully retrieved fournisseurs with pays filter"
    else:
        print_test_result("Fournisseurs pays filter", False, message)
        test_results["fournisseurs_filters"]["pays"]["message"] = message

def test_commandes_filters(token):
    print_header("Testing Commandes Filters")
    
    # Test status filter
    status = "brouillon"
    success, message, data = make_request("get", "/commandes", params={"status": status}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Commandes status filter", True, f"Retrieved {len(data)} commandes with status '{status}'")
        test_results["commandes_filters"]["status"]["success"] = True
        test_results["commandes_filters"]["status"]["message"] = f"Successfully retrieved commandes with status filter"
    else:
        print_test_result("Commandes status filter", False, message)
        test_results["commandes_filters"]["status"]["message"] = message
    
    # Test fournisseur filter
    fournisseur_id = get_test_fournisseur_id(token)
    if fournisseur_id:
        success, message, data = make_request("get", "/commandes", params={"fournisseur_id": fournisseur_id}, token=token, expected_status=200)
        
        if success and isinstance(data, list):
            print_test_result("Commandes fournisseur filter", True, f"Retrieved {len(data)} commandes from fournisseur '{fournisseur_id}'")
            test_results["commandes_filters"]["fournisseur"]["success"] = True
            test_results["commandes_filters"]["fournisseur"]["message"] = f"Successfully retrieved commandes with fournisseur filter"
        else:
            print_test_result("Commandes fournisseur filter", False, message)
            test_results["commandes_filters"]["fournisseur"]["message"] = message
    
    # Test date range filter
    date_from = (datetime.now() - timedelta(days=30)).isoformat()
    date_to = datetime.now().isoformat()
    success, message, data = make_request("get", "/commandes", params={"date_from": date_from, "date_to": date_to}, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Commandes date range filter", True, f"Retrieved {len(data)} commandes in date range")
        test_results["commandes_filters"]["date_range"]["success"] = True
        test_results["commandes_filters"]["date_range"]["message"] = f"Successfully retrieved commandes with date range filter"
    else:
        print_test_result("Commandes date range filter", False, message)
        test_results["commandes_filters"]["date_range"]["message"] = message

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

def run_tests():
    print_header("STARTING BACKEND API TESTS FOR PHASE 1")
    
    # Login
    token = login()
    if not token:
        print("Authentication failed, cannot proceed with tests")
        return
    
    # Get test data
    article_id = get_test_article_id(token)
    if not article_id:
        print("Failed to get or create a test article, cannot proceed with some tests")
    
    fournisseur_id = get_test_fournisseur_id(token)
    if not fournisseur_id:
        print("Failed to get a test fournisseur, cannot proceed with some tests")
    
    # Run tests
    if article_id:
        test_stock_evolution(token, article_id)
        test_stock_couverture(token, article_id)
    
    if article_id and fournisseur_id:
        test_commandes_validation(token, article_id, fournisseur_id)
    
    test_articles_filters(token)
    test_fournisseurs_filters(token)
    test_commandes_filters(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_tests()