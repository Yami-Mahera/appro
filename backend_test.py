#!/usr/bin/env python3
import requests
import json
import random
import string
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import sys
import os
from pprint import pprint

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://8a14b788-bf4b-4aff-be7d-f8941fcf1e77.preview.emergentagent.com/api"

# Test data
test_users = {
    "admin": {
        "email": f"admin_{int(time.time())}@test.com",
        "password": "Admin@123456",
        "nom": "Dupont",
        "prenom": "Jean",
        "role": "administrateur"
    },
    "manager": {
        "email": f"manager_{int(time.time())}@test.com",
        "password": "Manager@123456",
        "nom": "Martin",
        "prenom": "Sophie",
        "role": "manager"
    },
    "user": {
        "email": f"user_{int(time.time())}@test.com",
        "password": "User@123456",
        "nom": "Dubois",
        "prenom": "Pierre",
        "role": "utilisateur"
    }
}

# Store tokens and IDs
tokens = {}
user_ids = {}
fournisseur_ids = []
article_ids = []
commande_ids = []
alerte_ids = []

# Test results
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
}

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

def run_test(test_name, test_func, *args, **kwargs):
    print_subheader(f"Test: {test_name}")
    test_results["total"] += 1
    
    try:
        result = test_func(*args, **kwargs)
        if result:
            test_results["passed"] += 1
            print_success(f"Test '{test_name}' passed")
        else:
            test_results["failed"] += 1
            print_error(f"Test '{test_name}' failed")
        return result
    except Exception as e:
        test_results["failed"] += 1
        print_error(f"Test '{test_name}' failed with exception: {str(e)}")
        return False

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

# Authentication Tests
def test_register():
    print_subheader("Testing user registration")
    
    for role, user_data in test_users.items():
        print_info(f"Registering {role} user: {user_data['email']}")
        response = make_request("post", "/auth/register", user_data)
        
        if not response:
            print_error(f"Failed to register {role} user")
            return False
        
        print_success(f"Successfully registered {role} user: {response['email']}")
        user_ids[role] = response["id"]
    
    return True

def test_login():
    print_subheader("Testing user login")
    
    for role, user_data in test_users.items():
        print_info(f"Logging in as {role}: {user_data['email']}")
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = make_request("post", "/auth/login", login_data)
        
        if not response:
            print_error(f"Failed to login as {role}")
            return False
        
        tokens[role] = response["access_token"]
        print_success(f"Successfully logged in as {role}")
        print_info(f"Token: {tokens[role][:20]}...")
    
    return True

def test_get_current_user():
    print_subheader("Testing get current user")
    
    for role, token in tokens.items():
        print_info(f"Getting current user info for {role}")
        response = make_request("get", "/auth/me", token=token)
        
        if not response:
            print_error(f"Failed to get current user info for {role}")
            return False
        
        print_success(f"Successfully got current user info for {role}: {response['email']}")
        
        # Verify user data
        if response["email"] != test_users[role]["email"]:
            print_error(f"Email mismatch for {role}")
            return False
        
        if response["nom"] != test_users[role]["nom"]:
            print_error(f"Nom mismatch for {role}")
            return False
        
        if response["prenom"] != test_users[role]["prenom"]:
            print_error(f"Prenom mismatch for {role}")
            return False
        
        if response["role"] != test_users[role]["role"]:
            print_error(f"Role mismatch for {role}")
            return False
    
    return True

