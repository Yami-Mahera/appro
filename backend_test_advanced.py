import requests
import json
import time
import uuid
import re
import os
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

# Test results
test_results = {
    "export": {
        "fournisseurs_excel": {"success": False, "message": "Not tested"},
        "articles_csv": {"success": False, "message": "Not tested"},
        "commandes_pdf": {"success": False, "message": "Not tested"}
    },
    "kpis": {
        "taux_service_client": {"success": False, "message": "Not tested"},
        "delai_moyen_livraison": {"success": False, "message": "Not tested"},
        "synthese": {"success": False, "message": "Not tested"}
    },
    "powerbi": {
        "datasets": {"success": False, "message": "Not tested"},
        "data_fournisseurs": {"success": False, "message": "Not tested"}
    },
    "variations": {
        "ecarts": {"success": False, "message": "Not tested"},
        "previsions_vs_realisations": {"success": False, "message": "Not tested"}
    },
    "commandes": {
        "validation_avancee": {"success": False, "message": "Not tested"}
    },
    "dashboards": {
        "personnalises_creation": {"success": False, "message": "Not tested"},
        "widgets_disponibles": {"success": False, "message": "Not tested"}
    }
}

# IDs for created resources
created_ids = {
    "fournisseur": None,
    "article": None,
    "commande": None,
    "dashboard": None
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

def make_request(method, endpoint, data=None, token=None, expected_status=200, files=None, stream=False):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers, stream=stream)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers, files=files)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            return False, f"Unsupported method: {method}", None
        
        if response.status_code == expected_status:
            if stream:
                return True, "Success", response
            try:
                return True, "Success", response.json() if response.text else None
            except json.JSONDecodeError:
                return True, "Success (no JSON response)", response.text
        else:
            return False, f"Expected status {expected_status}, got {response.status_code}: {response.text}", None
    except Exception as e:
        return False, f"Request error: {str(e)}", None

