# test_api.py
import requests
import json

url = "http://localhost:5000/analyze"

test_code = """
def login_user():
    password = "admin123"  # Hardcoded password
    query = "SELECT * FROM users WHERE name='" + username + "'"  # SQL injection
    eval(user_input)  # Dangerous eval usage
    print(user_email)  # Potential PII exposure
"""

response = requests.post(url, json={'code': test_code})
print(json.dumps(response.json(), indent=2))