# Fournisseur Tests
def test_create_fournisseur():
    print_subheader("Testing fournisseur creation")
    
    # Only admin and manager can create fournisseurs
    for role in ["admin", "manager"]:
        if role not in tokens:
            print_warning(f"No token for {role}, skipping")
            continue
        
        print_info(f"Creating fournisseur as {role}")
        
        # Create 2 fournisseurs for testing
        for i in range(2):
            fournisseur_data = {
                "nom": f"Fournisseur Test {i+1}",
                "code_fournisseur": f"FRN{i+1}{int(time.time())}",
                "adresse": f"{i+10} Rue de la Paix",
                "ville": "Paris" if i % 2 == 0 else "Lyon",
                "code_postal": f"7500{i+1}",
                "pays": "France",
                "telephone": f"+33612345{i+10}",
                "email": f"contact{i+1}@fournisseur-test.com",
                "site_web": f"https://www.fournisseur-test{i+1}.com",
                "conditions_paiement": "30 jours",
                "delai_livraison_moyen": 5 + i,
                "contacts": [
                    {
                        "nom": "Dupont",
                        "prenom": "Jean",
                        "telephone": f"+33612345{i+20}",
                        "email": f"jean.dupont{i+1}@fournisseur-test.com",
                        "poste": "Directeur commercial"
                    },
                    {
                        "nom": "Martin",
                        "prenom": "Sophie",
                        "telephone": f"+33612345{i+30}",
                        "email": f"sophie.martin{i+1}@fournisseur-test.com",
                        "poste": "Responsable logistique"
                    }
                ]
            }
            
            response = make_request("post", "/fournisseurs", fournisseur_data, token=tokens[role])
            
            if not response:
                print_error(f"Failed to create fournisseur {i+1} as {role}")
                return False
            
            fournisseur_ids.append(response["id"])
            print_success(f"Successfully created fournisseur {i+1} as {role}: {response['nom']}")
    
    return True

def test_get_fournisseurs():
    print_subheader("Testing get fournisseurs")
    
    # Any authenticated user can get fournisseurs
    for role, token in tokens.items():
        print_info(f"Getting fournisseurs as {role}")
        
        response = make_request("get", "/fournisseurs", token=token)
        
        if not response:
            print_error(f"Failed to get fournisseurs as {role}")
            return False
        
        print_success(f"Successfully got fournisseurs as {role}: {len(response)} fournisseurs")
        
        # Verify that our created fournisseurs are in the list
        found_ids = [f["id"] for f in response]
        for fid in fournisseur_ids:
            if fid not in found_ids:
                print_error(f"Fournisseur {fid} not found in the list")
                return False
    
    return True

def test_get_fournisseur_by_id():
    print_subheader("Testing get fournisseur by ID")
    
    if not fournisseur_ids:
        print_warning("No fournisseur IDs available, skipping")
        return True
    
    # Any authenticated user can get a fournisseur by ID
    for role, token in tokens.items():
        for fid in fournisseur_ids:
            print_info(f"Getting fournisseur {fid} as {role}")
            
            response = make_request("get", f"/fournisseurs/{fid}", token=token)
            
            if not response:
                print_error(f"Failed to get fournisseur {fid} as {role}")
                return False
            
            print_success(f"Successfully got fournisseur {fid} as {role}: {response['nom']}")
    
    return True

def test_update_fournisseur():
    print_subheader("Testing update fournisseur")
    
    if not fournisseur_ids:
        print_warning("No fournisseur IDs available, skipping")
        return True
    
    # Only admin and manager can update fournisseurs
    for role in ["admin", "manager"]:
        if role not in tokens:
            print_warning(f"No token for {role}, skipping")
            continue
        
        fid = fournisseur_ids[0]
        print_info(f"Updating fournisseur {fid} as {role}")
        
        # Get current fournisseur data
        current_data = make_request("get", f"/fournisseurs/{fid}", token=tokens[role])
        if not current_data:
            print_error(f"Failed to get current fournisseur data for {fid}")
            return False
        
        # Update some fields
        update_data = {
            "nom": f"{current_data['nom']} (Updated)",
            "code_fournisseur": current_data["code_fournisseur"],
            "adresse": current_data["adresse"],
            "ville": current_data["ville"],
            "code_postal": current_data["code_postal"],
            "pays": current_data["pays"],
            "telephone": current_data["telephone"],
            "email": current_data["email"],
            "site_web": current_data["site_web"],
            "conditions_paiement": "45 jours",  # Updated
            "delai_livraison_moyen": current_data["delai_livraison_moyen"] + 1,  # Updated
            "contacts": current_data["contacts"]
        }
        
        response = make_request("put", f"/fournisseurs/{fid}", update_data, token=tokens[role])
        
        if not response:
            print_error(f"Failed to update fournisseur {fid} as {role}")
            return False
        
        print_success(f"Successfully updated fournisseur {fid} as {role}: {response['nom']}")
        
        # Verify updates
        if response["nom"] != update_data["nom"]:
            print_error(f"Name not updated correctly")
            return False
        
        if response["conditions_paiement"] != update_data["conditions_paiement"]:
            print_error(f"Conditions de paiement not updated correctly")
            return False
        
        if response["delai_livraison_moyen"] != update_data["delai_livraison_moyen"]:
            print_error(f"Délai de livraison not updated correctly")
            return False
    
    return True

