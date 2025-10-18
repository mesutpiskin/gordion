#!/usr/bin/env python3
"""
Test Ollama integration
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from ollama_agent import OllamaAgent

def main():
    print("=" * 70)
    print("Gordion AI Code Review Agent Test")
    print("=" * 70)
    print()
    
    # Load environment
    load_dotenv()
    
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    print(f"Ollama URL: {ollama_url}")
    print(f"Model: {ollama_model}")
    print()
    
    # Initialize agent
    print("Initializing Ollama agent...")
    agent = OllamaAgent(base_url=ollama_url, model=ollama_model)
    print()
    
    # Check connection
    print("Testing connection...")
    if not agent.check_connection():
        print()
        print("❌ Cannot connect to Ollama!")
        print()
        print("💡 Çözüm:")
        print("   1. Ollama'yı yükleyin: brew install ollama")
        print("   2. Servisi başlatın: ollama serve")
        print("   3. Veya kurulum scriptini çalıştırın: ./scripts/setup_ollama.sh")
        print()
        sys.exit(1)
    print()
    
    # Check model
    print("Checking model availability...")
    if not agent.check_model_available():
        print()
        print(f"❌ Model '{ollama_model}' bulunamadı!")
        print()
        print("💡 Çözüm:")
        print(f"   ollama pull {ollama_model}")
        print()
        print("Veya kurulum scriptini çalıştırın: ./scripts/setup_ollama.sh")
        print()
        sys.exit(1)
    print()
    
    print("=" * 70)
    print("Testing PR Analysis")
    print("=" * 70)
    print()
    
    # Mock PR data
    test_pr = {
        'id': 123,
        'title': 'Fix bug in user authentication',
        'description': 'This PR fixes a critical bug where users could not log in after password reset.',
        'author': {
            'name': 'John Doe',
            'email': 'john@example.com'
        },
        'changes': [
            {
                'path': 'src/auth/login.py',
                'additions': 15,
                'deletions': 5
            },
            {
                'path': 'tests/test_auth.py',
                'additions': 25,
                'deletions': 0
            }
        ]
    }
    
    print("Test PR:")
    print(f"  Title: {test_pr['title']}")
    print(f"  Author: {test_pr['author']['name']}")
    print(f"  Files: {len(test_pr['changes'])}")
    print()
    
    print("⏳ Analyzing with Ollama AI...")
    print("   (This may take 10-30 seconds depending on model size)")
    print()
    
    try:
        result = agent.analyze_pull_request(test_pr)
        
        if result:
            print("=" * 70)
            print("✅ Analysis Successful!")
            print("=" * 70)
            print()
            print(f"Approve: {result.get('approve')}")
            print(f"Confidence: {result.get('confidence_score')}%")
            print()
            print("Reasoning:")
            print(f"  {result.get('reasoning')}")
            print()
            
            concerns = result.get('concerns', [])
            if concerns:
                print("Concerns:")
                for concern in concerns:
                    print(f"  • {concern}")
                print()
            
            print("=" * 70)
            print("Approval Comment:")
            print("=" * 70)
            print()
            comment = agent.get_approval_comment(result)
            print(comment)
            print()
            
            print("=" * 70)
            print("✅ Test Passed!")
            print("=" * 70)
            print()
            print("🚀 Ollama is ready to use!")
            print()
        else:
            print("❌ Analysis failed - returned None")
            print()
            print("This might be due to:")
            print("  • Model response timeout")
            print("  • Invalid JSON response")
            print("  • Model not properly loaded")
            print()
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
