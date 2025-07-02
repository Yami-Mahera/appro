#!/usr/bin/env python3
import requests
import json
import uuid
from datetime import datetime, date, timedelta
import logging
import sys
import os
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("backend_test")

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://05035f8b-a440-499b-80a0-cd8a5d57b626.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

# Test data
test_fournisseur = {
    "code": f"FOUR{uuid.uuid4().hex[:6]}",
    "nom": "Fournitures Express",
    "raison_sociale": "Fournitures Express SARL",
    "adresse": "123 Avenue des Approvisionnements",
    "ville": "Paris",
    "code_postal": "75001",
    "pays": "France",
    "telephone": "+33123456789",
    "email": "contact@fournitures-express.fr",
    "site_web": "https://www.fournitures-express.fr",
    "delai_paiement": 30,
    "mode_reglement": "virement",
    "devise_principale": "EUR",
    "taux_remise": 5.0,
    "delai_livraison_standard": 5,
    "quantite_min_commande": 100.0,
    "frais_port": 15.0,
    "notes": "Fournisseur principal pour matériel de bureau"
}

test_contact = {
    "nom": "Dupont",
    "prenom": "Jean",
    "fonction": "Responsable Commercial",
    "telephone": "+33123456789",
    "email": "jean.dupont@fournitures-express.fr",
    "mobile": "+33612345678",
    "principal": True
}

test_article = {
    "reference": f"ART{uuid.uuid4().hex[:6]}",
    "designation": "Papier A4 Premium",
    "description": "Ramette de papier A4 80g/m² haute qualité",
    "famille": "Papeterie",
    "sous_famille": "Papier",
    "marque": "PaperQuality",
    "fournisseur_id": "",  # Will be set after creating a fournisseur
    "reference_fournisseur": "PAP-A4-80",
    "prix_unitaire": 4.50,
    "devise": "EUR",
    "stock_minimum": 10.0,
    "stock_maximum": 100.0,
    "stock_securite": 20.0,
    "seuil_alerte": 15.0,
    "unite_mesure": "ramette",
    "poids": 2.5,
    "volume": 0.01,
    "duree_vie": 365,
    "consommation_mensuelle": 20.0,
    "notes": "Papier pour imprimantes et photocopieurs"
}

test_commande = {
    "fournisseur_id": "",  # Will be set after creating a fournisseur
    "date_commande": date.today().isoformat(),
    "date_livraison_prevue": (date.today() + timedelta(days=7)).isoformat(),
    "priorite": "normale",
    "devise": "EUR",
    "incoterm": "DAP",
    "mode_transport": "routier",
    "taux_tva": 20.0,
    "frais_port": 10.0,
    "remise_globale": 2.0,
    "lignes": [],  # Will be populated after creating an article
    "notes": "Commande mensuelle de fournitures",
    "commentaires_internes": "Livraison à prévoir avant le 15",
    "creee_par": "Système de test"
}

test_alerte = {
    "titre": "Alerte stock critique",
    "message": "Le niveau de stock est en dessous du seuil critique",
    "type": "critique",
    "article_id": "",  # Will be set after creating an article
    "valeur_actuelle": 5.0,
    "valeur_seuil": 10.0
}

# Test results
test_results = {
    "fournisseurs": {"success": 0, "fail": 0},
    "articles": {"success": 0, "fail": 0},
    "commandes": {"success": 0, "fail": 0},
    "stocks": {"success": 0, "fail": 0},
    "alertes": {"success": 0, "fail": 0},
    "dashboard": {"success": 0, "fail": 0}
}

# Store created resources for cleanup and reference
created_resources = {
    "fournisseur_id": None,
    "article_id": None,
    "commande_id": None,
    "alerte_id": None
}

def log_test(module: str, test_name: str, success: bool, details: Optional[str] = None):
    """Log test results and update counters"""
    status = "✅ PASS" if success else "❌ FAIL"
    if success:
        test_results[module]["success"] += 1
    else:
        test_results[module]["fail"] += 1
    
    log_message = f"{status} - {module.upper()} - {test_name}"
    if details and not success:
        log_message += f": {details}"
    
    logger.info(log_message)
    return success

