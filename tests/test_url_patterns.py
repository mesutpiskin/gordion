"""
Test Stash with different URL patterns
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
import requests

load_dotenv()

stash_url = os.getenv('STASH_URL').rstrip('/')
stash_username = os.getenv('STASH_USERNAME')
stash_password = os.getenv('STASH_PASSWORD')

session = requests.Session()
session.auth = (stash_username, stash_password)

print("=" * 70)
print("Testing Different URL Patterns for Stash")
print("=" * 70)
print()

# Try different base patterns
patterns = [
    ("", "Direct"),
    ("/git", "With /git"),
    ("/stash", "With /stash"),
    ("/scm", "With /scm"),
]

endpoints = [
    "/rest/api/1.0/projects",
    "/rest/api/1.0/application-properties",
    "/api/1.0/projects",
]

found_working = False

for prefix, prefix_name in patterns:
    print(f"Testing pattern: {prefix_name}")
    print(f"  Base: {stash_url}{prefix}")
    
    for endpoint in endpoints:
        url = f"{stash_url}{prefix}{endpoint}"
        
        try:
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"    ✅ {endpoint} - WORKS!")
                found_working = True
                
                # Show response
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        print(f"       Keys: {list(data.keys())[:5]}")
                except:
                    pass
                    
            elif response.status_code != 404:
                print(f"    ⚠️  {endpoint} - {response.status_code}")
                
        except Exception as e:
            pass
    
    print()

if not found_working:
    print("=" * 70)
    print("❌ No working pattern found")
    print()
    print("Please check:")
    print(f"  1. Can you access: {stash_url} in browser?")
    print(f"  2. Is the URL correct?")
    print(f"  3. Are you on VPN/network?")
    print()
    print("Try manually:")
    print(f"  curl -u {stash_username}:PASSWORD {stash_url}/rest/api/1.0/projects")
    print("=" * 70)
