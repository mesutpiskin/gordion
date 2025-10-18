"""
Stash API Explorer - Test different endpoints to find the correct one
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_api_endpoints():
    """Test various Stash API endpoints"""
    load_dotenv()
    
    stash_url = os.getenv('STASH_URL')
    stash_username = os.getenv('STASH_USERNAME')
    stash_token = os.getenv('STASH_TOKEN')
    
    if not all([stash_url, stash_username, stash_token]):
        logger.error("Missing required environment variables!")
        return False
    
    base_url = stash_url.rstrip('/')
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {stash_token}',
        'Content-Type': 'application/json'
    })
    
    logger.info(f"Testing Stash API: {base_url}")
    logger.info(f"Username: {stash_username}")
    logger.info("")
    
    # Test endpoints
    endpoints = [
        # User info
        ("/rest/api/1.0/users/" + stash_username, {}, "User Info"),
        
        # Dashboard endpoints
        ("/rest/api/1.0/dashboard/pull-requests", {'role': 'REVIEWER', 'state': 'OPEN'}, "Dashboard PRs"),
        ("/rest/api/1.0/inbox/pull-requests", {'state': 'OPEN'}, "Inbox PRs"),
        
        # Projects
        ("/rest/api/1.0/projects", {'limit': 5}, "Projects List"),
        
        # User's PRs (alternative methods)
        ("/rest/api/1.0/users/" + stash_username + "/repos", {'limit': 10}, "User Repos"),
        
        # Profile/Activity
        ("/rest/api/1.0/profile/recent/repos", {'limit': 10}, "Recent Repos"),
    ]
    
    results = []
    
    for endpoint, params, description in endpoints:
        url = base_url + endpoint
        logger.info(f"Testing: {description}")
        logger.info(f"  URL: {endpoint}")
        
        try:
            response = session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"  ✅ SUCCESS (200)")
                try:
                    data = response.json()
                    if 'values' in data:
                        logger.info(f"     Found {len(data.get('values', []))} items")
                    elif isinstance(data, dict):
                        logger.info(f"     Response keys: {list(data.keys())[:5]}")
                    results.append((description, endpoint, True, None))
                except:
                    logger.info(f"     Response: {response.text[:100]}")
                    results.append((description, endpoint, True, None))
            elif response.status_code == 404:
                logger.warning(f"  ❌ NOT FOUND (404)")
                results.append((description, endpoint, False, "404"))
            elif response.status_code == 401:
                logger.warning(f"  🔐 UNAUTHORIZED (401) - Check token!")
                results.append((description, endpoint, False, "401"))
            elif response.status_code == 403:
                logger.warning(f"  🚫 FORBIDDEN (403) - Insufficient permissions")
                results.append((description, endpoint, False, "403"))
            else:
                logger.warning(f"  ⚠️  Status: {response.status_code}")
                results.append((description, endpoint, False, str(response.status_code)))
                
        except Exception as e:
            logger.error(f"  ❌ ERROR: {str(e)[:100]}")
            results.append((description, endpoint, False, str(e)[:50]))
        
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    
    working_endpoints = [r for r in results if r[2]]
    if working_endpoints:
        logger.info(f"\n✅ Working endpoints ({len(working_endpoints)}):")
        for desc, endpoint, _, _ in working_endpoints:
            logger.info(f"  • {desc}: {endpoint}")
    
    failed_endpoints = [r for r in results if not r[2]]
    if failed_endpoints:
        logger.info(f"\n❌ Failed endpoints ({len(failed_endpoints)}):")
        for desc, endpoint, _, error in failed_endpoints:
            logger.info(f"  • {desc}: {endpoint} ({error})")
    
    logger.info("")
    logger.info("=" * 60)
    
    if working_endpoints:
        logger.info("\n💡 Suggestion:")
        logger.info("Update src/stash_client.py to use the working endpoints above.")
    else:
        logger.error("\n⚠️  No working endpoints found!")
        logger.error("Possible issues:")
        logger.error("  1. Check if STASH_TOKEN is valid")
        logger.error("  2. Token might need different format (try without 'Bearer ')")
        logger.error("  3. Token might not have required permissions")
        logger.error("  4. API URL might be different (check Stash version)")
    
    return len(working_endpoints) > 0


if __name__ == '__main__':
    print("=" * 60)
    print("Stash API Explorer")
    print("=" * 60)
    print()
    
    # Fix token variable name
    load_dotenv()
    token = os.getenv('STASH_TOKEN')
    
    success = test_api_endpoints()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Found working API endpoints!")
    else:
        print("❌ No working endpoints found")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