def test_search_fournisseurs():
    print_subheader("Testing search fournisseurs")
    
    if not fournisseur_ids:
        print_warning("No fournisseur IDs available, skipping")
        return True
    
    # Any authenticated user can search fournisseurs
    role = "admin"  # Use admin for this test
    token = tokens.get(role)
    
    if not token:
        print_warning(f"No token for {role}, skipping")
        return True
    
    # Test search by name
    print_info("Testing search by name")
    response = make_request("get", "/fournisseurs", token=token, params={"search": "Fournisseur Test"})
    
    if not response:
        print_error("Failed to search fournisseurs by name")
        return False
    
    print_success(f"Successfully searched fournisseurs by name: {len(response)} results")
    
    # Test search by ville
    print_info("Testing search by ville")
    response = make_request("get", "/fournisseurs", token=token, params={"ville": "Paris"})
    
    if not response:
        print_error("Failed to search fournisseurs by ville")
        return False
    
    print_success(f"Successfully searched fournisseurs by ville: {len(response)} results")
    
    # Test search by pays
    print_info("Testing search by pays")
    response = make_request("get", "/fournisseurs", token=token, params={"pays": "France"})
    
    if not response:
        print_error("Failed to search fournisseurs by pays")
        return False
    
    print_success(f"Successfully searched fournisseurs by pays: {len(response)} results")
    
    return True

# Article Tests
def test_create_article():
    print_subheader("Testing article creation")
    
    if not fournisseur_ids:
        print_warning("No fournisseur IDs available, skipping")
        return True
    
    # Only admin and manager can create articles
    for role in ["admin", "manager"]:
        if role not in tokens:
            print_warning(f"No token for {role}, skipping")
            continue
        
        print_info(f"Creating article as {role}")
        
        # Create 3 articles for testing
        for i in range(3):
            article_data = {
                "reference": f"ART{i+1}{int(time.time())}",
                "nom": f"Article Test {i+1}",
                "description": f"Description de l'article test {i+1}",
                "famille": f"Famille {i % 2 + 1}",
                "fournisseur_id": fournisseur_ids[i % len(fournisseur_ids)],
                "prix_unitaire": 10.5 + i * 5.25,
                "unite": "pièce" if i % 2 == 0 else "kg",
                "seuil_min": 10,
                "seuil_max": 100,
                "stock_actuel": 5 if i == 0 else 20,  # First article has stock below threshold
                "duree_vie": 365,
                "emplacement_stockage": f"Étagère {i+1}"
            }
            
            response = make_request("post", "/articles", article_data, token=tokens[role])
            
            if not response:
                print_error(f"Failed to create article {i+1} as {role}")
                return False
            
            article_ids.append(response["id"])
            print_success(f"Successfully created article {i+1} as {role}: {response['nom']}")
    
    return True

def test_get_articles():
    print_subheader("Testing get articles")
    
    # Any authenticated user can get articles
    for role, token in tokens.items():
        print_info(f"Getting articles as {role}")
        
        response = make_request("get", "/articles", token=token)
        
        if not response:
            print_error(f"Failed to get articles as {role}")
            return False
        
        print_success(f"Successfully got articles as {role}: {len(response)} articles")
        
        # Verify that our created articles are in the list
        found_ids = [a["id"] for a in response]
        for aid in article_ids:
            if aid not in found_ids:
                print_error(f"Article {aid} not found in the list")
                return False
    
    return True

def test_get_articles_stock_bas():
    print_subheader("Testing get articles with low stock")
    
    # Any authenticated user can get articles with low stock
    for role, token in tokens.items():
        print_info(f"Getting articles with low stock as {role}")
        
        response = make_request("get", "/articles/stock-bas", token=token)
        
        if not response:
            print_error(f"Failed to get articles with low stock as {role}")
            return False
        
        print_success(f"Successfully got articles with low stock as {role}: {len(response)} articles")
        
        # Verify that at least one article has stock below threshold
        if len(response) == 0:
            print_warning("No articles with low stock found")
        else:
            print_info(f"Found {len(response)} articles with low stock")
            for article in response:
                print_info(f"Article {article['nom']} has stock {article['stock_actuel']} (below threshold {article['seuil_min']})")
    
    return True