def make_request(method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
    """Make an HTTP request to the API and handle errors"""
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
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
            return {"error": f"Unsupported method: {method}"}
        
        if response.status_code >= 400:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
        
        if response.text:
            return response.json()
        return {"status": "success", "status_code": response.status_code}
    
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def test_root_api():
    """Test the root API endpoint"""
    response = make_request("get", "/")
    success = "error" not in response and "message" in response
    return log_test("dashboard", "Root API", success, response.get("error"))

def test_fournisseurs_api():
    """Test the fournisseurs API endpoints"""
    global test_fournisseur, created_resources
    
    # Test GET /fournisseurs (empty list or existing fournisseurs)
    response = make_request("get", "/fournisseurs")
    success = isinstance(response, list) or ("error" not in response)
    log_test("fournisseurs", "GET /fournisseurs", success, None if isinstance(response, list) else response.get("error"))
    
    # Test POST /fournisseurs (create)
    response = make_request("post", "/fournisseurs", test_fournisseur)
    success = "error" not in response and "id" in response
    log_test("fournisseurs", "POST /fournisseurs", success, response.get("error"))
    
    if success:
        created_resources["fournisseur_id"] = response["id"]
        test_fournisseur["id"] = response["id"]
        test_article["fournisseur_id"] = response["id"]
        test_commande["fournisseur_id"] = response["id"]
    
    # Test GET /fournisseurs/{id}
    if created_resources["fournisseur_id"]:
        response = make_request("get", f"/fournisseurs/{created_resources['fournisseur_id']}")
        success = "error" not in response and response.get("id") == created_resources["fournisseur_id"]
        log_test("fournisseurs", "GET /fournisseurs/{id}", success, response.get("error"))
    
    # Test PUT /fournisseurs/{id}
    if created_resources["fournisseur_id"]:
        updated_data = test_fournisseur.copy()
        updated_data["nom"] = "Fournitures Express Updated"
        response = make_request("put", f"/fournisseurs/{created_resources['fournisseur_id']}", updated_data)
        success = "error" not in response and response.get("nom") == "Fournitures Express Updated"
        log_test("fournisseurs", "PUT /fournisseurs/{id}", success, response.get("error"))
    
    # Test POST /fournisseurs/{id}/contacts
    if created_resources["fournisseur_id"]:
        response = make_request("post", f"/fournisseurs/{created_resources['fournisseur_id']}/contacts", test_contact)
        success = "error" not in response and "id" in response
        log_test("fournisseurs", "POST /fournisseurs/{id}/contacts", success, response.get("error"))
    
    # Test DELETE /fournisseurs/{id} (soft delete)
    if created_resources["fournisseur_id"]:
        response = make_request("delete", f"/fournisseurs/{created_resources['fournisseur_id']}")
        success = "error" not in response and "message" in response
        log_test("fournisseurs", "DELETE /fournisseurs/{id}", success, response.get("error"))

def test_articles_api():
    """Test the articles API endpoints"""
    global test_article, created_resources
    
    # Skip if no fournisseur was created
    if not created_resources["fournisseur_id"]:
        logger.warning("Skipping articles tests: No fournisseur created")
        return
    
    # Test GET /articles (empty list or existing articles)
    response = make_request("get", "/articles")
    success = isinstance(response, list) or ("error" not in response)
    log_test("articles", "GET /articles", success, None if isinstance(response, list) else response.get("error"))
    
    # Test POST /articles (create)
    response = make_request("post", "/articles", test_article)
    success = "error" not in response and "id" in response
    log_test("articles", "POST /articles", success, response.get("error"))
    
    if success:
        created_resources["article_id"] = response["id"]
        test_article["id"] = response["id"]
        test_alerte["article_id"] = response["id"]
        
        # Add a line to the test_commande
        test_commande["lignes"] = [{
            "article_id": response["id"],
            "quantite": 10,
            "prix_unitaire": 4.50,
            "remise": 0,
            "date_livraison_souhaitee": (date.today() + timedelta(days=7)).isoformat()
        }]
    
    # Test GET /articles/{id}
    if created_resources["article_id"]:
        response = make_request("get", f"/articles/{created_resources['article_id']}")
        success = "error" not in response and response.get("id") == created_resources["article_id"]
        log_test("articles", "GET /articles/{id}", success, response.get("error"))
    
    # Test PUT /articles/{id}
    if created_resources["article_id"]:
        updated_data = test_article.copy()
        updated_data["designation"] = "Papier A4 Premium Plus"
        updated_data["prix_unitaire"] = 5.0
        response = make_request("put", f"/articles/{created_resources['article_id']}", updated_data)
        success = "error" not in response and response.get("designation") == "Papier A4 Premium Plus"
        log_test("articles", "PUT /articles/{id}", success, response.get("error"))
    
    # Test GET /articles with filters
    response = make_request("get", "/articles", params={"famille": "Papeterie"})
    success = isinstance(response, list) or ("error" not in response)
    log_test("articles", "GET /articles with filters", success, None if isinstance(response, list) else response.get("error"))

def test_commandes_api():
    """Test the commandes API endpoints"""
    global test_commande, created_resources
    
    # Skip if no fournisseur or article was created
    if not created_resources["fournisseur_id"] or not created_resources["article_id"]:
        logger.warning("Skipping commandes tests: No fournisseur or article created")
        return
    
    # Test GET /commandes (empty list or existing commandes)
    response = make_request("get", "/commandes")
    success = isinstance(response, list) or ("error" not in response)
    log_test("commandes", "GET /commandes", success, None if isinstance(response, list) else response.get("error"))
    
    # Test POST /commandes (create)
    response = make_request("post", "/commandes", test_commande)
    success = "error" not in response and "id" in response
    log_test("commandes", "POST /commandes", success, response.get("error"))
    
    if success:
        created_resources["commande_id"] = response["id"]
        test_commande["id"] = response["id"]
    
    # Test GET /commandes/{id}
    if created_resources["commande_id"]:
        response = make_request("get", f"/commandes/{created_resources['commande_id']}")
        success = "error" not in response and response.get("id") == created_resources["commande_id"]
        log_test("commandes", "GET /commandes/{id}", success, response.get("error"))
    
    # Test PUT /commandes/{id}/etat
    if created_resources["commande_id"]:
        response = make_request("put", f"/commandes/{created_resources['commande_id']}/etat", {"nouvel_etat": "passee"})
        success = "error" not in response and "message" in response
        log_test("commandes", "PUT /commandes/{id}/etat", success, response.get("error"))
    
    # Test GET /commandes with filters
    response = make_request("get", "/commandes", params={"fournisseur_id": created_resources["fournisseur_id"]})
    success = isinstance(response, list) or ("error" not in response)
    log_test("commandes", "GET /commandes with filters", success, None if isinstance(response, list) else response.get("error"))

def test_stocks_api():
    """Test the stocks API endpoints"""
    global created_resources
    
    # Skip if no article was created
    if not created_resources["article_id"]:
        logger.warning("Skipping stocks tests: No article created")
        return
    
    # Test GET /stocks (list)
    response = make_request("get", "/stocks")
    success = isinstance(response, list) or ("error" not in response)
    log_test("stocks", "GET /stocks", success, None if isinstance(response, list) else response.get("error"))
    
    # Test GET /stocks/{article_id}
    response = make_request("get", f"/stocks/{created_resources['article_id']}")
    success = "error" not in response and response.get("article_id") == created_resources["article_id"]
    log_test("stocks", "GET /stocks/{article_id}", success, response.get("error"))
    
    # Test PUT /stocks/{article_id}
    stock_update = {
        "quantite_physique": 50.0,
        "quantite_reservee": 5.0,
        "seuil_alerte": 10.0
    }
    response = make_request("put", f"/stocks/{created_resources['article_id']}", stock_update)
    success = "error" not in response and response.get("quantite_physique") == 50.0
    log_test("stocks", "PUT /stocks/{article_id}", success, response.get("error"))
    
    # Test GET /stocks with filters
    response = make_request("get", "/stocks", params={"alerte": True})
    success = "error" not in response
    log_test("stocks", "GET /stocks with filters", success, response.get("error"))

def test_alertes_api():
    """Test the alertes API endpoints"""
    global test_alerte, created_resources
    
    # Skip if no article was created
    if not created_resources["article_id"]:
        logger.warning("Skipping alertes tests: No article created")
        return
    
    # Test GET /alertes (list)
    response = make_request("get", "/alertes")
    success = isinstance(response, list) or ("error" not in response)
    log_test("alertes", "GET /alertes", success, None if isinstance(response, list) else response.get("error"))
    
    # Test POST /alertes (create)
    response = make_request("post", "/alertes", test_alerte)
    success = "error" not in response and "id" in response
    log_test("alertes", "POST /alertes", success, response.get("error"))
    
    if success:
        created_resources["alerte_id"] = response["id"]
    
    # Test PUT /alertes/{id}/traiter
    if created_resources["alerte_id"]:
        traitement_data = {
            "actions_prises": "Commande passée au fournisseur",
            "traitee_par": "Système de test"
        }
        response = make_request("put", f"/alertes/{created_resources['alerte_id']}/traiter", traitement_data)
        success = "error" not in response and "message" in response
        log_test("alertes", "PUT /alertes/{id}/traiter", success, response.get("error"))
    
    # Test GET /alertes with filters
    response = make_request("get", "/alertes", params={"type": "critique"})
    success = "error" not in response
    log_test("alertes", "GET /alertes with filters", success, response.get("error"))

def test_dashboard_api():
    """Test the dashboard API endpoint"""
    response = make_request("get", "/dashboard")
    success = "error" not in response and "nb_articles_total" in response
    log_test("dashboard", "GET /dashboard", success, response.get("error"))
    
    # Verify that all expected fields are present
    if success:
        expected_fields = [
            "nb_articles_total", "nb_articles_alerte", "nb_articles_rupture",
            "valeur_stock_total", "nb_commandes_en_cours", "nb_commandes_retard",
            "montant_commandes_mois", "nb_fournisseurs_actifs",
            "nb_alertes_critiques", "nb_alertes_importantes"
        ]
        
        for field in expected_fields:
            if field not in response:
                log_test("dashboard", f"Dashboard field: {field}", False, f"Field missing in response")
            else:
                log_test("dashboard", f"Dashboard field: {field}", True)

def print_summary():
    """Print a summary of all test results"""
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    total_success = 0
    total_fail = 0
    
    for module, results in test_results.items():
        success = results["success"]
        fail = results["fail"]
        total = success + fail
        success_rate = (success / total * 100) if total > 0 else 0
        
        logger.info(f"{module.upper()}: {success}/{total} tests passed ({success_rate:.1f}%)")
        total_success += success
        total_fail += fail
    
    grand_total = total_success + total_fail
    overall_rate = (total_success / grand_total * 100) if grand_total > 0 else 0
    
    logger.info("-"*50)
    logger.info(f"OVERALL: {total_success}/{grand_total} tests passed ({overall_rate:.1f}%)")
    logger.info("="*50)
    
    return total_fail == 0

if __name__ == "__main__":
    logger.info(f"Starting backend API tests against {API_URL}")
    
    # Test root API
    test_root_api()
    
    # Test all modules
    test_fournisseurs_api()
    test_articles_api()
    test_commandes_api()
    test_stocks_api()
    test_alertes_api()
    test_dashboard_api()
    
    # Print summary
    all_tests_passed = print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_tests_passed else 1)