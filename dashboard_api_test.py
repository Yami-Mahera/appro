import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_USER = {
    "email": "admin@test.com",
    "password": "admin123"
}

# Test results
test_results = {
    "dashboards_personnalises": {
        "get": {"success": False, "message": "Not tested"},
        "post": {"success": False, "message": "Not tested"},
        "put": {"success": False, "message": "Not tested"},
        "delete": {"success": False, "message": "Not tested"}
    },
    "widgets_disponibles": {
        "get": {"success": False, "message": "Not tested"}
    },
    "dashboard_stats": {
        "get": {"success": False, "message": "Not tested"}
    },
    "kpis": {
        "taux_service_client": {"success": False, "message": "Not tested"},
        "delai_moyen_livraison": {"success": False, "message": "Not tested"},
        "synthese": {"success": False, "message": "Not tested"}
    },
    "alertes": {
        "get_non_lues": {"success": False, "message": "Not tested"}
    }
}

# Created resources IDs
created_ids = {
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
    print_header("Logging in as admin")
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

# Test functions
def test_get_widgets_disponibles(token):
    print_header("Testing GET /api/dashboards/widgets-disponibles")
    success, message, data = make_request("get", "/dashboards/widgets-disponibles", token=token, expected_status=200)
    
    if success and data and "widgets" in data:
        print_test_result("Get widgets disponibles", True, f"Retrieved {len(data['widgets'])} widget types")
        test_results["widgets_disponibles"]["get"]["success"] = True
        test_results["widgets_disponibles"]["get"]["message"] = f"Successfully retrieved {len(data['widgets'])} widget types"
        return True
    else:
        print_test_result("Get widgets disponibles", False, message)
        test_results["widgets_disponibles"]["get"]["message"] = message
        return False

def test_get_dashboard_stats(token):
    print_header("Testing GET /api/dashboard/stats")
    success, message, data = make_request("get", "/dashboard/stats", token=token, expected_status=200)
    
    if success and data:
        print_test_result("Get dashboard stats", True, f"Retrieved dashboard stats with {len(data)} metrics")
        test_results["dashboard_stats"]["get"]["success"] = True
        test_results["dashboard_stats"]["get"]["message"] = f"Successfully retrieved dashboard stats with {len(data)} metrics"
        return True
    else:
        print_test_result("Get dashboard stats", False, message)
        test_results["dashboard_stats"]["get"]["message"] = message
        return False

def test_get_kpi_taux_service(token):
    print_header("Testing GET /api/kpis/taux-service-client")
    success, message, data = make_request("get", "/kpis/taux-service-client", token=token, expected_status=200)
    
    if success and data and "taux_service_client" in data:
        print_test_result("Get KPI taux service client", True, f"Retrieved taux service client: {data['taux_service_client']}")
        test_results["kpis"]["taux_service_client"]["success"] = True
        test_results["kpis"]["taux_service_client"]["message"] = f"Successfully retrieved taux service client: {data['taux_service_client']}"
        return True
    else:
        print_test_result("Get KPI taux service client", False, message)
        test_results["kpis"]["taux_service_client"]["message"] = message
        return False

def test_get_kpi_delai_moyen(token):
    print_header("Testing GET /api/kpis/delai-moyen-livraison")
    success, message, data = make_request("get", "/kpis/delai-moyen-livraison", token=token, expected_status=200)
    
    if success and data and "delai_moyen_livraison" in data:
        print_test_result("Get KPI délai moyen livraison", True, f"Retrieved délai moyen livraison: {data['delai_moyen_livraison']}")
        test_results["kpis"]["delai_moyen_livraison"]["success"] = True
        test_results["kpis"]["delai_moyen_livraison"]["message"] = f"Successfully retrieved délai moyen livraison: {data['delai_moyen_livraison']}"
        return True
    else:
        print_test_result("Get KPI délai moyen livraison", False, message)
        test_results["kpis"]["delai_moyen_livraison"]["message"] = message
        return False

def test_get_kpi_synthese(token):
    print_header("Testing GET /api/kpis/synthese")
    success, message, data = make_request("get", "/kpis/synthese", token=token, expected_status=200)
    
    if success and data:
        print_test_result("Get KPI synthèse", True, f"Retrieved KPI synthèse with {len(data)} metrics")
        test_results["kpis"]["synthese"]["success"] = True
        test_results["kpis"]["synthese"]["message"] = f"Successfully retrieved KPI synthèse with {len(data)} metrics"
        return True
    else:
        print_test_result("Get KPI synthèse", False, message)
        test_results["kpis"]["synthese"]["message"] = message
        return False

def test_get_alertes_non_lues(token):
    print_header("Testing GET /api/alertes?lue=false")
    success, message, data = make_request("get", "/alertes?lue=false", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get alertes non lues", True, f"Retrieved {len(data)} alertes non lues")
        test_results["alertes"]["get_non_lues"]["success"] = True
        test_results["alertes"]["get_non_lues"]["message"] = f"Successfully retrieved {len(data)} alertes non lues"
        return True
    else:
        print_test_result("Get alertes non lues", False, message)
        test_results["alertes"]["get_non_lues"]["message"] = message
        return False

def test_create_dashboard_personnalise(token):
    print_header("Testing POST /api/dashboards/personnalises")
    dashboard_data = {
        "nom": f"Dashboard Test {uuid.uuid4().hex[:6]}",
        "description": "Dashboard de test pour les tests API",
        "widgets": [
            {
                "id": str(uuid.uuid4()),
                "type": "kpi_card",
                "title": "Taux de service client",
                "config": {
                    "kpi_type": "taux_service_client",
                    "display_icon": True,
                    "display_trend": True
                },
                "position": {"x": 0, "y": 0, "w": 4, "h": 2}
            },
            {
                "id": str(uuid.uuid4()),
                "type": "chart_line",
                "title": "Évolution des commandes",
                "config": {
                    "data_type": "evolution_commandes",
                    "period": "month",
                    "limit": 12
                },
                "position": {"x": 4, "y": 0, "w": 8, "h": 4}
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
        print_test_result("Create dashboard personnalisé", True, f"Created dashboard: {data['nom']}")
        test_results["dashboards_personnalises"]["post"]["success"] = True
        test_results["dashboards_personnalises"]["post"]["message"] = f"Successfully created dashboard: {data['nom']}"
        created_ids["dashboard"] = data["id"]
        return data["id"]
    else:
        print_test_result("Create dashboard personnalisé", False, message)
        test_results["dashboards_personnalises"]["post"]["message"] = message
        return None

def test_get_dashboards_personnalises(token):
    print_header("Testing GET /api/dashboards/personnalises")
    success, message, data = make_request("get", "/dashboards/personnalises", token=token, expected_status=200)
    
    if success and isinstance(data, list):
        print_test_result("Get dashboards personnalisés", True, f"Retrieved {len(data)} dashboards")
        test_results["dashboards_personnalises"]["get"]["success"] = True
        test_results["dashboards_personnalises"]["get"]["message"] = f"Successfully retrieved {len(data)} dashboards"
        
        # If we don't have a dashboard ID yet but there are dashboards, use the first one
        if not created_ids["dashboard"] and data:
            created_ids["dashboard"] = data[0]["id"]
            print(f"Using existing dashboard with ID: {created_ids['dashboard']}")
        
        return True
    else:
        print_test_result("Get dashboards personnalisés", False, message)
        test_results["dashboards_personnalises"]["get"]["message"] = message
        return False

def test_update_dashboard_personnalise(token, dashboard_id):
    if not dashboard_id:
        print_test_result("Update dashboard personnalisé", False, "No dashboard ID available")
        test_results["dashboards_personnalises"]["put"]["message"] = "No dashboard ID available"
        return False
    
    print_header(f"Testing PUT /api/dashboards/personnalises/{dashboard_id}")
    update_data = {
        "nom": f"Dashboard Test Updated {uuid.uuid4().hex[:6]}",
        "description": "Dashboard de test mis à jour",
        "widgets": [
            {
                "id": str(uuid.uuid4()),
                "type": "kpi_card",
                "title": "Délai moyen de livraison",
                "config": {
                    "kpi_type": "delai_moyen_livraison",
                    "display_icon": True,
                    "display_trend": True
                },
                "position": {"x": 0, "y": 0, "w": 4, "h": 2}
            }
        ]
    }
    
    success, message, data = make_request("put", f"/dashboards/personnalises/{dashboard_id}", update_data, token=token, expected_status=200)
    
    if success and data and data["nom"] == update_data["nom"]:
        print_test_result("Update dashboard personnalisé", True, f"Updated dashboard: {data['nom']}")
        test_results["dashboards_personnalises"]["put"]["success"] = True
        test_results["dashboards_personnalises"]["put"]["message"] = f"Successfully updated dashboard: {data['nom']}"
        return True
    else:
        print_test_result("Update dashboard personnalisé", False, message)
        test_results["dashboards_personnalises"]["put"]["message"] = message
        return False

def test_delete_dashboard_personnalise(token, dashboard_id):
    if not dashboard_id:
        print_test_result("Delete dashboard personnalisé", False, "No dashboard ID available")
        test_results["dashboards_personnalises"]["delete"]["message"] = "No dashboard ID available"
        return False
    
    print_header(f"Testing DELETE /api/dashboards/personnalises/{dashboard_id}")
    success, message, data = make_request("delete", f"/dashboards/personnalises/{dashboard_id}", token=token, expected_status=200)
    
    if success:
        print_test_result("Delete dashboard personnalisé", True, "Dashboard deleted successfully")
        test_results["dashboards_personnalises"]["delete"]["success"] = True
        test_results["dashboards_personnalises"]["delete"]["message"] = "Successfully deleted dashboard"
        return True
    else:
        print_test_result("Delete dashboard personnalisé", False, message)
        test_results["dashboards_personnalises"]["delete"]["message"] = message
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

def run_tests():
    print_header("STARTING DASHBOARD API TESTS")
    
    # Login
    token = login()
    if not token:
        print("Authentication failed, cannot proceed with tests")
        return
    
    # Test widgets disponibles
    test_get_widgets_disponibles(token)
    
    # Test dashboard stats
    test_get_dashboard_stats(token)
    
    # Test KPIs
    test_get_kpi_taux_service(token)
    test_get_kpi_delai_moyen(token)
    test_get_kpi_synthese(token)
    
    # Test alertes
    test_get_alertes_non_lues(token)
    
    # Test dashboards personnalisés
    test_get_dashboards_personnalises(token)
    dashboard_id = test_create_dashboard_personnalise(token)
    if dashboard_id:
        test_update_dashboard_personnalise(token, dashboard_id)
        test_delete_dashboard_personnalise(token, dashboard_id)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    run_tests()