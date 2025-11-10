import requests

print("Testing Epieos API...")
r = requests.get('https://api.epieos.com/email-finder?name=john+doe', timeout=5)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")
