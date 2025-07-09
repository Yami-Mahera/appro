import requests
import json
import uuid
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123"
}

def authenticate():
    print("Authenticating...")
    response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_USER)
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            print("✅ Authentication successful")
            return data["access_token"]
        else:
            print("❌ Authentication failed - No access token in response")
            print(f"   Response: {data}")
            return None
    elif response.status_code == 401:
        print("❌ Authentication failed - Invalid credentials")
        print("Trying to register the admin user...")
        
        # Try to register the admin user
        register_data = {
            "email": ADMIN_USER["email"],
            "password": ADMIN_USER["password"],
            "nom": "Admin",
            "prenom": "Test",
            "role": "administrateur"
        }
        
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if register_response.status_code == 200:
            print("✅ Admin user registered successfully")
            # Try to login again
            login_response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_USER)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                if "access_token" in login_data:
                    print("✅ Authentication successful after registration")
                    return login_data["access_token"]
                else:
                    print("❌ Authentication failed after registration - No access token in response")
                    print(f"   Response: {login_data}")
                    return None
            else:
                print(f"❌ Authentication failed after registration - Status code: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return None
        else:
            print(f"❌ Failed to register admin user - Status code: {register_response.status_code}")
            print(f"   Response: {register_response.text}")
            return None
    else:
        print(f"❌ Authentication failed - Status code: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def create_test_data(token):
    print("\nCreating test data...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Create a test fournisseur
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
    
    response = requests.post(f"{BASE_URL}/fournisseurs", json=fournisseur_data, headers=headers)
    
    if response.status_code == 200:
        fournisseur_id = response.json()["id"]
        print(f"✅ Created test fournisseur with ID: {fournisseur_id}")
        
        # Create a test article
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
            "stock_actuel": 5,
            "duree_vie": 365,
            "emplacement_stockage": "Étagère A1"
        }
        
        response = requests.post(f"{BASE_URL}/articles", json=article_data, headers=headers)
        
        if response.status_code == 200:
            article_id = response.json()["id"]
            print(f"✅ Created test article with ID: {article_id}")
            
            # Create multiple commandes for pagination testing
            commande_ids = []
            for i in range(15):  # Create 15 commandes to ensure we have enough for pagination
                commande_data = {
                    "fournisseur_id": fournisseur_id,
                    "lignes": [
                        {
                            "article_id": article_id,
                            "quantite": 10 + i,
                            "prix_unitaire": 19.99,
                            "total": (10 + i) * 19.99
                        }
                    ],
                    "date_livraison_prevue": (datetime.now() + timedelta(days=7 + i)).isoformat(),
                    "notes": f"Commande test pagination {i+1}"
                }
                
                response = requests.post(f"{BASE_URL}/commandes", json=commande_data, headers=headers)
                if response.status_code == 200:
                    commande_id = response.json()["id"]
                    commande_ids.append(commande_id)
                    print(f"✅ Created test commande {i+1} with ID: {commande_id}")
                else:
                    print(f"❌ Failed to create test commande {i+1}")
                    print(f"   Response status code: {response.status_code}")
                    print(f"   Response text: {response.text}")
            
            print(f"✅ Created {len(commande_ids)} test commandes")
            return True
        else:
            print(f"❌ Failed to create test article")
            print(f"   Response status code: {response.status_code}")
            print(f"   Response text: {response.text}")
            return False
    else:
        print(f"❌ Failed to create test fournisseur")
        print(f"   Response status code: {response.status_code}")
        print(f"   Response text: {response.text}")
        return False

def test_commandes_pagination():
    print("Testing commandes pagination API...")
    
    # Authenticate first
    token = authenticate()
    if not token:
        print("Cannot proceed with tests without authentication")
        return
    
    # Create test data
    create_test_data(token)
    
    # Set up headers with authentication token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Test 1: Basic pagination - limit and skip
    print("\nTest 1: GET /api/commandes?limit=5&skip=0")
    response = requests.get(f"{BASE_URL}/commandes?limit=5&skip=0", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved commandes with limit=5, skip=0")
        print(f"   Response status code: {response.status_code}")
        print(f"   Response structure: {list(data.keys())}")
        
        if "commandes" in data:
            print(f"   Number of commandes: {len(data['commandes'])}")
        
        if "total" in data:
            print(f"   Total commandes: {data['total']}")
        
        if "limit" in data:
            print(f"   Limit: {data['limit']}")
        
        if "skip" in data:
            print(f"   Skip: {data['skip']}")
        
        if "has_next" in data:
            print(f"   Has next page: {data['has_next']}")
        
        if "has_previous" in data:
            print(f"   Has previous page: {data['has_previous']}")
            
        # Store first page commandes for comparison
        first_page_commandes = data['commandes']
    else:
        print(f"❌ Failed to retrieve commandes with limit=5, skip=0")
        print(f"   Response status code: {response.status_code}")
        print(f"   Response text: {response.text}")
        return
    
    # Test 2: Next page - limit=5, skip=5
    print("\nTest 2: GET /api/commandes?limit=5&skip=5")
    response = requests.get(f"{BASE_URL}/commandes?limit=5&skip=5", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved commandes with limit=5, skip=5")
        print(f"   Response status code: {response.status_code}")
        
        if "commandes" in data:
            print(f"   Number of commandes: {len(data['commandes'])}")
        
        if "has_previous" in data:
            print(f"   Has previous page: {data['has_previous']}")
            if data['has_previous']:
                print("   ✅ has_previous is correctly set to True for second page")
            else:
                print("   ❌ has_previous should be True for second page but is False")
        
        # Check if commandes are different from first page
        if first_page_commandes and len(data['commandes']) > 0:
            first_page_ids = [commande["id"] for commande in first_page_commandes]
            second_page_ids = [commande["id"] for commande in data['commandes']]
            
            overlap = set(first_page_ids).intersection(set(second_page_ids))
            if not overlap:
                print("   ✅ No overlap between first and second page - pagination working correctly")
            else:
                print(f"   ❌ Found {len(overlap)} overlapping commandes between pages - pagination may not be working correctly")
    else:
        print(f"❌ Failed to retrieve commandes with limit=5, skip=5")
        print(f"   Response status code: {response.status_code}")
        print(f"   Response text: {response.text}")
    
    # Test 3: Filter by status
    print("\nTest 3: GET /api/commandes?status=brouillon&limit=5&skip=0")
    response = requests.get(f"{BASE_URL}/commandes?status=brouillon&limit=5&skip=0", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved commandes with status=brouillon, limit=5, skip=0")
        print(f"   Response status code: {response.status_code}")
        
        if "commandes" in data and "total" in data:
            print(f"   Number of commandes: {len(data['commandes'])}")
            print(f"   Total matching status: {data['total']}")
            
            # Check if all returned commandes have status=brouillon
            if len(data['commandes']) > 0:
                all_brouillon = all(commande["status"] == "brouillon" for commande in data['commandes'])
                if all_brouillon:
                    print("   ✅ All returned commandes have status=brouillon - filtering working correctly")
                else:
                    print("   ❌ Some returned commandes do not have status=brouillon - filtering may not be working correctly")
    else:
        print(f"❌ Failed to retrieve commandes with status filter")
        print(f"   Response status code: {response.status_code}")
        print(f"   Response text: {response.text}")
    
    # Test 4: Date range filter
    print("\nTest 4: GET /api/commandes with date range filter")
    date_from = (datetime.now() - timedelta(days=1)).isoformat()
    date_to = (datetime.now() + timedelta(days=30)).isoformat()
    
    response = requests.get(f"{BASE_URL}/commandes?date_from={date_from}&date_to={date_to}&limit=5&skip=0", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Successfully retrieved commandes with date range filter, limit=5, skip=0")
        print(f"   Response status code: {response.status_code}")
        
        if "commandes" in data and "total" in data:
            print(f"   Number of commandes: {len(data['commandes'])}")
            print(f"   Total matching date range: {data['total']}")
    else:
        print(f"❌ Failed to retrieve commandes with date range filter")
        print(f"   Response status code: {response.status_code}")
        print(f"   Response text: {response.text}")
    
    # Test 5: Filter by fournisseur_id
    if len(first_page_commandes) > 0:
        fournisseur_id = first_page_commandes[0]["fournisseur_id"]
        print(f"\nTest 5: GET /api/commandes?fournisseur_id={fournisseur_id}&limit=5&skip=0")
        response = requests.get(f"{BASE_URL}/commandes?fournisseur_id={fournisseur_id}&limit=5&skip=0", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved commandes with fournisseur_id filter, limit=5, skip=0")
            print(f"   Response status code: {response.status_code}")
            
            if "commandes" in data and "total" in data:
                print(f"   Number of commandes: {len(data['commandes'])}")
                print(f"   Total matching fournisseur_id: {data['total']}")
                
                # Check if all returned commandes have the correct fournisseur_id
                if len(data['commandes']) > 0:
                    all_correct_fournisseur = all(commande["fournisseur_id"] == fournisseur_id for commande in data['commandes'])
                    if all_correct_fournisseur:
                        print("   ✅ All returned commandes have the correct fournisseur_id - filtering working correctly")
                    else:
                        print("   ❌ Some returned commandes do not have the correct fournisseur_id - filtering may not be working correctly")
        else:
            print(f"❌ Failed to retrieve commandes with fournisseur_id filter")
            print(f"   Response status code: {response.status_code}")
            print(f"   Response text: {response.text}")
    
    print("\nCommandes pagination tests completed")

if __name__ == "__main__":
    test_commandes_pagination()