def login_admin():
    print_header("Logging in as Admin")
    login_data = {
        "email": ADMIN_USER["email"],
        "password": ADMIN_USER["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Login admin", True, f"Logged in as: {ADMIN_USER['email']}")
        return data["access_token"]
    else:
        print_test_result("Login admin", False, message)
        # Try to register if login fails
        register_data = ADMIN_USER.copy()
        success, message, data = make_request("post", "/auth/register", register_data, expected_status=200)
        if success:
            print_test_result("Register admin", True, f"Registered admin: {ADMIN_USER['email']}")
            # Try login again
            success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
            if success and data and "access_token" in data:
                print_test_result("Login after register", True, f"Logged in as: {ADMIN_USER['email']}")
                return data["access_token"]
        
        print_test_result("Admin authentication", False, "Failed to login or register admin")
        return None

def create_test_data(token):
    print_header("Creating Test Data")
    
    # Create a test supplier
    fournisseur_data = {
        "nom": f"Fournisseur Test {uuid.uuid4().hex[:6]}",
        "code_fournisseur": f"FOUR-{uuid.uuid4().hex[:6]}",
        "adresse": "123 Rue de Test",
        "ville": "Paris",
        "code_postal": "75001",
        "pays": "France",
        "telephone": "+33123456789",
        "email": f"contact_{uuid.uuid4().hex[:6]}@fournisseur-test.com",
        "site_web": "https://www.fournisseur-test.com",
        "conditions_paiement": "30 jours",
        "delai_livraison_moyen": 5
    }
    
    success, message, data = make_request("post", "/fournisseurs", fournisseur_data, token=token, expected_status=200)
    if success and data and "id" in data:
        print_test_result("Create test supplier", True, f"Created supplier: {data['nom']}")
        created_ids["fournisseur"] = data["id"]
        
        # Create a test article
        article_data = {
            "reference": f"ART-{uuid.uuid4().hex[:6]}",
            "nom": "Article Test",
            "description": "Description de l'article test",
            "famille": "Test",
            "fournisseur_id": created_ids["fournisseur"],
            "prix_unitaire": 19.99,
            "unite": "pièce",
            "seuil_min": 10,
            "seuil_max": 100,
            "stock_actuel": 5,
            "duree_vie": 365,
            "emplacement_stockage": "Étagère A1"
        }
        
        success, message, data = make_request("post", "/articles", article_data, token=token, expected_status=200)
        if success and data and "id" in data:
            print_test_result("Create test article", True, f"Created article: {data['nom']}")
            created_ids["article"] = data["id"]
            
            # Create a test order
            commande_data = {
                "fournisseur_id": created_ids["fournisseur"],
                "lignes": [
                    {
                        "article_id": created_ids["article"],
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
                print_test_result("Create test order", True, f"Created order: {data['numero_commande']}")
                created_ids["commande"] = data["id"]
            else:
                print_test_result("Create test order", False, message)
        else:
            print_test_result("Create test article", False, message)
    else:
        print_test_result("Create test supplier", False, message)
    
    # Create stock movements for the article
    if created_ids["article"]:
        # Create an entry movement
        mouvement_data = {
            "article_id": created_ids["article"],
            "type_mouvement": "entree",
            "quantite": 20,
            "stock_avant": 5,
            "stock_apres": 25,
            "commentaire": "Entrée de stock test"
        }
        
        success, message, data = make_request("post", "/stock/mouvements", mouvement_data, token=token, expected_status=200)
        if success:
            print_test_result("Create stock entry movement", True, "Created stock entry movement")
        else:
            print_test_result("Create stock entry movement", False, message)
        
        # Create an exit movement
        mouvement_data = {
            "article_id": created_ids["article"],
            "type_mouvement": "sortie",
            "quantite": 8,
            "stock_avant": 25,
            "stock_apres": 17,
            "commentaire": "Sortie de stock test"
        }
        
        success, message, data = make_request("post", "/stock/mouvements", mouvement_data, token=token, expected_status=200)
        if success:
            print_test_result("Create stock exit movement", True, "Created stock exit movement")
        else:
            print_test_result("Create stock exit movement", False, message)
        
        # Create consumption forecasts
        for i in range(4):
            week_start = datetime.now() + timedelta(weeks=i)
            week_end = week_start + timedelta(days=7)
            
            prevision_data = {
                "article_id": created_ids["article"],
                "semaine": week_start.isocalendar()[1],
                "annee": week_start.year,
                "date_debut_semaine": week_start.isoformat(),
                "date_fin_semaine": week_end.isoformat(),
                "quantite_prevue": 5 + i,
                "quantite_reelle": 4 + i if i < 2 else None
            }
            
            success, message, data = make_request("post", "/stock/previsions", prevision_data, token=token, expected_status=200)
            if success:
                print_test_result(f"Create consumption forecast for week {i+1}", True, f"Created forecast for week {i+1}")
            else:
                print_test_result(f"Create consumption forecast for week {i+1}", False, message)

# Test functions for Export APIs
def test_export_fournisseurs_excel(token):
    print_header("Testing Export Fournisseurs Excel")
    
    success, message, response = make_request("get", "/export/fournisseurs/excel", token=token, expected_status=200, stream=True)
    
    if success and response:
        # Check if the response is a file
        content_type = response.headers.get('Content-Type')
        content_disposition = response.headers.get('Content-Disposition')
        
        if content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and content_disposition:
            print_test_result("Export fournisseurs excel", True, "Successfully exported fournisseurs to Excel")
            test_results["export"]["fournisseurs_excel"]["success"] = True
            test_results["export"]["fournisseurs_excel"]["message"] = "Successfully exported fournisseurs to Excel"
            return True
        else:
            print_test_result("Export fournisseurs excel", False, f"Invalid response format: {content_type}")
            test_results["export"]["fournisseurs_excel"]["message"] = f"Invalid response format: {content_type}"
            return False
    else:
        print_test_result("Export fournisseurs excel", False, message)
        test_results["export"]["fournisseurs_excel"]["message"] = message
        return False

def test_export_articles_csv(token):
    print_header("Testing Export Articles CSV")
    
    success, message, response = make_request("get", "/export/articles/csv", token=token, expected_status=200, stream=True)
    
    if success and response:
        # Check if the response is a file
        content_type = response.headers.get('Content-Type')
        content_disposition = response.headers.get('Content-Disposition')
        
        if content_type == 'text/csv' and content_disposition:
            print_test_result("Export articles csv", True, "Successfully exported articles to CSV")
            test_results["export"]["articles_csv"]["success"] = True
            test_results["export"]["articles_csv"]["message"] = "Successfully exported articles to CSV"
            return True
        else:
            print_test_result("Export articles csv", False, f"Invalid response format: {content_type}")
            test_results["export"]["articles_csv"]["message"] = f"Invalid response format: {content_type}"
            return False
    else:
        print_test_result("Export articles csv", False, message)
        test_results["export"]["articles_csv"]["message"] = message
        return False

def test_export_commandes_pdf(token):
    print_header("Testing Export Commandes PDF")
    
    success, message, response = make_request("get", "/export/commandes/pdf", token=token, expected_status=200, stream=True)
    
    if success and response:
        # Check if the response is a file
        content_type = response.headers.get('Content-Type')
        content_disposition = response.headers.get('Content-Disposition')
        
        if content_type == 'application/pdf' and content_disposition:
            print_test_result("Export commandes pdf", True, "Successfully exported commandes to PDF")
            test_results["export"]["commandes_pdf"]["success"] = True
            test_results["export"]["commandes_pdf"]["message"] = "Successfully exported commandes to PDF"
            return True
        else:
            print_test_result("Export commandes pdf", False, f"Invalid response format: {content_type}")
            test_results["export"]["commandes_pdf"]["message"] = f"Invalid response format: {content_type}"
            return False
    else:
        print_test_result("Export commandes pdf", False, message)
        test_results["export"]["commandes_pdf"]["message"] = message
        return False

# Test functions for KPI APIs
def test_kpi_taux_service_client(token):
    print_header("Testing KPI Taux Service Client")
    
    success, message, data = make_request("get", "/kpis/taux-service-client", token=token, expected_status=200)
    
    if success and data:
        print_test_result("KPI taux service client", True, f"Retrieved KPI data: {data}")
        test_results["kpis"]["taux_service_client"]["success"] = True
        test_results["kpis"]["taux_service_client"]["message"] = "Successfully retrieved taux service client KPI"
        return True
    else:
        print_test_result("KPI taux service client", False, message)
        test_results["kpis"]["taux_service_client"]["message"] = message
        return False

def test_kpi_delai_moyen_livraison(token):
    print_header("Testing KPI Délai Moyen Livraison")
    
    success, message, data = make_request("get", "/kpis/delai-moyen-livraison", token=token, expected_status=200)
    
    if success and data:
        print_test_result("KPI délai moyen livraison", True, f"Retrieved KPI data: {data}")
        test_results["kpis"]["delai_moyen_livraison"]["success"] = True
        test_results["kpis"]["delai_moyen_livraison"]["message"] = "Successfully retrieved délai moyen livraison KPI"
        return True
    else:
        print_test_result("KPI délai moyen livraison", False, message)
        test_results["kpis"]["delai_moyen_livraison"]["message"] = message
        return False

def test_kpi_synthese(token):
    print_header("Testing KPI Synthèse")
    
    success, message, data = make_request("get", "/kpis/synthese", token=token, expected_status=200)
    
    if success and data:
        print_test_result("KPI synthèse", True, f"Retrieved KPI synthèse data")
        test_results["kpis"]["synthese"]["success"] = True
        test_results["kpis"]["synthese"]["message"] = "Successfully retrieved KPI synthèse"
        return True
    else:
        print_test_result("KPI synthèse", False, message)
        test_results["kpis"]["synthese"]["message"] = message
        return False

# Test functions for Power BI APIs
def test_powerbi_datasets(token):
    print_header("Testing Power BI Datasets")
    
    success, message, data = make_request("get", "/powerbi/datasets", token=token, expected_status=200)
    
    if success and data:
        print_test_result("Power BI datasets", True, f"Retrieved Power BI datasets: {data}")
        test_results["powerbi"]["datasets"]["success"] = True
        test_results["powerbi"]["datasets"]["message"] = "Successfully retrieved Power BI datasets"
        return True
    else:
        print_test_result("Power BI datasets", False, message)
        test_results["powerbi"]["datasets"]["message"] = message
        return False

def test_powerbi_data_fournisseurs(token):
    print_header("Testing Power BI Data Fournisseurs")
    
    success, message, data = make_request("get", "/powerbi/data/fournisseurs", token=token, expected_status=200)
    
    if success and data:
        print_test_result("Power BI data fournisseurs", True, f"Retrieved Power BI data for fournisseurs")
        test_results["powerbi"]["data_fournisseurs"]["success"] = True
        test_results["powerbi"]["data_fournisseurs"]["message"] = "Successfully retrieved Power BI data for fournisseurs"
        return True
    else:
        print_test_result("Power BI data fournisseurs", False, message)
        test_results["powerbi"]["data_fournisseurs"]["message"] = message
        return False

# Test functions for Variation APIs
def test_variations_ecarts(token):
    print_header("Testing Variations Écarts")
    
    success, message, data = make_request("get", "/variations/ecarts", token=token, expected_status=200)
    
    if success and data is not None:
        print_test_result("Variations écarts", True, f"Retrieved variations écarts data")
        test_results["variations"]["ecarts"]["success"] = True
        test_results["variations"]["ecarts"]["message"] = "Successfully retrieved variations écarts data"
        return True
    else:
        print_test_result("Variations écarts", False, message)
        test_results["variations"]["ecarts"]["message"] = message
        return False

def test_variations_previsions_vs_realisations(token, article_id):
    print_header("Testing Variations Prévisions vs Réalisations")
    
    if not article_id:
        print_test_result("Variations prévisions vs réalisations", False, "No article ID available")
        test_results["variations"]["previsions_vs_realisations"]["message"] = "No article ID available"
        return False
    
    success, message, data = make_request("get", f"/variations/previsions-vs-realisations/{article_id}", token=token, expected_status=200)
    
    if success and data:
        print_test_result("Variations prévisions vs réalisations", True, f"Retrieved prévisions vs réalisations data")
        test_results["variations"]["previsions_vs_realisations"]["success"] = True
        test_results["variations"]["previsions_vs_realisations"]["message"] = "Successfully retrieved prévisions vs réalisations data"
        return True
    else:
        print_test_result("Variations prévisions vs réalisations", False, message)
        test_results["variations"]["previsions_vs_realisations"]["message"] = message
        return False

# Test function for Advanced Order Validation
def test_commandes_validation_avancee(token, commande_id):
    print_header("Testing Commandes Validation Avancée")
    
    if not commande_id:
        print_test_result("Commandes validation avancée", False, "No commande ID available")
        test_results["commandes"]["validation_avancee"]["message"] = "No commande ID available"
        return False
    
    validation_data = {
        "commande_id": commande_id,
        "date_limite_consommation": (datetime.now() + timedelta(days=180)).isoformat(),
        "espace_stockage_disponible": True,
        "quantite_min_respectee": True,
        "delai_livraison_acceptable": True,
        "stock_securite_respecte": True,
        "seuil_surstock_respecte": True,
        "contraintes_additionnelles": {
            "transport_special": False,
            "temperature_controlee": False
        },
        "commentaires": "Validation test"
    }
    
    success, message, data = make_request("post", "/commandes/validation-avancee", validation_data, token=token, expected_status=200)
    
    if success and data:
        print_test_result("Commandes validation avancée", True, f"Successfully validated commande")
        test_results["commandes"]["validation_avancee"]["success"] = True
        test_results["commandes"]["validation_avancee"]["message"] = "Successfully validated commande"
        return True
    else:
        print_test_result("Commandes validation avancée", False, message)
        test_results["commandes"]["validation_avancee"]["message"] = message
        return False

# Test functions for Dashboard APIs
def test_dashboards_personnalises_creation(token):
    print_header("Testing Dashboards Personnalisés Creation")
    
    dashboard_data = {
        "nom": f"Dashboard Test {uuid.uuid4().hex[:6]}",
        "description": "Dashboard de test pour les tests automatisés",
        "widgets": [
            {
                "type": "kpi",
                "titre": "Taux de service",
                "config": {
                    "kpi_type": "taux_service_client",
                    "periode": "30d"
                },
                "position": {"x": 0, "y": 0, "w": 6, "h": 2}
            },
            {
                "type": "chart",
                "titre": "Évolution des commandes",
                "config": {
                    "chart_type": "line",
                    "data_source": "commandes",
                    "periode": "90d"
                },
                "position": {"x": 6, "y": 0, "w": 6, "h": 4}
            }
        ],
        "layout": {
            "columns": 12,
            "rowHeight": 50
        },
        "partage": True
    }
    
    success, message, data = make_request("post", "/dashboards/personnalises", dashboard_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print_test_result("Dashboards personnalisés creation", True, f"Created dashboard: {data['nom']}")
        test_results["dashboards"]["personnalises_creation"]["success"] = True
        test_results["dashboards"]["personnalises_creation"]["message"] = f"Successfully created dashboard: {data['nom']}"
        created_ids["dashboard"] = data["id"]
        return True
    else:
        print_test_result("Dashboards personnalisés creation", False, message)
        test_results["dashboards"]["personnalises_creation"]["message"] = message
        return False

def test_dashboards_widgets_disponibles(token):
    print_header("Testing Dashboards Widgets Disponibles")
    
    success, message, data = make_request("get", "/dashboards/widgets-disponibles", token=token, expected_status=200)
    
    if success and data:
        print_test_result("Dashboards widgets disponibles", True, f"Retrieved available widgets")
        test_results["dashboards"]["widgets_disponibles"]["success"] = True
        test_results["dashboards"]["widgets_disponibles"]["message"] = "Successfully retrieved available widgets"
        return True
    else:
        print_test_result("Dashboards widgets disponibles", False, message)
        test_results["dashboards"]["widgets_disponibles"]["message"] = message
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
    print_header("STARTING ADVANCED BACKEND API TESTS")
    
    # Login as admin
    token = login_admin()
    if not token:
        print("Admin authentication failed, cannot proceed with tests")
        print_summary()
        return
    
    # Create test data
    create_test_data(token)
    
    # Test Export APIs
    test_export_fournisseurs_excel(token)
    test_export_articles_csv(token)
    test_export_commandes_pdf(token)
    
    # Test KPI APIs
    test_kpi_taux_service_client(token)
    test_kpi_delai_moyen_livraison(token)
    test_kpi_synthese(token)
    
    # Test Power BI APIs
    test_powerbi_datasets(token)
    test_powerbi_data_fournisseurs(token)
    
    # Test Variation APIs
    test_variations_ecarts(token)
    if created_ids["article"]:
        test_variations_previsions_vs_realisations(token, created_ids["article"])
    
    # Test Advanced Order Validation
    if created_ids["commande"]:
        test_commandes_validation_avancee(token, created_ids["commande"])
    
    # Test Dashboard APIs
    test_dashboards_personnalises_creation(token)
    test_dashboards_widgets_disponibles(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_all_tests()