def test_filter_articles():
    print_subheader("Testing filter articles")
    
    if not article_ids or not fournisseur_ids:
        print_warning("No article or fournisseur IDs available, skipping")
        return True
    
    # Any authenticated user can filter articles
    role = "admin"  # Use admin for this test
    token = tokens.get(role)
    
    if not token:
        print_warning(f"No token for {role}, skipping")
        return True
    
    # Test filter by famille
    print_info("Testing filter by famille")
    response = make_request("get", "/articles", token=token, params={"famille": "Famille 1"})
    
    if not response:
        print_error("Failed to filter articles by famille")
        return False
    
    print_success(f"Successfully filtered articles by famille: {len(response)} results")
    
    # Test filter by fournisseur_id
    print_info("Testing filter by fournisseur_id")
    response = make_request("get", "/articles", token=token, params={"fournisseur_id": fournisseur_ids[0]})
    
    if not response:
        print_error("Failed to filter articles by fournisseur_id")
        return False
    
    print_success(f"Successfully filtered articles by fournisseur_id: {len(response)} results")
    
    # Test filter by stock_bas
    print_info("Testing filter by stock_bas")
    response = make_request("get", "/articles", token=token, params={"stock_bas": True})
    
    if not response:
        print_error("Failed to filter articles by stock_bas")
        return False
    
    print_success(f"Successfully filtered articles by stock_bas: {len(response)} results")
    
    return True

# Commande Tests
def test_create_commande():
    print_subheader("Testing commande creation")
    
    if not article_ids or not fournisseur_ids:
        print_warning("No article or fournisseur IDs available, skipping")
        return True
    
    # Only admin and manager can create commandes
    for role in ["admin", "manager"]:
        if role not in tokens:
            print_warning(f"No token for {role}, skipping")
            continue
        
        print_info(f"Creating commande as {role}")
        
        # Create 2 commandes for testing
        for i in range(2):
            # Get fournisseur for this commande
            fournisseur_id = fournisseur_ids[i % len(fournisseur_ids)]
            print_info(f"Using fournisseur_id: {fournisseur_id}")
            
            # Verify fournisseur exists
            fournisseur = make_request("get", f"/fournisseurs/{fournisseur_id}", token=tokens[role])
            if not fournisseur:
                print_error(f"Failed to get fournisseur {fournisseur_id}")
                print_info("Skipping commande creation due to fournisseur lookup failure")
                continue
            
            print_info(f"Fournisseur verified: {fournisseur['nom']}")
            
            # Create lignes de commande
            lignes = []
            for j in range(2):  # 2 lines per commande
                if not article_ids:
                    print_error("No article IDs available")
                    continue
                    
                article_id = article_ids[(i + j) % len(article_ids)]
                print_info(f"Using article_id: {article_id}")
                
                # Get article details to use the correct price
                article = make_request("get", f"/articles/{article_id}", token=tokens[role])
                if not article:
                    print_error(f"Failed to get article {article_id}")
                    print_info("This is likely the cause of the 404 error in commande creation")
                    print_info("Checking if article exists in the database...")
                    
                    # Try to get all articles to see if our ID is valid
                    all_articles = make_request("get", "/articles", token=tokens[role])
                    if all_articles:
                        found = False
                        for a in all_articles:
                            if a["id"] == article_id:
                                found = True
                                break
                        
                        if found:
                            print_info(f"Article {article_id} exists in the database but can't be retrieved by ID")
                        else:
                            print_info(f"Article {article_id} does not exist in the database")
                    
                    continue
                
                print_info(f"Article verified: {article['nom']}")
                
                quantite = j + 1
                prix_unitaire = article["prix_unitaire"]
                total = quantite * prix_unitaire
                
                lignes.append({
                    "article_id": article_id,
                    "quantite": quantite,
                    "prix_unitaire": prix_unitaire,
                    "total": total
                })
            
            if not lignes:
                print_error("No lignes created, skipping commande creation")
                continue
            
            commande_data = {
                "fournisseur_id": fournisseur_id,
                "lignes": lignes,
                "date_livraison_prevue": (datetime.now() + timedelta(days=7)).isoformat(),
                "notes": f"Commande test {i+1}"
            }
            
            print_info(f"Commande data prepared: {json.dumps(commande_data, indent=2)}")
            
            response = make_request("post", "/commandes", commande_data, token=tokens[role])
            
            if not response:
                print_error(f"Failed to create commande {i+1} as {role}")
                continue
            
            commande_ids.append(response["id"])
            print_success(f"Successfully created commande {i+1} as {role}: {response['numero_commande']}")
            
            # Verify automatic calculations
            expected_total_ht = sum(ligne["total"] for ligne in lignes)
            expected_total_ttc = expected_total_ht * 1.2  # 20% TVA
            
            if abs(response["total_ht"] - expected_total_ht) > 0.01:
                print_error(f"Total HT calculation incorrect: expected {expected_total_ht}, got {response['total_ht']}")
                return False
            
            if abs(response["total_ttc"] - expected_total_ttc) > 0.01:
                print_error(f"Total TTC calculation incorrect: expected {expected_total_ttc}, got {response['total_ttc']}")
                return False
            
            print_success(f"Automatic calculations verified: Total HT = {response['total_ht']}, Total TTC = {response['total_ttc']}")
    
    return len(commande_ids) > 0

