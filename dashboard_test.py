import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://4b6c9fbc-ce17-45c7-ad60-5c384ec9314c.preview.emergentagent.com/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123",
    "nom": "Admin",
    "prenom": "Test",
    "role": "administrateur"
}

def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

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

def test_auth_register(user_data):
    print_header("Testing User Registration")
    success, message, data = make_request("post", "/auth/register", user_data, expected_status=200)
    
    if success:
        print(f"✅ Created user: {user_data['email']}")
        return True
    else:
        print(f"❌ Failed to register user: {message}")
        return False

def test_auth_login(user_data):
    print_header("Testing User Login")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print(f"✅ Logged in as: {user_data['email']}")
        return data["access_token"]
    else:
        print(f"❌ Failed to login: {message}")
        return None

def create_test_fournisseur(token):
    print_header("Creating Test Fournisseur")
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
        print(f"✅ Created fournisseur: {data['nom']} (ID: {data['id']})")
        return data["id"]
    else:
        print(f"❌ Failed to create fournisseur: {message}")
        return None

def create_test_article(token, fournisseur_id):
    print_header("Creating Test Article")
    article_data = {
        "reference": f"ART-{uuid.uuid4().hex[:6]}",
        "nom": f"Article Test {uuid.uuid4().hex[:6]}",
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
        print(f"✅ Created article: {data['nom']} (ID: {data['id']})")
        return data["id"]
    else:
        print(f"❌ Failed to create article: {message}")
        return None

def create_test_commande(token, fournisseur_id, article_id, status="brouillon"):
    print_header(f"Creating Test Commande with status: {status}")
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
        "notes": f"Commande test avec status {status}"
    }
    
    success, message, data = make_request("post", "/commandes", commande_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print(f"✅ Created commande: {data['numero_commande']} (ID: {data['id']}) with status: {data['status']}")
        return data["id"]
    else:
        print(f"❌ Failed to create commande: {message}")
        return None

def update_commande_status(token, commande_id, new_status):
    print_header(f"Updating Commande Status to {new_status}")
    update_data = {
        "status": new_status
    }
    
    success, message, data = make_request("put", f"/commandes/{commande_id}", update_data, token=token, expected_status=200)
    
    if success and data and data["status"] == new_status:
        print(f"✅ Successfully updated commande status to {new_status}")
        return True
    else:
        print(f"❌ Failed to update commande status: {message}")
        return False

def create_test_alerte(token, article_id):
    print_header("Creating Test Alerte")
    alerte_data = {
        "type": "stock_bas",
        "priorite": "high",
        "titre": "Stock bas pour article test",
        "message": "Le stock de l'article test est en dessous du seuil minimum",
        "article_id": article_id,
        "lue": False
    }
    
    success, message, data = make_request("post", "/alertes/test-create", alerte_data, token=token, expected_status=200)
    
    if success and data and "id" in data:
        print(f"✅ Created alerte: {data['titre']} (ID: {data['id']})")
        return data["id"]
    else:
        print(f"❌ Failed to create alerte: {message}")
        return None

def test_dashboard_stats():
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
            return False
        
        # Check if all values are non-zero
        zero_fields = [field for field in required_fields if stats_data.get(field, 0) == 0]
        
        if zero_fields:
            print(f"⚠️ The following fields have zero values: {', '.join(zero_fields)}")
            print("Creating test data to populate these fields...")
            
            # Create test data
            fournisseur_id = create_test_fournisseur(admin_token)
            if fournisseur_id:
                article_id = create_test_article(admin_token, fournisseur_id)
                if article_id:
                    commande_id = create_test_commande(admin_token, fournisseur_id, article_id)
                    if commande_id:
                        # Update commande status to test commandes_en_cours
                        update_commande_status(admin_token, commande_id, "en_attente")
                    
                    # Create an alert
                    create_test_alerte(admin_token, article_id)
            
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
                return False
        else:
            print("✅ All fields have non-zero values.")
        
        return True
    else:
        print(f"❌ Failed to retrieve dashboard stats from /api/dashboard/stats")
        print(f"   Error: {message}")
        return False

if __name__ == "__main__":
    test_dashboard_stats()