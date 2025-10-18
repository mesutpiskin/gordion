"""
Test script to verify AI agent functionality
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv
from ai_agent import AIAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ai_agent():
    """Test AI agent"""
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        logger.error("Missing OPENAI_API_KEY in .env file")
        return False
    
    logger.info("Initializing AI agent...")
    
    try:
        agent = AIAgent(api_key=api_key, model="gpt-4")
        
        # Create a sample PR for testing
        sample_pr = {
            'id': 123,
            'title': 'Add new feature: user authentication',
            'description': 'This PR adds basic user authentication with JWT tokens',
            'author': {'user': {'displayName': 'Test User'}},
            'changes': [
                {'path': {'toString': 'src/auth/login.js'}, 'type': 'ADD'},
                {'path': {'toString': 'src/auth/token.js'}, 'type': 'ADD'},
                {'path': {'toString': 'tests/auth.test.js'}, 'type': 'ADD'},
            ],
            'diff': '''
--- /dev/null
+++ src/auth/login.js
@@ -0,0 +1,10 @@
+function login(username, password) {
+    // Authenticate user
+    if (validateCredentials(username, password)) {
+        return generateToken(username);
+    }
+    return null;
+}
+
+module.exports = { login };
''',
            'activities': []
        }
        
        logger.info("Testing AI analysis with sample PR...")
        analysis = agent.analyze_pull_request(sample_pr)
        
        if analysis:
            logger.info("✅ AI Analysis successful!")
            logger.info(f"   Approve: {analysis.get('approve')}")
            logger.info(f"   Confidence: {analysis.get('confidence_score')}%")
            logger.info(f"   Reasoning: {analysis.get('reasoning')}")
            
            if analysis.get('concerns'):
                logger.info(f"   Concerns: {analysis.get('concerns')}")
            
            return True
        else:
            logger.error("❌ AI analysis failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("AI Agent Test")
    print("=" * 60)
    print()
    
    success = test_ai_agent()
    
    print()
    print("=" * 60)
    if success:
        print("✅ AI agent test passed!")
    else:
        print("❌ AI agent test failed!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