def test_get_commandes():
    print_subheader("Testing get commandes")
    
    # Any authenticated user can get commandes
    for role, token in tokens.items():
        print_info(f"Getting commandes as {role}")
        
        response = make_request("get", "/commandes", token=token)
        
        if not response:
            print_error(f"Failed to get commandes as {role}")
            return False
        
        print_success(f"Successfully got commandes as {role}: {len(response)} commandes")
        
        # Verify that our created commandes are in the list
        found_ids = [c["id"] for c in response]
        for cid in commande_ids:
            if cid not in found_ids:
                print_error(f"Commande {cid} not found in the list")
                return False
    
    return True

# Dashboard Tests
def test_dashboard_stats():
    print_subheader("Testing dashboard stats")
    
    # Any authenticated user can get dashboard stats
    for role, token in tokens.items():
        print_info(f"Getting dashboard stats as {role}")
        
        response = make_request("get", "/dashboard/stats", token=token)
        
        if not response:
            print_error(f"Failed to get dashboard stats as {role}")
            return False
        
        print_success(f"Successfully got dashboard stats as {role}")
        
        # Verify that the stats contain the expected fields
        expected_fields = [
            "total_fournisseurs",
            "total_articles",
            "total_commandes",
            "alertes_non_lues",
            "articles_stock_bas",
            "commandes_en_cours"
        ]
        
        for field in expected_fields:
            if field not in response:
                print_error(f"Dashboard stats missing field: {field}")
                return False
            
            print_info(f"{field}: {response[field]}")
    
    return True

# Alerte Tests
def test_create_alerte():
    print_subheader("Testing alerte creation")
    
    if not article_ids:
        print_warning("No article IDs available, skipping")
        return True
    
    # Any authenticated user can create a test alerte
    for role, token in tokens.items():
        print_info(f"Creating test alerte as {role}")
        
        alerte_data = {
            "type": "stock_bas",
            "priorite": "high",
            "titre": f"Test Alerte {role}",
            "message": f"Ceci est une alerte de test créée par {role}",
            "article_id": article_ids[0]
        }
        
        response = make_request("post", "/alertes/test-create", alerte_data, token=token)
        
        if not response:
            print_error(f"Failed to create test alerte as {role}")
            return False
        
        alerte_ids.append(response["id"])
        print_success(f"Successfully created test alerte as {role}: {response['titre']}")
    
    return True

def test_get_alertes():
    print_subheader("Testing get alertes")
    
    # Any authenticated user can get alertes
    for role, token in tokens.items():
        print_info(f"Getting alertes as {role}")
        
        response = make_request("get", "/alertes", token=token)
        
        if not response:
            print_error(f"Failed to get alertes as {role}")
            return False
        
        print_success(f"Successfully got alertes as {role}: {len(response)} alertes")
        
        # Verify that our created alertes are in the list
        found_ids = [a["id"] for a in response]
        for aid in alerte_ids:
            if aid not in found_ids:
                print_error(f"Alerte {aid} not found in the list")
                return False
    
    return True

