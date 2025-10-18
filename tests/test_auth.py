"""
Quick test to check authentication method
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
import requests

load_dotenv()

stash_url = os.getenv('STASH_URL')
stash_username = os.getenv('STASH_USERNAME')
stash_password = os.getenv('STASH_PASSWORD')

if not all([stash_url, stash_username, stash_password]):
    print("❌ Missing environment variables!")
    print("Required: STASH_URL, STASH_USERNAME, STASH_PASSWORD")
    sys.exit(1)

base_url = stash_url.rstrip('/')
test_endpoint = "/rest/api/1.0/application-properties"

print("Testing authentication with Stash...")
print(f"URL: {base_url}")
print(f"Username: {stash_username}")
print()

# Test different auth methods (Basic Auth should work for older Stash)
auth_methods = [
    ("Basic Auth (username + password)", {}, (stash_username, stash_password)),
    ("Bearer Token (if PAT exists)", {'Authorization': f'Bearer {stash_password}'}),
    ("Token Only", {'Authorization': stash_password}),
]

for method_name, headers, *auth in auth_methods:
    print(f"Testing: {method_name}")
    
    try:
        url = base_url + test_endpoint
        
        if auth:
            response = requests.get(url, headers=headers, auth=auth[0], timeout=5)
        else:
            response = requests.get(url, headers=headers, timeout=5)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ SUCCESS!")
            try:
                data = response.json()
                print(f"  Response keys: {list(data.keys())[:5]}")
            except:
                print(f"  Response: {response.text[:100]}")
            print()
            print("=" * 60)
            print(f"✅ Working auth method: {method_name}")
            print("=" * 60)
            sys.exit(0)
        elif response.status_code == 401:
            print(f"  ❌ Unauthorized")
        elif response.status_code == 404:
            print(f"  ⚠️  Not found (but auth might be OK)")
        else:
            print(f"  ⚠️  Status: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")
    
    print()

print("=" * 60)
print("❌ No working authentication method found!")
print()
print("Please check:")
print("  1. STASH_TOKEN is valid")
print("  2. Token has correct permissions")
print("  3. Stash URL is correct")
print("=" * 60)
sys.exit(1)
