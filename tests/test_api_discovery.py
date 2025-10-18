"""
Simple Stash API Discovery - Find working endpoints
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
    sys.exit(1)

base_url = stash_url.rstrip('/')
session = requests.Session()
session.auth = (stash_username, stash_password)

print("=" * 70)
print("Stash API Endpoint Discovery")
print("=" * 70)
print(f"URL: {base_url}")
print(f"User: {stash_username}")
print()

# Common Stash/Bitbucket Server endpoints
endpoints = [
    # Root/Info
    ("/rest/api/1.0/", "API Root"),
    ("/rest/api/1.0/application-properties", "Application Properties"),
    
    # User/Profile
    (f"/rest/api/1.0/users/{stash_username}", "User Profile"),
    ("/rest/api/1.0/profile/recent/repos", "Recent Repos"),
    
    # Projects
    ("/rest/api/1.0/projects", "Projects List"),
    
    # Pull Requests - Various methods
    ("/rest/api/1.0/inbox/pull-requests", "Inbox PRs"),
    ("/rest/api/1.0/dashboard/pull-requests", "Dashboard PRs"),
    
    # Legacy/Alternative endpoints
    ("/rest/api/latest/application-properties", "API Latest - App Properties"),
    ("/rest/api/latest/projects", "API Latest - Projects"),
    (f"/rest/api/latest/users/{stash_username}", "API Latest - User"),
]

working = []
failed = []

for endpoint, name in endpoints:
    url = base_url + endpoint
    
    try:
        print(f"Testing: {name}")
        print(f"  {endpoint}")
        
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✅ 200 OK")
            working.append((endpoint, name, response))
        elif response.status_code == 401:
            print(f"  🔐 401 Unauthorized - Check credentials!")
        elif response.status_code == 404:
            print(f"  ❌ 404 Not Found")
            failed.append((endpoint, name))
        else:
            print(f"  ⚠️  {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")
        failed.append((endpoint, name))
    
    print()

print("=" * 70)
print("RESULTS")
print("=" * 70)
print()

if working:
    print(f"✅ Working Endpoints ({len(working)}):")
    print()
    for endpoint, name, response in working:
        print(f"  • {name}")
        print(f"    {endpoint}")
        
        try:
            data = response.json()
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                print(f"    Keys: {keys}")
            elif isinstance(data, list):
                print(f"    List with {len(data)} items")
        except:
            print(f"    Response length: {len(response.text)}")
        print()
else:
    print("❌ No working endpoints found!")
    print()
    print("Possible issues:")
    print("  1. Wrong credentials")
    print("  2. Different Stash API version")
    print("  3. Network/firewall issue")
    print()

# If we found projects endpoint, try to get PRs from there
if any(endpoint == "/rest/api/1.0/projects" for endpoint, _, _ in working):
    print("=" * 70)
    print("Trying to find PRs via Projects...")
    print("=" * 70)
    print()
    
    try:
        # Get first project
        response = session.get(base_url + "/rest/api/1.0/projects", params={'limit': 5}, timeout=10)
        data = response.json()
        projects = data.get('values', [])
        
        if projects:
            project = projects[0]
            project_key = project.get('key')
            print(f"Testing project: {project_key}")
            
            # Get repos
            repos_url = f"/rest/api/1.0/projects/{project_key}/repos"
            response = session.get(base_url + repos_url, params={'limit': 5}, timeout=10)
            repos_data = response.json()
            repos = repos_data.get('values', [])
            
            if repos:
                repo = repos[0]
                repo_slug = repo.get('slug')
                print(f"  Testing repo: {repo_slug}")
                
                # Get PRs
                prs_url = f"/rest/api/1.0/projects/{project_key}/repos/{repo_slug}/pull-requests"
                response = session.get(base_url + prs_url, params={'state': 'OPEN'}, timeout=10)
                
                if response.status_code == 200:
                    prs_data = response.json()
                    prs = prs_data.get('values', [])
                    print(f"    ✅ Found {len(prs)} PRs")
                    print()
                    print(f"  Correct endpoint pattern:")
                    print(f"    /rest/api/1.0/projects/{{project}}/repos/{{repo}}/pull-requests")
                else:
                    print(f"    ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

print()
print("=" * 70)