# Reporting Tests
def test_reporting_fournisseurs():
    print_subheader("Testing reporting fournisseurs")
    
    # Any authenticated user can get fournisseurs report
    for role, token in tokens.items():
        print_info(f"Getting fournisseurs report as {role}")
        
        response = make_request("get", "/reports/fournisseurs", token=token)
        
        if not response:
            print_error(f"Failed to get fournisseurs report as {role}")
            return False
        
        print_success(f"Successfully got fournisseurs report as {role}: {len(response)} fournisseurs")
    
    return True

def test_reporting_articles():
    print_subheader("Testing reporting articles")
    
    # Any authenticated user can get articles report
    for role, token in tokens.items():
        print_info(f"Getting articles report as {role}")
        
        response = make_request("get", "/reports/articles", token=token)
        
        if not response:
            print_error(f"Failed to get articles report as {role}")
            return False
        
        print_success(f"Successfully got articles report as {role}: {len(response)} articles")
    
    return True

def test_reporting_commandes():
    print_subheader("Testing reporting commandes")
    
    # Any authenticated user can get commandes report
    for role, token in tokens.items():
        print_info(f"Getting commandes report as {role}")
        
        response = make_request("get", "/reports/commandes", token=token)
        
        if not response:
            print_error(f"Failed to get commandes report as {role}")
            return False
        
        print_success(f"Successfully got commandes report as {role}: {len(response)} commandes")
    
    return True

def test_reporting_synthese():
    print_subheader("Testing reporting synthese")
    
    # Any authenticated user can get synthese report
    for role, token in tokens.items():
        print_info(f"Getting synthese report as {role}")
        
        response = make_request("get", "/reports/synthese", token=token)
        
        if not response:
            print_error(f"Failed to get synthese report as {role}")
            return False
        
        print_success(f"Successfully got synthese report as {role}")
        
        # Verify that the report contains the expected fields
        expected_fields = [
            "total_fournisseurs",
            "total_articles",
            "articles_stock_bas",
            "total_commandes",
            "valeur_totale_commandes",
            "valeur_totale_stock",
            "alertes_non_lues"
        ]
        
        for field in expected_fields:
            if field not in response:
                print_error(f"Synthese report missing field: {field}")
                return False
            
            print_info(f"{field}: {response[field]}")
    
    return True

def run_all_tests():
    print_header("BACKEND API TESTING")
    print_info(f"Testing backend API at: {BACKEND_URL}")
    
    # Authentication tests
    run_test("User Registration", test_register)
    run_test("User Login", test_login)
    run_test("Get Current User", test_get_current_user)
    
    # Fournisseur tests
    run_test("Create Fournisseur", test_create_fournisseur)
    run_test("Get Fournisseurs", test_get_fournisseurs)
    run_test("Get Fournisseur by ID", test_get_fournisseur_by_id)
    run_test("Update Fournisseur", test_update_fournisseur)
    run_test("Search Fournisseurs", test_search_fournisseurs)
    
    # Article tests
    run_test("Create Article", test_create_article)
    run_test("Get Articles", test_get_articles)
    run_test("Get Articles with Low Stock", test_get_articles_stock_bas)
    run_test("Filter Articles", test_filter_articles)
    
    # Commande tests
    run_test("Create Commande", test_create_commande)
    run_test("Get Commandes", test_get_commandes)
    
    # Dashboard tests
    run_test("Dashboard Stats", test_dashboard_stats)
    
    # Alerte tests
    run_test("Create Alerte", test_create_alerte)
    run_test("Get Alertes", test_get_alertes)
    
    # Reporting tests
    run_test("Reporting Fournisseurs", test_reporting_fournisseurs)
    run_test("Reporting Articles", test_reporting_articles)
    run_test("Reporting Commandes", test_reporting_commandes)
    run_test("Reporting Synthese", test_reporting_synthese)
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"Total tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Skipped: {test_results['skipped']}")
    
    success_rate = test_results['passed'] / test_results['total'] * 100 if test_results['total'] > 0 else 0
    print(f"Success rate: {success_rate:.2f}%")
    
    if test_results['failed'] == 0:
        print_success("All tests passed successfully!")
    else:
        print_error(f"{test_results['failed']} tests failed.")

if __name__ == "__main__":
    run_all_tests()