#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://8a14b788-bf4b-4aff-be7d-f8941fcf1e77.preview.emergentagent.com/api"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_subheader(message):
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * 50}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def make_request(method, endpoint, data=None, token=None, params=None, expected_status=200):
    url = f"{BACKEND_URL}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        print_info(f"Making {method.upper()} request to {url}")
        if data:
            print_info(f"Request data: {json.dumps(data, indent=2)}")
        if params:
            print_info(f"Request params: {params}")
            
        if method.lower() == "get":
            response = requests.get(url, headers=headers, params=params)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code != expected_status:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
        
        if response.status_code == 204:  # No content
            return True
        
        try:
            json_response = response.json()
            return json_response
        except json.JSONDecodeError:
            print_error(f"Failed to parse JSON response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None

def login():
    print_subheader("Logging in as admin")
    
    login_data = {
        "email": "admin@test.com",
        "password": "Admin@123456"
    }
    
    response = make_request("post", "/auth/login", login_data)
    
    if not response:
        print_error("Failed to login")
        return None
    
    print_success("Successfully logged in")
    return response["access_token"]

def test_article_lookup():
    print_header("TESTING ARTICLE LOOKUP")
    
    token = login()
    if not token:
        return
    
    # Get all articles
    print_subheader("Getting all articles")
    articles = make_request("get", "/articles", token=token)
    
    if not articles or len(articles) == 0:
        print_error("No articles found")
        return
    
    print_success(f"Found {len(articles)} articles")
    
    # Test lookup for each article
    print_subheader("Testing article lookup by ID")
    
    for i, article in enumerate(articles):
        article_id = article["id"]
        print_info(f"Looking up article {i+1}/{len(articles)}: {article_id}")
        
        article_detail = make_request("get", f"/articles/{article_id}", token=token)
        
        if not article_detail:
            print_error(f"Failed to lookup article {article_id}")
        else:
            print_success(f"Successfully looked up article {article_id}: {article_detail['nom']}")

def test_reporting_api():
    print_header("TESTING REPORTING API")
    
    token = login()
    if not token:
        return
    
    # Test fournisseurs report
    print_subheader("Testing fournisseurs report")
    response = make_request("get", "/reports/fournisseurs", token=token)
    
    if not response:
        print_error("Failed to get fournisseurs report")
    else:
        print_success(f"Successfully got fournisseurs report: {len(response)} fournisseurs")
    
    # Test articles report
    print_subheader("Testing articles report")
    response = make_request("get", "/reports/articles", token=token)
    
    if not response:
        print_error("Failed to get articles report")
    else:
        print_success(f"Successfully got articles report: {len(response)} articles")
    
    # Test commandes report
    print_subheader("Testing commandes report")
    response = make_request("get", "/reports/commandes", token=token)
    
    if not response:
        print_error("Failed to get commandes report")
    else:
        print_success(f"Successfully got commandes report: {len(response)} commandes")
    
    # Test synthese report
    print_subheader("Testing synthese report")
    response = make_request("get", "/reports/synthese", token=token)
    
    if not response:
        print_error("Failed to get synthese report")
    else:
        print_success("Successfully got synthese report")
        for key, value in response.items():
            print_info(f"{key}: {value}")

def test_create_commande():
    print_header("TESTING COMMANDE CREATION")
    
    token = login()
    if not token:
        return
    
    # Get a fournisseur
    print_subheader("Getting a fournisseur")
    fournisseurs = make_request("get", "/fournisseurs", token=token)
    
    if not fournisseurs or len(fournisseurs) == 0:
        print_error("No fournisseurs found")
        return
    
    fournisseur_id = fournisseurs[0]["id"]
    print_success(f"Using fournisseur: {fournisseurs[0]['nom']} (ID: {fournisseur_id})")
    
    # Get articles
    print_subheader("Getting articles")
    articles = make_request("get", "/articles", token=token)
    
    if not articles or len(articles) == 0:
        print_error("No articles found")
        return
    
    print_success(f"Found {len(articles)} articles")
    
    # Create commande
    print_subheader("Creating commande")
    
    # Create lignes de commande
    lignes = []
    for i in range(min(2, len(articles))):
        article = articles[i]
        article_id = article["id"]
        
        # Verify article can be looked up by ID
        article_detail = make_request("get", f"/articles/{article_id}", token=token)
        if not article_detail:
            print_error(f"Failed to lookup article {article_id}, skipping")
            continue
        
        quantite = i + 1
        prix_unitaire = article["prix_unitaire"]
        total = quantite * prix_unitaire
        
        lignes.append({
            "article_id": article_id,
            "quantite": quantite,
            "prix_unitaire": prix_unitaire,
            "total": total
        })
    
    if not lignes:
        print_error("No lignes created, cannot create commande")
        return
    
    commande_data = {
        "fournisseur_id": fournisseur_id,
        "lignes": lignes,
        "date_livraison_prevue": (datetime.now().isoformat()),
        "notes": "Commande test diagnostic"
    }
    
    response = make_request("post", "/commandes", commande_data, token=token)
    
    if not response:
        print_error("Failed to create commande")
    else:
        print_success(f"Successfully created commande: {response['numero_commande']}")
        print_info(f"Commande ID: {response['id']}")
        print_info(f"Total HT: {response['total_ht']}")
        print_info(f"Total TTC: {response['total_ttc']}")

if __name__ == "__main__":
    test_article_lookup()
    test_create_commande()
    test_reporting_api()