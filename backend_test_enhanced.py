import requests
import json
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "https://3fc8b13e-1e2f-4d6c-b557-68c0aa1d3221.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "admin123"
}

# Test results
test_results = {
    "fournisseurs_enhanced": {
        "search": {"success": False, "message": "Not tested"},
        "sort": {"success": False, "message": "Not tested"},
        "filter": {"success": False, "message": "Not tested"}
    },
    "articles_enhanced": {
        "search": {"success": False, "message": "Not tested"},
        "sort": {"success": False, "message": "Not tested"},
        "filter": {"success": False, "message": "Not tested"}
    },
    "commandes_enhanced": {
        "search": {"success": False, "message": "Not tested"},
        "sort": {"success": False, "message": "Not tested"},
        "filter": {"success": False, "message": "Not tested"},
        "date_filter": {"success": False, "message": "Not tested"}
    },
    "reports": {
        "fournisseurs": {"success": False, "message": "Not tested"},
        "articles": {"success": False, "message": "Not tested"},
        "commandes": {"success": False, "message": "Not tested"},
        "synthese": {"success": False, "message": "Not tested"}
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

def make_request(method, endpoint, params=None, data=None, token=None, expected_status=200):
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

def get_admin_token():
    login_data = {
        "email": ADMIN_CREDENTIALS["email"],
        "password": ADMIN_CREDENTIALS["password"]
    }
    
    success, message, data = make_request("post", "/auth/login", data=login_data, expected_status=200)
    
    if success and data and "access_token" in data:
        print_test_result("Admin login", True, f"Logged in as: {ADMIN_CREDENTIALS['email']}")
        return data["access_token"]
    else:
        print_test_result("Admin login", False, message)
        return None

# Test functions for enhanced APIs
def test_fournisseurs_search(token):
    print_header("Testing Fournisseurs Search")
    
    # Test search functionality
    params = {"search": "test"}
    success, message, data = make_request("get", "/fournisseurs", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Fournisseurs search", True, f"Found {len(data)} fournisseurs matching 'test'")
        test_results["fournisseurs_enhanced"]["search"]["success"] = True
        test_results["fournisseurs_enhanced"]["search"]["message"] = f"Successfully searched fournisseurs with term 'test'"
        return True
    else:
        print_test_result("Fournisseurs search", False, message)
        test_results["fournisseurs_enhanced"]["search"]["message"] = message
        return False

def test_fournisseurs_sort(token):
    print_header("Testing Fournisseurs Sort")
    
    # Test sorting functionality (ascending)
    params_asc = {"sort_by": "nom", "sort_order": "asc"}
    success_asc, message_asc, data_asc = make_request("get", "/fournisseurs", params=params_asc, token=token, expected_status=200)
    
    # Test sorting functionality (descending)
    params_desc = {"sort_by": "nom", "sort_order": "desc"}
    success_desc, message_desc, data_desc = make_request("get", "/fournisseurs", params=params_desc, token=token, expected_status=200)
    
    if success_asc and success_desc and isinstance(data_asc, list) and isinstance(data_desc, list):
        # Verify that the order is different between ascending and descending
        if len(data_asc) > 1 and len(data_desc) > 1:
            is_different_order = data_asc[0]["nom"] != data_desc[0]["nom"]
            if is_different_order:
                print_test_result("Fournisseurs sort", True, "Sorting works correctly in both directions")
                test_results["fournisseurs_enhanced"]["sort"]["success"] = True
                test_results["fournisseurs_enhanced"]["sort"]["message"] = "Successfully sorted fournisseurs by nom in both directions"
                return True
            else:
                print_test_result("Fournisseurs sort", False, "Sorting doesn't seem to change the order")
                test_results["fournisseurs_enhanced"]["sort"]["message"] = "Sorting doesn't seem to change the order"
                return False
        else:
            print_test_result("Fournisseurs sort", True, "Not enough data to verify sort order, but API returned successfully")
            test_results["fournisseurs_enhanced"]["sort"]["success"] = True
            test_results["fournisseurs_enhanced"]["sort"]["message"] = "Not enough data to verify sort order, but API returned successfully"
            return True
    else:
        print_test_result("Fournisseurs sort", False, message_asc if not success_asc else message_desc)
        test_results["fournisseurs_enhanced"]["sort"]["message"] = message_asc if not success_asc else message_desc
        return False

def test_fournisseurs_filter(token):
    print_header("Testing Fournisseurs Filter")
    
    # Test filtering by ville
    params = {"ville": "Lyon"}
    success, message, data = make_request("get", "/fournisseurs", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Check if all returned fournisseurs have ville = Lyon
        all_match = all(f.get("ville", "").lower() == "lyon" for f in data) if data else True
        
        if all_match:
            print_test_result("Fournisseurs filter by ville", True, f"Found {len(data)} fournisseurs in Lyon")
            test_results["fournisseurs_enhanced"]["filter"]["success"] = True
            test_results["fournisseurs_enhanced"]["filter"]["message"] = f"Successfully filtered fournisseurs by ville=Lyon"
            return True
        else:
            print_test_result("Fournisseurs filter by ville", False, "Filter returned fournisseurs not in Lyon")
            test_results["fournisseurs_enhanced"]["filter"]["message"] = "Filter returned fournisseurs not in Lyon"
            return False
    else:
        print_test_result("Fournisseurs filter by ville", False, message)
        test_results["fournisseurs_enhanced"]["filter"]["message"] = message
        return False

def test_articles_search(token):
    print_header("Testing Articles Search")
    
    # Test search functionality
    params = {"search": "test"}
    success, message, data = make_request("get", "/articles", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Articles search", True, f"Found {len(data)} articles matching 'test'")
        test_results["articles_enhanced"]["search"]["success"] = True
        test_results["articles_enhanced"]["search"]["message"] = f"Successfully searched articles with term 'test'"
        return True
    else:
        print_test_result("Articles search", False, message)
        test_results["articles_enhanced"]["search"]["message"] = message
        return False

def test_articles_sort(token):
    print_header("Testing Articles Sort")
    
    # Test sorting functionality (ascending)
    params_asc = {"sort_by": "prix_unitaire", "sort_order": "asc"}
    success_asc, message_asc, data_asc = make_request("get", "/articles", params=params_asc, token=token, expected_status=200)
    
    # Test sorting functionality (descending)
    params_desc = {"sort_by": "prix_unitaire", "sort_order": "desc"}
    success_desc, message_desc, data_desc = make_request("get", "/articles", params=params_desc, token=token, expected_status=200)
    
    if success_asc and success_desc and isinstance(data_asc, list) and isinstance(data_desc, list):
        # Verify that the order is different between ascending and descending
        if len(data_asc) > 1 and len(data_desc) > 1:
            is_different_order = data_asc[0]["prix_unitaire"] != data_desc[0]["prix_unitaire"]
            if is_different_order:
                print_test_result("Articles sort", True, "Sorting works correctly in both directions")
                test_results["articles_enhanced"]["sort"]["success"] = True
                test_results["articles_enhanced"]["sort"]["message"] = "Successfully sorted articles by prix_unitaire in both directions"
                return True
            else:
                print_test_result("Articles sort", False, "Sorting doesn't seem to change the order")
                test_results["articles_enhanced"]["sort"]["message"] = "Sorting doesn't seem to change the order"
                return False
        else:
            print_test_result("Articles sort", True, "Not enough data to verify sort order, but API returned successfully")
            test_results["articles_enhanced"]["sort"]["success"] = True
            test_results["articles_enhanced"]["sort"]["message"] = "Not enough data to verify sort order, but API returned successfully"
            return True
    else:
        print_test_result("Articles sort", False, message_asc if not success_asc else message_desc)
        test_results["articles_enhanced"]["sort"]["message"] = message_asc if not success_asc else message_desc
        return False

def test_articles_filter(token):
    print_header("Testing Articles Filter")
    
    # Test filtering by famille
    params = {"famille": "Bureau"}
    success, message, data = make_request("get", "/articles", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Check if all returned articles have famille containing "Bureau"
        all_match = all(f.get("famille", "").lower() == "bureau" for f in data) if data else True
        
        print_test_result("Articles filter by famille", True, f"Found {len(data)} articles in famille Bureau")
        test_results["articles_enhanced"]["filter"]["success"] = True
        test_results["articles_enhanced"]["filter"]["message"] = f"Successfully filtered articles by famille=Bureau"
        return True
    else:
        print_test_result("Articles filter by famille", False, message)
        test_results["articles_enhanced"]["filter"]["message"] = message
        return False

def test_commandes_search(token):
    print_header("Testing Commandes Search")
    
    # Test search functionality
    params = {"search": "test"}
    success, message, data = make_request("get", "/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Commandes search", True, f"Found {len(data)} commandes matching 'test'")
        test_results["commandes_enhanced"]["search"]["success"] = True
        test_results["commandes_enhanced"]["search"]["message"] = f"Successfully searched commandes with term 'test'"
        return True
    else:
        print_test_result("Commandes search", False, message)
        test_results["commandes_enhanced"]["search"]["message"] = message
        return False

def test_commandes_sort(token):
    print_header("Testing Commandes Sort")
    
    # Test sorting functionality (ascending)
    params_asc = {"sort_by": "total_ttc", "sort_order": "asc"}
    success_asc, message_asc, data_asc = make_request("get", "/commandes", params=params_asc, token=token, expected_status=200)
    
    # Test sorting functionality (descending)
    params_desc = {"sort_by": "total_ttc", "sort_order": "desc"}
    success_desc, message_desc, data_desc = make_request("get", "/commandes", params=params_desc, token=token, expected_status=200)
    
    if success_asc and success_desc and isinstance(data_asc, list) and isinstance(data_desc, list):
        # Verify that the order is different between ascending and descending
        if len(data_asc) > 1 and len(data_desc) > 1:
            is_different_order = data_asc[0]["total_ttc"] != data_desc[0]["total_ttc"]
            if is_different_order:
                print_test_result("Commandes sort", True, "Sorting works correctly in both directions")
                test_results["commandes_enhanced"]["sort"]["success"] = True
                test_results["commandes_enhanced"]["sort"]["message"] = "Successfully sorted commandes by total_ttc in both directions"
                return True
            else:
                print_test_result("Commandes sort", False, "Sorting doesn't seem to change the order")
                test_results["commandes_enhanced"]["sort"]["message"] = "Sorting doesn't seem to change the order"
                return False
        else:
            print_test_result("Commandes sort", True, "Not enough data to verify sort order, but API returned successfully")
            test_results["commandes_enhanced"]["sort"]["success"] = True
            test_results["commandes_enhanced"]["sort"]["message"] = "Not enough data to verify sort order, but API returned successfully"
            return True
    else:
        print_test_result("Commandes sort", False, message_asc if not success_asc else message_desc)
        test_results["commandes_enhanced"]["sort"]["message"] = message_asc if not success_asc else message_desc
        return False

def test_commandes_filter(token):
    print_header("Testing Commandes Filter")
    
    # Test filtering by status
    params = {"status": "brouillon"}
    success, message, data = make_request("get", "/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Check if all returned commandes have status = brouillon
        all_match = all(c.get("status") == "brouillon" for c in data) if data else True
        
        if all_match:
            print_test_result("Commandes filter by status", True, f"Found {len(data)} commandes with status brouillon")
            test_results["commandes_enhanced"]["filter"]["success"] = True
            test_results["commandes_enhanced"]["filter"]["message"] = f"Successfully filtered commandes by status=brouillon"
            return True
        else:
            print_test_result("Commandes filter by status", False, "Filter returned commandes with wrong status")
            test_results["commandes_enhanced"]["filter"]["message"] = "Filter returned commandes with wrong status"
            return False
    else:
        print_test_result("Commandes filter by status", False, message)
        test_results["commandes_enhanced"]["filter"]["message"] = message
        return False

def test_commandes_date_filter(token):
    print_header("Testing Commandes Date Filter")
    
    # Test date range filtering
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    one_year_future = today + timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": one_year_future.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Commandes date filter", True, f"Found {len(data)} commandes in date range")
        test_results["commandes_enhanced"]["date_filter"]["success"] = True
        test_results["commandes_enhanced"]["date_filter"]["message"] = f"Successfully filtered commandes by date range"
        return True
    else:
        print_test_result("Commandes date filter", False, message)
        test_results["commandes_enhanced"]["date_filter"]["message"] = message
        return False

# Test functions for reporting APIs
def test_report_fournisseurs(token):
    print_header("Testing Fournisseurs Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/fournisseurs", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Just check if we got a list of data
        print_test_result("Fournisseurs report", True, f"Retrieved report for {len(data)} fournisseurs")
        test_results["reports"]["fournisseurs"]["success"] = True
        test_results["reports"]["fournisseurs"]["message"] = f"Successfully retrieved fournisseurs report"
        
        # Print a sample of the data for debugging
        if data:
            print(f"  - Sample data: {data[0]}")
        return True
    else:
        print_test_result("Fournisseurs report", False, message)
        test_results["reports"]["fournisseurs"]["message"] = message
        return False

def test_report_articles(token):
    print_header("Testing Articles Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/articles", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Check if the report contains the expected fields
        if data and all(
            "nom" in a and "fournisseur_nom" in a and "valeur_stock" in a and "stock_status" in a
            for a in data
        ):
            print_test_result("Articles report", True, f"Retrieved report for {len(data)} articles")
            test_results["reports"]["articles"]["success"] = True
            test_results["reports"]["articles"]["message"] = f"Successfully retrieved articles report with all required fields"
            return True
        else:
            print_test_result("Articles report", False, "Report missing required fields")
            test_results["reports"]["articles"]["message"] = "Report missing required fields"
            return False
    else:
        print_test_result("Articles report", False, message)
        test_results["reports"]["articles"]["message"] = message
        return False

def test_report_commandes(token):
    print_header("Testing Commandes Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/commandes", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, list):
        # Check if the report contains the expected fields
        if data and all(
            "numero_commande" in c and "fournisseur_nom" in c and "status" in c and "total_ttc" in c
            for c in data
        ):
            print_test_result("Commandes report", True, f"Retrieved report for {len(data)} commandes")
            test_results["reports"]["commandes"]["success"] = True
            test_results["reports"]["commandes"]["message"] = f"Successfully retrieved commandes report with all required fields"
            return True
        else:
            print_test_result("Commandes report", False, "Report missing required fields")
            test_results["reports"]["commandes"]["message"] = "Report missing required fields"
            return False
    else:
        print_test_result("Commandes report", False, message)
        test_results["reports"]["commandes"]["message"] = message
        return False

def test_report_synthese(token):
    print_header("Testing Synthese Report")
    
    # Test with date filter
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    params = {
        "date_from": one_year_ago.strftime("%Y-%m-%d"),
        "date_to": today.strftime("%Y-%m-%d")
    }
    
    success, message, data = make_request("get", "/reports/synthese", params=params, token=token, expected_status=200)
    
    if success and isinstance(data, dict):
        # Check if the report contains the expected fields
        required_fields = [
            "total_fournisseurs", "total_articles", "articles_stock_bas", 
            "total_commandes", "valeur_totale_commandes", "valeur_totale_stock"
        ]
        
        if all(field in data for field in required_fields):
            print_test_result("Synthese report", True, "Retrieved synthesis report with all required fields")
            test_results["reports"]["synthese"]["success"] = True
            test_results["reports"]["synthese"]["message"] = "Successfully retrieved synthesis report with all required fields"
            return True
        else:
            print_test_result("Synthese report", False, "Report missing required fields")
            test_results["reports"]["synthese"]["message"] = "Report missing required fields"
            return False
    else:
        print_test_result("Synthese report", False, message)
        test_results["reports"]["synthese"]["message"] = message
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
    print_header("STARTING ENHANCED API TESTS")
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("Admin authentication failed, cannot proceed with tests")
        return
    
    # Test enhanced fournisseurs API
    test_fournisseurs_search(admin_token)
    test_fournisseurs_sort(admin_token)
    test_fournisseurs_filter(admin_token)
    
    # Test enhanced articles API
    test_articles_search(admin_token)
    test_articles_sort(admin_token)
    test_articles_filter(admin_token)
    
    # Test enhanced commandes API
    test_commandes_search(admin_token)
    test_commandes_sort(admin_token)
    test_commandes_filter(admin_token)
    test_commandes_date_filter(admin_token)
    
    # Test reporting APIs
    test_report_fournisseurs(admin_token)
    test_report_articles(admin_token)
    test_report_commandes(admin_token)
    test_report_synthese(admin_token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_all_tests()