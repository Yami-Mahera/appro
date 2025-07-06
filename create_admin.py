import requests
import json

# Configuration
BASE_URL = "http://localhost:8001/api"

# Create admin user
admin_data = {
    "email": "admin@test.com",
    "password": "admin123",
    "nom": "Admin",
    "prenom": "Test",
    "role": "administrateur"
}

# Register the user
response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
print(f"Register response: {response.status_code}")
print(response.json() if response.text else "No response body")

# Try to login
login_data = {
    "email": admin_data["email"],
    "password": admin_data["password"]
}

response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Login response: {response.status_code}")
print(response.json() if response.text else "No response body")