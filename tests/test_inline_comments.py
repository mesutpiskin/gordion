#!/usr/bin/env python3
"""
Test inline comment functionality
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from logger import setup_logger
from stash_client import StashClient
from ollama_agent import OllamaAgent

# Load environment
load_dotenv()
logger = setup_logger(log_level='DEBUG')


def test_inline_comments():
    """Test adding inline comments to a PR"""
    
    # Get credentials
    stash_url = os.getenv('STASH_URL')
    stash_token = os.getenv('STASH_TOKEN')
    stash_username = os.getenv('STASH_USERNAME')
    stash_password = os.getenv('STASH_PASSWORD')
    
    if not stash_url:
        print("❌ STASH_URL not found in .env")
        return
    
    # Initialize Stash client
    if stash_token:
        logger.info("Using Personal Access Token authentication")
        client = StashClient(stash_url, token=stash_token, username=stash_username)
    elif stash_username and stash_password:
        logger.info("Using Basic Authentication")
        client = StashClient(stash_url, username=stash_username, password=stash_password)
    else:
        print("❌ No authentication credentials found")
        return
    
    # Initialize Ollama agent
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    agent = OllamaAgent(base_url=ollama_url, model=ollama_model)
    
    # Check Ollama
    if not agent.check_connection():
        print("❌ Cannot connect to Ollama")
        return
    
    if not agent.check_model_available():
        print(f"❌ Model '{ollama_model}' not available")
        return
    
    print(f"✅ Connected to Ollama with model: {ollama_model}")
    
    # Get first PR
    print("\nFetching assigned PRs...")
    prs = client.get_assigned_pull_requests()
    
    if not prs:
        print("❌ No assigned PRs found")
        return
    
    pr = prs[0]
    pr_id = pr.get('id')
    
    # Extract identifiers
    from pr_analyzer import PRAnalyzer
    analyzer = PRAnalyzer({})
    identifiers = analyzer.extract_pr_identifiers(pr)
    
    if not identifiers:
        print("❌ Could not extract PR identifiers")
        return
    
    project_key, repo_slug, pr_id = identifiers
    
    print(f"\n📋 Testing with PR #{pr_id}: {pr.get('title')}")
    print(f"   Repository: {project_key}/{repo_slug}")
    
    # Get changes
    print("\nFetching PR changes...")
    changes = client.get_pull_request_changes(project_key, repo_slug, pr_id)
    
    if not changes:
        print("❌ No changes found")
        return
    
    print(f"✅ Found {len(changes)} file change(s)")
    
    # Test inline comment analysis
    for i, file_change in enumerate(changes[:3], 1):  # Test first 3 files
        file_path = file_change.get('path', 'unknown')
        hunks = file_change.get('hunks', [])
        
        if not hunks:
            continue
        
        print(f"\n{i}. Analyzing: {file_path}")
        
        # Get AI suggestions
        file_analysis = agent.analyze_file_changes(file_path, hunks)
        
        if not file_analysis or not file_analysis.get('comments'):
            print(f"   ℹ️  No suggestions for this file")
            continue
        
        suggestions = file_analysis['comments']
        print(f"   ✅ Generated {len(suggestions)} suggestion(s):")
        
        for suggestion in suggestions:
            line_num = suggestion.get('line', 0)
            comment_text = suggestion.get('comment', '')
            severity = suggestion.get('severity', 'info')
            
            severity_emoji = {
                'critical': '🔴',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(severity, 'ℹ️')
            
            print(f"\n   {severity_emoji} Line {line_num} ({severity}):")
            print(f"      {comment_text[:100]}...")
            
            # Ask if should add comment
            response = input(f"\n   Add this inline comment? (y/N): ").strip().lower()
            
            if response == 'y':
                formatted_comment = f"{severity_emoji} **Gordion AI Review**\n\n{comment_text}"
                
                if client.add_inline_comment(
                    project_key, repo_slug, pr_id,
                    file_path, line_num, formatted_comment
                ):
                    print(f"   ✅ Added inline comment to {file_path}:{line_num}")
                else:
                    print(f"   ❌ Failed to add inline comment")
    
    print("\n✅ Test completed!")


if __name__ == '__main__':
    try:
        test_inline_comments()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
