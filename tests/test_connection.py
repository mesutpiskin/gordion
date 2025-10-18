"""
Test script to verify Stash connection and configuration
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from stash_client import StashClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """Test Stash connection"""
    load_dotenv()
    
    stash_url = os.getenv('STASH_URL')
    stash_token = os.getenv('STASH_TOKEN')
    stash_username = os.getenv('STASH_USERNAME')
    stash_password = os.getenv('STASH_PASSWORD')
    
    if not stash_url:
        logger.error("Missing STASH_URL in .env file")
        return False
    
    logger.info(f"Testing connection to: {stash_url}")
    
    # Check authentication method
    if stash_token:
        logger.info("Using Personal Access Token authentication")
        if stash_username:
            logger.info(f"Username: {stash_username}")
        client = StashClient(stash_url, token=stash_token, username=stash_username)
    elif stash_username and stash_password:
        logger.info(f"Username: {stash_username}")
        logger.info("Using Basic Authentication (username + password)")
        client = StashClient(stash_url, username=stash_username, password=stash_password)
    else:
        logger.error("Missing authentication credentials!")
        logger.error("Please provide either:")
        logger.error("  - STASH_TOKEN (Personal Access Token)")
        logger.error("  - STASH_USERNAME + STASH_PASSWORD (Basic Auth)")
        return False
    
    try:
        # Try to fetch PRs
        logger.info("Fetching assigned pull requests...")
        prs = client.get_assigned_pull_requests()
        
        logger.info(f"✅ Success! Found {len(prs)} assigned PR(s)")
        
        if prs:
            logger.info("\nPull Requests:")
            for pr in prs[:5]:  # Show first 5
                logger.info(f"  - PR #{pr.get('id')}: {pr.get('title', 'No title')}")
                logger.info(f"    Author: {pr.get('author', {}).get('user', {}).get('displayName', 'Unknown')}")
                logger.info(f"    State: {pr.get('state')}")
                logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Stash Connection Test")
    print("=" * 60)
    print()
    
    success = test_connection()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Connection test passed!")
    else:
        print("❌ Connection test failed!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
