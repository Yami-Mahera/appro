import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://fd9177f2-1bcf-486d-b5e9-ac472b93d60d.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "admin123"
}

def login():
    response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDENTIALS)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def test_alertes_avancees():
    token = login()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test GET /api/stock/alertes-avancees
    print("\nTesting GET /api/stock/alertes-avancees")
    response = requests.get(f"{BASE_URL}/stock/alertes-avancees", headers=headers)
    if response.status_code == 200:
        alertes = response.json()
        print(f"Retrieved {len(alertes)} alertes avancées")
    else:
        print(f"Failed to get alertes avancées: {response.text}")
    
    # 2. Test POST /api/stock/generer-alertes
    print("\nTesting POST /api/stock/generer-alertes")
    response = requests.post(f"{BASE_URL}/stock/generer-alertes", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"Generated {len(result.get('alertes', []))} alertes")
        
        # Print details of generated alerts
        for i, alerte in enumerate(result.get("alertes", [])[:5]):
            print(f"\nAlert {i+1}:")
            print(f"  Type: {alerte.get('type_alerte')}")
            print(f"  Niveau: {alerte.get('niveau_alerte')}")
            print(f"  Message: {alerte.get('message')}")
            print(f"  Recommandation: {alerte.get('recommandation')}")
    else:
        print(f"Failed to generate alertes: {response.text}")
    
    # 3. Check alertes again after generation
    print("\nChecking alertes after generation")
    response = requests.get(f"{BASE_URL}/stock/alertes-avancees", headers=headers)
    if response.status_code == 200:
        alertes = response.json()
        print(f"Retrieved {len(alertes)} alertes avancées after generation")
        
        # Print details of the first few alerts
        for i, alerte in enumerate(alertes[:5]):
            print(f"\nAlert {i+1}:")
            print(f"  Type: {alerte.get('type_alerte')}")
            print(f"  Niveau: {alerte.get('niveau_alerte')}")
            print(f"  Message: {alerte.get('message')}")
            print(f"  Recommandation: {alerte.get('recommandation')}")
    else:
        print(f"Failed to get alertes avancées after generation: {response.text}")

if __name__ == "__main__":
    test_alertes_avancees()