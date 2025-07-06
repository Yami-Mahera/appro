import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://eb8f69ef-e374-4b45-8fef-987ba5a17544.preview.emergentagent.com/api"
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
    
    # First try to login
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
        print("Login failed, trying to register...")
        success, message, data = make_request("post", "/auth/register", ADMIN_USER, expected_status=200)
        
        if success:
            print_test_result("Register", True, f"Registered user: {ADMIN_USER['email']}")
            
            # Try login again
            success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
            
            if success and data and "access_token" in data:
                print_test_result("Login after register", True, f"Logged in as: {ADMIN_USER['email']}")
                return data["access_token"]
            else:
                print_test_result("Login after register", False, message)
                return None
        else:
            print_test_result("Register", False, message)
            return None

def create_test_data(token):
    print_header("Creating Test Data")
    
    # Create a test supplier
    supplier_data = {
        "nom": "Fournisseur Test Alertes",
        "code_fournisseur": f"FTA-{uuid.uuid4().hex[:6]}",
        "adresse": "123 Rue des Tests",
        "ville": "Paris",
        "code_postal": "75001",
        "pays": "France",
        "telephone": "+33123456789",
        "email": f"contact_{uuid.uuid4().hex[:6]}@fournisseur-test.com",
        "site_web": "https://www.fournisseur-test.com",
        "conditions_paiement": "30 jours",
        "delai_livraison_moyen": 14,  # 14 days delivery time
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
    
    success, message, supplier_data = make_request("post", "/fournisseurs", supplier_data, token=token, expected_status=200)
    
    if not success:
        print_test_result("Create supplier", False, message)
        return None, None, None
    
    supplier_id = supplier_data["id"]
    print_test_result("Create supplier", True, f"Created supplier: {supplier_data['nom']} (ID: {supplier_id})")
    
    # Create test articles with different stock levels
    articles = []
    
    # Article 1: Critical stock level (for testing urgent alerts)
    article1_data = {
        "reference": f"ART-CRIT-{uuid.uuid4().hex[:6]}",
        "nom": "Article Test Critique",
        "description": "Article avec stock critique pour test d'alertes",
        "famille": "Test",
        "fournisseur_id": supplier_id,
        "prix_unitaire": 19.99,
        "unite": "pièce",
        "seuil_min": 50,  # High minimum threshold
        "seuil_max": 100,
        "stock_actuel": 5,  # Very low stock
        "duree_vie": 365,
        "emplacement_stockage": "Étagère A1"
    }
    
    success, message, article1_data = make_request("post", "/articles", article1_data, token=token, expected_status=200)
    
    if success:
        articles.append(article1_data)
        print_test_result("Create critical article", True, f"Created article: {article1_data['nom']} (ID: {article1_data['id']})")
        
        # Create movement records for this article to simulate consumption
        for i in range(5):
            movement_data = {
                "article_id": article1_data["id"],
                "type_mouvement": "sortie",
                "quantite": 10,
                "stock_avant": 55 - i*10,
                "stock_apres": 45 - i*10,
                "commentaire": f"Mouvement de test {i+1}",
                "created_by": "admin"
            }
            
            success, message, _ = make_request("post", "/stock/mouvements", movement_data, token=token, expected_status=200)
            if success:
                print(f"  - Created movement record {i+1}: -10 units")
            else:
                print(f"  - Failed to create movement record: {message}")
    else:
        print_test_result("Create critical article", False, message)
    
    # Article 2: Normal stock level
    article2_data = {
        "reference": f"ART-NORM-{uuid.uuid4().hex[:6]}",
        "nom": "Article Test Normal",
        "description": "Article avec stock normal pour test d'alertes",
        "famille": "Test",
        "fournisseur_id": supplier_id,
        "prix_unitaire": 29.99,
        "unite": "pièce",
        "seuil_min": 10,
        "seuil_max": 50,
        "stock_actuel": 30,  # Normal stock
        "duree_vie": 365,
        "emplacement_stockage": "Étagère B2"
    }
    
    success, message, article2_data = make_request("post", "/articles", article2_data, token=token, expected_status=200)
    
    if success:
        articles.append(article2_data)
        print_test_result("Create normal article", True, f"Created article: {article2_data['nom']} (ID: {article2_data['id']})")
        
        # Create movement records for this article to simulate consumption
        for i in range(3):
            movement_data = {
                "article_id": article2_data["id"],
                "type_mouvement": "sortie",
                "quantite": 5,
                "stock_avant": 45 - i*5,
                "stock_apres": 40 - i*5,
                "commentaire": f"Mouvement de test {i+1}",
                "created_by": "admin"
            }
            
            success, message, _ = make_request("post", "/stock/mouvements", movement_data, token=token, expected_status=200)
            if success:
                print(f"  - Created movement record {i+1}: -5 units")
            else:
                print(f"  - Failed to create movement record: {message}")
    else:
        print_test_result("Create normal article", False, message)
    
    # Create a test order for the first article
    if articles:
        commande_data = {
            "fournisseur_id": supplier_id,
            "lignes": [
                {
                    "article_id": articles[0]["id"],
                    "quantite": 50,
                    "prix_unitaire": articles[0]["prix_unitaire"],
                    "total": 50 * articles[0]["prix_unitaire"]
                }
            ],
            "date_livraison_prevue": (datetime.now() + timedelta(days=7)).isoformat(),
            "date_production": (datetime.now() + timedelta(days=2)).isoformat(),
            "date_mise_disposition": (datetime.now() + timedelta(days=4)).isoformat(),
            "date_embarquement_cible": (datetime.now() + timedelta(days=5)).isoformat(),
            "notes": "Commande test pour alertes avancées"
        }
        
        success, message, commande_data = make_request("post", "/commandes", commande_data, token=token, expected_status=200)
        
        if success:
            print_test_result("Create order", True, f"Created order: {commande_data['numero_commande']} (ID: {commande_data['id']})")
            
            # Update the order status to PENDING to test commandes_en_cours alerts
            update_data = {
                "status": "en_attente"  # CommandeStatus.PENDING
            }
            
            success, message, _ = make_request("put", f"/commandes/{commande_data['id']}", update_data, token=token, expected_status=200)
            if success:
                print("  - Updated order status to PENDING")
            else:
                print(f"  - Failed to update order status: {message}")
            
            return supplier_id, articles, commande_data["id"]
        else:
            print_test_result("Create order", False, message)
            return supplier_id, articles, None
    
    return supplier_id, articles, None

def test_get_alertes_avancees(token):
    print_header("Testing GET /api/stock/alertes-avancees")
    
    success, message, data = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get alertes avancées", True, f"Retrieved {len(data)} alertes avancées")
        
        # Print details of the first few alerts if any
        if data:
            print("\nDetails of first alert:")
            first_alert = data[0]
            for key, value in first_alert.items():
                print(f"  {key}: {value}")
        
        return True, data
    else:
        print_test_result("Get alertes avancées", False, message)
        return False, None

def test_generer_alertes(token):
    print_header("Testing POST /api/stock/generer-alertes")
    
    success, message, data = make_request("post", "/stock/generer-alertes", token=token, expected_status=200)
    
    if success and isinstance(data, dict):
        print_test_result("Générer alertes", True, f"Generated {data.get('message', 'unknown number of')} alertes")
        
        # Print details of the generated alerts
        alertes = data.get("alertes", [])
        print(f"\nGenerated {len(alertes)} alerts:")
        
        for i, alerte in enumerate(alertes[:5]):  # Show first 5 alerts
            print(f"\nAlert {i+1}:")
            print(f"  Type: {alerte.get('type_alerte')}")
            print(f"  Niveau: {alerte.get('niveau_alerte')}")
            print(f"  Message: {alerte.get('message')}")
            print(f"  Recommandation: {alerte.get('recommandation')}")
        
        if len(alertes) > 5:
            print(f"\n... and {len(alertes) - 5} more alerts")
        
        return True, data
    else:
        print_test_result("Générer alertes", False, message)
        return False, None

def test_alert_formulas(token, articles):
    print_header("Testing Alert Calculation Formulas")
    
    if not articles:
        print_test_result("Test formulas", False, "No test articles available")
        return False
    
    # Test the formula for new orders (Db - Do - Dc)
    print("\nTesting formula for new orders: Db - Do - Dc")
    
    # Get couverture data for the critical article
    critical_article = articles[0]
    success, message, couverture_data = make_request("get", f"/stock/couverture/{critical_article['id']}", token=token, expected_status=200)
    
    if success and isinstance(couverture_data, dict):
        print_test_result("Get couverture data", True, "Retrieved couverture data for critical article")
        
        # Print relevant data for formula verification
        print("\nCouverture data for critical article:")
        print(f"  Stock actuel: {couverture_data.get('stock_actuel', 'N/A')}")
        print(f"  Couverture actuelle (Cr): {couverture_data.get('couverture_actuelle', 'N/A')}")
        print(f"  Couverture minimale sécurité (CMS): {couverture_data.get('couverture_minimale_securite', 'N/A')}")
        print(f"  Date besoin: {couverture_data.get('date_besoin', 'N/A')}")
        
        # Generate alerts to trigger the formula calculation
        success, message, alertes_data = make_request("post", "/stock/generer-alertes", token=token, expected_status=200)
        
        if success:
            alertes = alertes_data.get("alertes", [])
            critical_alertes = [a for a in alertes if a.get("article_id") == critical_article["id"] and a.get("type_alerte") == "nouvelle_commande"]
            
            if critical_alertes:
                alerte = critical_alertes[0]
                print("\nAlert generated for critical article:")
                print(f"  Niveau alerte: {alerte.get('niveau_alerte')}")
                print(f"  Date besoin: {alerte.get('date_besoin')}")
                print(f"  Délai passation: {alerte.get('delai_passation')}")
                print(f"  Écart jours: {alerte.get('ecart_jours')}")
                
                # Verify the formula: Db - Do - Dc
                if alerte.get('date_besoin') and alerte.get('delai_passation') is not None:
                    date_besoin = datetime.fromisoformat(alerte.get('date_besoin').replace('Z', '+00:00'))
                    date_observation = datetime.utcnow()
                    delai_passation = alerte.get('delai_passation')
                    
                    expected_ecart = (date_besoin - date_observation).days - delai_passation
                    actual_ecart = alerte.get('ecart_jours')
                    
                    # Allow for a small difference due to timing
                    if actual_ecart is not None and abs(expected_ecart - actual_ecart) <= 1:
                        print_test_result("Formula Db - Do - Dc", True, f"Expected: ~{expected_ecart}, Actual: {actual_ecart}")
                    else:
                        print_test_result("Formula Db - Do - Dc", False, f"Expected: ~{expected_ecart}, Actual: {actual_ecart}")
                else:
                    print_test_result("Formula Db - Do - Dc", False, "Missing data for formula verification")
            else:
                print_test_result("Formula Db - Do - Dc", False, "No alerts generated for critical article")
        else:
            print_test_result("Generate alerts for formula test", False, message)
    else:
        print_test_result("Get couverture data", False, message)
    
    # Test the formula for orders in progress (Cp-CMS) / (CMS+da)
    print("\nTesting formula for orders in progress: (Cp-CMS) / (CMS+da)")
    
    # This is harder to test directly as it requires orders in progress
    # We'll check if the endpoint handles the calculation correctly
    
    # Get all alerts after generation
    success, message, all_alertes = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if success and isinstance(all_alertes, list):
        commande_en_cours_alertes = [a for a in all_alertes if a.get("type_alerte") == "commande_en_cours"]
        
        if commande_en_cours_alertes:
            alerte = commande_en_cours_alertes[0]
            print("\nAlert for order in progress:")
            print(f"  Niveau alerte: {alerte.get('niveau_alerte')}")
            print(f"  Article ID: {alerte.get('article_id')}")
            print(f"  Commande ID: {alerte.get('commande_id')}")
            
            # We can't easily verify the formula without direct access to the database
            # But we can check if the alert has the expected fields
            expected_fields = ["niveau_alerte", "type_alerte", "article_id", "commande_id", "message", "recommandation"]
            missing_fields = [field for field in expected_fields if field not in alerte]
            
            if not missing_fields:
                print_test_result("Alert for order in progress", True, "Alert contains all expected fields")
            else:
                print_test_result("Alert for order in progress", False, f"Missing fields: {', '.join(missing_fields)}")
        else:
            print_test_result("Alert for order in progress", False, "No alerts found for orders in progress")
    else:
        print_test_result("Get all alerts", False, message)
    
    return True

def test_alert_thresholds(token, articles):
    print_header("Testing Alert Thresholds")
    
    if not articles:
        print_test_result("Test thresholds", False, "No test articles available")
        return False
    
    # Generate alerts
    success, message, alertes_data = make_request("post", "/stock/generer-alertes", token=token, expected_status=200)
    
    if not success:
        print_test_result("Generate alerts for threshold test", False, message)
        return False
    
    # Get all alerts
    success, message, all_alertes = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if not success or not isinstance(all_alertes, list):
        print_test_result("Get alerts for threshold test", False, message if not success else "Invalid response format")
        return False
    
    # Test thresholds for new orders
    print("\nTesting thresholds for new orders:")
    nouvelle_commande_alertes = [a for a in all_alertes if a.get("type_alerte") == "nouvelle_commande"]
    
    if nouvelle_commande_alertes:
        # Group alerts by level
        by_level = {}
        for alerte in nouvelle_commande_alertes:
            niveau = alerte.get("niveau_alerte")
            if niveau not in by_level:
                by_level[niveau] = []
            by_level[niveau].append(alerte)
        
        print(f"Found alerts with the following levels: {', '.join(by_level.keys())}")
        
        # Check if we have alerts for different thresholds
        if "urgent" in by_level:
            urgent_alert = by_level["urgent"][0]
            print(f"\nUrgent alert example (ecart_jours should be between -4 and 0):")
            print(f"  Écart jours: {urgent_alert.get('ecart_jours')}")
            
            if urgent_alert.get('ecart_jours') is not None and -4 < urgent_alert.get('ecart_jours') <= 0:
                print_test_result("Urgent threshold", True, f"Écart jours: {urgent_alert.get('ecart_jours')} is within expected range (-4 to 0)")
            else:
                print_test_result("Urgent threshold", False, f"Écart jours: {urgent_alert.get('ecart_jours')} is outside expected range (-4 to 0)")
        
        if "critique" in by_level:
            critique_alert = by_level["critique"][0]
            print(f"\nCritical alert example (ecart_jours should be < -4):")
            print(f"  Écart jours: {critique_alert.get('ecart_jours')}")
            
            if critique_alert.get('ecart_jours') is not None and critique_alert.get('ecart_jours') < -4:
                print_test_result("Critical threshold", True, f"Écart jours: {critique_alert.get('ecart_jours')} is < -4 as expected")
            else:
                print_test_result("Critical threshold", False, f"Écart jours: {critique_alert.get('ecart_jours')} is not < -4")
        
        if "normal" in by_level:
            normal_alert = by_level["normal"][0]
            print(f"\nNormal alert example (ecart_jours should be > 0):")
            print(f"  Écart jours: {normal_alert.get('ecart_jours')}")
            
            if normal_alert.get('ecart_jours') is not None and normal_alert.get('ecart_jours') > 0:
                print_test_result("Normal threshold", True, f"Écart jours: {normal_alert.get('ecart_jours')} is > 0 as expected")
            else:
                print_test_result("Normal threshold", False, f"Écart jours: {normal_alert.get('ecart_jours')} is not > 0")
    else:
        print_test_result("New orders thresholds", False, "No alerts found for new orders")
    
    # Test thresholds for orders in progress
    print("\nTesting thresholds for orders in progress:")
    commande_en_cours_alertes = [a for a in all_alertes if a.get("type_alerte") == "commande_en_cours"]
    
    if commande_en_cours_alertes:
        # For orders in progress, we need to get the couverture data to verify thresholds
        for alerte in commande_en_cours_alertes[:3]:  # Check first 3 alerts
            article_id = alerte.get("article_id")
            commande_id = alerte.get("commande_id")
            niveau = alerte.get("niveau_alerte")
            
            if not article_id or not commande_id:
                continue
            
            print(f"\nAlert for article {article_id}, commande {commande_id}:")
            print(f"  Niveau: {niveau}")
            
            # Get couverture data
            success, message, couverture_data = make_request("get", f"/stock/couverture/{article_id}", token=token, expected_status=200)
            
            if success and isinstance(couverture_data, dict):
                cms = couverture_data.get("couverture_minimale_securite")
                cr = couverture_data.get("couverture_actuelle")
                
                if cms is not None and cr is not None:
                    # We don't have direct access to Cp (couverture prévue), but we can use Cr as an approximation
                    cp = cr
                    da = couverture_data.get("delai_acheminement", 14) / 7  # Convert to weeks
                    
                    if (cms + da) > 0:
                        pourcentage = (cp - cms) / (cms + da)
                        print(f"  Approximated (Cp-CMS)/(CMS+da): {pourcentage:.2f}")
                        
                        # Check if the alert level matches the expected threshold
                        if niveau == "normal" and pourcentage > 0.1:
                            print_test_result(f"Normal threshold (> 10%)", True, f"Pourcentage: {pourcentage:.2f} > 0.1")
                        elif niveau == "a_suivre" and 0 < pourcentage <= 0.1:
                            print_test_result(f"À suivre threshold (0-10%)", True, f"Pourcentage: {pourcentage:.2f} is between 0 and 0.1")
                        elif niveau == "urgent" and pourcentage <= 0:
                            print_test_result(f"Urgent threshold (< 0%)", True, f"Pourcentage: {pourcentage:.2f} <= 0")
                        else:
                            print_test_result(f"{niveau} threshold", False, f"Pourcentage: {pourcentage:.2f} doesn't match expected range for {niveau}")
                    else:
                        print_test_result("Calculate percentage", False, "Denominator (CMS+da) is zero or negative")
                else:
                    print_test_result("Get CMS and Cr", False, "Missing CMS or Cr values")
            else:
                print_test_result("Get couverture data", False, message if not success else "Invalid response format")
    else:
        print_test_result("Orders in progress thresholds", False, "No alerts found for orders in progress")
    
    return True

def test_alert_types(token):
    print_header("Testing Alert Types")
    
    # Get all alerts
    success, message, all_alertes = make_request("get", "/stock/alertes-avancees", token=token, expected_status=200)
    
    if not success or not isinstance(all_alertes, list):
        print_test_result("Get alerts for type test", False, message if not success else "Invalid response format")
        return False
    
    # Count alerts by type
    alert_types = {}
    for alerte in all_alertes:
        type_alerte = alerte.get("type_alerte")
        if type_alerte not in alert_types:
            alert_types[type_alerte] = 0
        alert_types[type_alerte] += 1
    
    print(f"Found alerts with the following types: {alert_types}")
    
    # Check if we have the expected alert types
    expected_types = ["nouvelle_commande", "commande_en_cours"]
    missing_types = [t for t in expected_types if t not in alert_types]
    
    if not missing_types:
        print_test_result("Alert types", True, f"Found all expected alert types: {', '.join(expected_types)}")
    else:
        print_test_result("Alert types", False, f"Missing alert types: {', '.join(missing_types)}")
    
    # Check if alerts have the expected fields based on their type
    for type_alerte in alert_types:
        alerts_of_type = [a for a in all_alertes if a.get("type_alerte") == type_alerte]
        if not alerts_of_type:
            continue
        
        sample_alert = alerts_of_type[0]
        print(f"\nSample alert of type '{type_alerte}':")
        
        if type_alerte == "nouvelle_commande":
            expected_fields = ["article_id", "niveau_alerte", "date_besoin", "delai_passation", "ecart_jours", "message", "recommandation"]
        elif type_alerte == "commande_en_cours":
            expected_fields = ["article_id", "commande_id", "niveau_alerte", "message", "recommandation"]
        else:
            expected_fields = ["article_id", "niveau_alerte", "message", "recommandation"]
        
        missing_fields = [field for field in expected_fields if field not in sample_alert]
        
        if not missing_fields:
            print_test_result(f"{type_alerte} fields", True, f"Alert contains all expected fields: {', '.join(expected_fields)}")
        else:
            print_test_result(f"{type_alerte} fields", False, f"Missing fields: {', '.join(missing_fields)}")
        
        # Print sample alert details
        for field in expected_fields:
            if field in sample_alert:
                print(f"  {field}: {sample_alert[field]}")
    
    return True

def run_tests():
    print_header("STARTING ADVANCED ALERT SYSTEM TESTS")
    
    # Login
    token = login()
    if not token:
        print("Authentication failed, cannot proceed with tests")
        return False
    
    # Create test data
    supplier_id, articles, commande_id = create_test_data(token)
    
    # Test GET /api/stock/alertes-avancees
    success, initial_alertes = test_get_alertes_avancees(token)
    
    # Test POST /api/stock/generer-alertes
    success, generated_alertes = test_generer_alertes(token)
    
    # Test alert formulas
    test_alert_formulas(token, articles)
    
    # Test alert thresholds
    test_alert_thresholds(token, articles)
    
    # Test alert types
    test_alert_types(token)
    
    # Final check of alerts
    print_header("Final Check of Alerts")
    success, final_alertes = test_get_alertes_avancees(token)
    
    if success and isinstance(final_alertes, list):
        initial_count = len(initial_alertes) if initial_alertes else 0
        final_count = len(final_alertes)
        
        print(f"Initial alert count: {initial_count}")
        print(f"Final alert count: {final_count}")
        print(f"Difference: {final_count - initial_count}")
        
        if final_count > initial_count:
            print_test_result("Alert generation", True, f"Successfully generated {final_count - initial_count} new alerts")
        else:
            print_test_result("Alert generation", False, "No new alerts were generated")
    
    print_header("ADVANCED ALERT SYSTEM TESTS COMPLETED")
    return True

if __name__ == "__main__":
    run_tests()