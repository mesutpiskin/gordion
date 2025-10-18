"""
Main application entry point
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Optional
import schedule

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
import yaml

from logger import setup_logger
from stash_client import StashClient
from ai_agent import AIAgent
from ollama_agent import OllamaAgent
from pr_analyzer import PRAnalyzer
from database import Database

logger = logging.getLogger(__name__)


class StashAgentApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize application"""
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.config = self._load_config()
        
        # Setup logger
        log_config = self.config.get('logging', {})
        setup_logger(
            log_level=os.getenv('LOG_LEVEL', log_config.get('level', 'INFO')),
            log_file=os.getenv('LOG_FILE', log_config.get('file', 'logs/agent.log')),
            console=log_config.get('console', True)
        )
        
        logger.info("=" * 60)
        logger.info("Stash PR Auto-Approve Agent Starting...")
        logger.info("=" * 60)
        
        # Initialize database
        self.db = Database()
        
        # Initialize clients
        self.stash_client = self._init_stash_client()
        self.ai_agent = self._init_ai_agent()
        self.pr_analyzer = PRAnalyzer(self.config)
        
        # Configuration
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 
                                           self.config.get('check_interval', 300)))
        self.dry_run = os.getenv('DRY_RUN', 
                                str(self.config.get('dry_run', False))).lower() == 'true'
        
        if self.dry_run:
            logger.warning("🔸 DRY RUN MODE - Will not actually approve PRs")
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _init_stash_client(self) -> StashClient:
        """Initialize Stash client with token or username/password"""
        stash_url = os.getenv('STASH_URL')
        stash_token = os.getenv('STASH_TOKEN')
        stash_username = os.getenv('STASH_USERNAME')
        stash_password = os.getenv('STASH_PASSWORD')
        
        if not stash_url:
            logger.error("Missing STASH_URL in .env file")
            sys.exit(1)
        
        logger.info(f"Initializing Stash client for: {stash_url}")
        
        # Prefer token over username/password
        if stash_token:
            logger.info("Using Personal Access Token authentication")
            return StashClient(stash_url, token=stash_token, username=stash_username)
        elif stash_username and stash_password:
            logger.info(f"Using Basic Authentication for user: {stash_username}")
            return StashClient(stash_url, username=stash_username, password=stash_password)
        else:
            logger.error("Missing Stash authentication in .env file")
            logger.error("Provide either:")
            logger.error("  - STASH_TOKEN (Personal Access Token)")
            logger.error("  - STASH_USERNAME + STASH_PASSWORD (Basic Auth)")
            sys.exit(1)
    
    def _init_ai_agent(self):
        """Initialize AI agent (OpenAI or Ollama)"""
        ai_provider = os.getenv('AI_PROVIDER', 'ollama').lower()
        
        if ai_provider == 'ollama':
            return self._init_ollama_agent()
        elif ai_provider == 'openai':
            return self._init_openai_agent()
        else:
            logger.error(f"Unknown AI_PROVIDER: {ai_provider}. Use 'openai' or 'ollama'")
            sys.exit(1)
    
    def _init_openai_agent(self) -> AIAgent:
        """Initialize OpenAI agent"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            logger.error("Missing OPENAI_API_KEY in .env file")
            sys.exit(1)
        
        ai_config = self.config.get('ai', {})
        model = os.getenv('OPENAI_MODEL', ai_config.get('model', 'gpt-4'))
        
        logger.info(f"Initializing OpenAI agent with model: {model}")
        return AIAgent(
            api_key=api_key,
            model=model,
            temperature=ai_config.get('temperature', 0.3),
            max_tokens=ai_config.get('max_tokens', 2000)
        )
    
    def _init_ollama_agent(self) -> OllamaAgent:
        """Initialize Ollama agent for local AI"""
        ai_config = self.config.get('ai', {})
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', ai_config.get('ollama_model', 'llama3.1:8b'))
        
        logger.info(f"Initializing Ollama agent with model: {ollama_model}")
        logger.info(f"Ollama URL: {ollama_url}")
        
        agent = OllamaAgent(
            base_url=ollama_url,
            model=ollama_model,
            temperature=ai_config.get('temperature', 0.3)
        )
        
        # Check Ollama connection
        if not agent.check_connection():
            logger.warning("⚠️  Cannot connect to Ollama server")
            logger.warning("💡 Make sure Ollama is running: brew install ollama && ollama serve")
            logger.warning("⚠️  Continuing anyway - will use fallback approval if needed")
        elif not agent.check_model_available():
            logger.warning(f"⚠️  Model '{ollama_model}' not available")
            logger.warning(f"💡 Pull the model: ollama pull {ollama_model}")
            logger.warning("⚠️  Continuing anyway - will use fallback approval if needed")
        
        return agent
    
    def process_pull_requests(self) -> None:
        """Main processing loop - check and process PRs"""
        try:
            logger.info("-" * 60)
            logger.info("Checking for assigned pull requests...")
            
            # Get assigned PRs
            pull_requests = self.stash_client.get_assigned_pull_requests()
            
            if not pull_requests:
                logger.info("No assigned pull requests found")
                return
            
            logger.info(f"Processing {len(pull_requests)} pull request(s)...")
            
            for pr in pull_requests:
                self._process_single_pr(pr)
                
        except Exception as e:
            logger.error(f"Error processing pull requests: {e}", exc_info=True)
    
    def _handle_rejection(self, pr_details: Dict, project_key: str, repo_slug: str, 
                         pr_id: int, analysis: Optional[Dict], reason: str) -> None:
        """
        Handle PR rejection with comment and/or decline
        
        Args:
            pr_details: PR details dictionary
            project_key: Project key
            repo_slug: Repository slug
            pr_id: PR ID
            analysis: AI analysis result (can be None)
            reason: Rejection reason
        """
        try:
            comment_on_reject = self.config.get('approval_criteria', {}).get('comment_on_reject', True)
            mark_needs_work = self.config.get('approval_criteria', {}).get('mark_needs_work_on_reject', True)
            decline_on_reject = self.config.get('approval_criteria', {}).get('decline_on_reject', False)
            add_inline_comments = self.config.get('approval_criteria', {}).get('add_inline_comments_on_reject', True)
            
            # Add inline comments on file changes (if enabled)
            if add_inline_comments and isinstance(self.ai_agent, OllamaAgent):
                self._add_inline_comments(pr_details, project_key, repo_slug, pr_id)
            
            # Build rejection comment
            if comment_on_reject:
                comment = self._build_rejection_comment(analysis, reason)
                
                if self.dry_run:
                    logger.info("🔸 DRY RUN - Would have added rejection comment:")
                    logger.info(f"   {comment[:200]}...")
                else:
                    logger.info("💬 Adding rejection comment to PR...")
                    if self.stash_client.add_comment_to_pull_request(
                        project_key, repo_slug, pr_id, comment
                    ):
                        logger.info("✅ Rejection comment added")
                    else:
                        logger.error("❌ Failed to add rejection comment")
            
            # Mark as "Needs Work" if configured
            if mark_needs_work:
                if self.dry_run:
                    logger.warning("🔸 DRY RUN - Would have marked PR as NEEDS WORK")
                else:
                    logger.warning("⚠️  Marking PR as NEEDS WORK...")
                    if self.stash_client.mark_needs_work(project_key, repo_slug, pr_id):
                        logger.warning("⚠️  PR marked as NEEDS WORK")
                    else:
                        logger.error("❌ Failed to mark PR as needs work")
            
            # Decline PR if configured (more aggressive than needs_work)
            if decline_on_reject:
                if self.dry_run:
                    logger.warning("🔸 DRY RUN - Would have DECLINED this PR")
                else:
                    logger.warning("⛔ Declining PR...")
                    pr_version = pr_details.get('version', 0)
                    if self.stash_client.decline_pull_request(
                        project_key, repo_slug, pr_id, pr_version
                    ):
                        logger.warning("⛔ PR has been DECLINED")
                    else:
                        logger.error("❌ Failed to decline PR")
            
            # Log rejection to database
            status = 'declined' if decline_on_reject else 'needs_work' if mark_needs_work else 'rejected'
            stats = self.pr_analyzer.calculate_pr_stats(pr_details)
            self._log_pr_to_database(pr_details, project_key, repo_slug, pr_id, 
                                    status, analysis, stats)
                        
        except Exception as e:
            logger.error(f"Error handling rejection: {e}", exc_info=True)
    
    def _add_inline_comments(self, pr_details: Dict, project_key: str, repo_slug: str, pr_id: int) -> None:
        """
        Add inline comments to specific code changes
        
        Args:
            pr_details: Full PR details with changes
            project_key: Project key
            repo_slug: Repository slug
            pr_id: PR ID
        """
        try:
            changes = pr_details.get('changes', [])
            if not changes:
                logger.debug("No changes to analyze for inline comments")
                return
            
            logger.info(f"🔍 Analyzing {len(changes)} file(s) for inline comments...")
            
            total_comments_added = 0
            
            # Analyze each file
            for file_change in changes[:10]:  # Limit to first 10 files
                file_path = file_change.get('path', 'unknown')
                hunks = file_change.get('hunks', [])
                
                if not hunks:
                    continue
                
                # Skip certain file types
                if file_path.endswith(('.json', '.xml', '.md', '.txt', '.yml', '.yaml')):
                    logger.debug(f"Skipping non-code file: {file_path}")
                    continue
                
                logger.debug(f"Analyzing file: {file_path}")
                
                # Get AI suggestions for this file
                file_analysis = self.ai_agent.analyze_file_changes(file_path, hunks)
                
                if not file_analysis or not file_analysis.get('comments'):
                    continue
                
                # Add inline comments
                for comment_item in file_analysis['comments']:
                    line_num = comment_item.get('line', 0)
                    comment_text = comment_item.get('comment', '')
                    severity = comment_item.get('severity', 'info')
                    
                    if not line_num or not comment_text:
                        continue
                    
                    # Add severity emoji
                    severity_emoji = {
                        'critical': '🔴',
                        'warning': '⚠️',
                        'info': 'ℹ️'
                    }.get(severity, 'ℹ️')
                    
                    formatted_comment = f"{severity_emoji} **Gordion AI Review**\n\n{comment_text}"
                    
                    if self.dry_run:
                        logger.info(f"🔸 DRY RUN - Would add inline comment to {file_path}:{line_num}")
                        logger.info(f"   {formatted_comment[:100]}...")
                    else:
                        if self.stash_client.add_inline_comment(
                            project_key, repo_slug, pr_id,
                            file_path, line_num, formatted_comment
                        ):
                            total_comments_added += 1
                            logger.info(f"📝 Added inline comment to {file_path}:{line_num}")
            
            if total_comments_added > 0:
                logger.info(f"✅ Added {total_comments_added} inline comment(s) to PR")
            else:
                logger.info("ℹ️  No inline comments needed")
                
        except Exception as e:
            logger.error(f"Error adding inline comments: {e}", exc_info=True)
    
    def _log_pr_to_database(self, pr_details: Dict, project_key: str, repo_slug: str, 
                           pr_id: int, status: str, analysis: Optional[Dict], stats: Dict) -> None:
        """
        Log PR to database for history tracking
        
        Args:
            pr_details: PR details
            project_key: Project key
            repo_slug: Repository slug
            pr_id: PR ID
            status: Status (approved, rejected, needs_work, declined)
            analysis: AI analysis result
            stats: PR statistics
        """
        try:
            author_user = pr_details.get('author', {}).get('user', {})
            author_name = author_user.get('displayName', author_user.get('name', 'Unknown'))
            
            pr_data = {
                'pr_id': pr_id,
                'project_key': project_key,
                'repo_slug': repo_slug,
                'title': pr_details.get('title', 'No title'),
                'author': author_name,
                'status': status,
                'confidence_score': analysis.get('confidence_score', 0) if analysis else 0,
                'reasoning': analysis.get('reasoning', '') if analysis else '',
                'concerns': analysis.get('concerns', []) if analysis else [],
                'files_changed': stats.get('files_changed', 0),
                'additions': stats.get('additions', 0),
                'deletions': stats.get('deletions', 0),
                'ai_model': getattr(self.ai_agent, 'model', 'unknown')
            }
            
            self.db.add_pr_record(pr_data)
            logger.debug(f"PR #{pr_id} logged to database")
        except Exception as e:
            logger.error(f"Error logging PR to database: {e}", exc_info=True)
    
    def _build_rejection_comment(self, analysis: Optional[Dict], reason: str) -> str:
        """
        Build rejection comment based on AI analysis
        
        Args:
            analysis: AI analysis result (can be None)
            reason: Rejection reason
            
        Returns:
            Comment text
        """
        if not analysis:
            return f"""🤖 **AI Code Review - NOT APPROVED**

**Reason:** {reason}

⚠️ This PR was not automatically approved. Please review the changes carefully.

*Automated by Stash PR Agent*"""
        
        confidence = analysis.get('confidence_score', 0)
        reasoning = analysis.get('reasoning', 'No specific reasoning provided')
        concerns = analysis.get('concerns', [])
        
        comment = f"""🤖 **AI Code Review - NOT APPROVED**

**Confidence:** {confidence}%

**Analysis:**
{reasoning}
"""
        
        if concerns:
            comment += f"\n**⚠️ Concerns:**\n"
            for concern in concerns:
                comment += f"- {concern}\n"
        
        comment += "\n---\n*Please address these issues before merging.*\n"
        comment += f"*Automated by Gordion PR Agent using {getattr(self.ai_agent, 'model', 'AI')}*"
        
        return comment
    
    def _process_single_pr(self, pr: Dict) -> None:
        """
        Process a single pull request
        
        Args:
            pr: Pull request dictionary
        """
        try:
            # Extract identifiers
            identifiers = self.pr_analyzer.extract_pr_identifiers(pr)
            if not identifiers:
                logger.error("Could not extract PR identifiers")
                return
            
            project_key, repo_slug, pr_id = identifiers
            
            logger.info(f"\n{'='*50}")
            logger.info(f"📋 Processing PR #{pr_id}: {pr.get('title', 'No title')}")
            logger.info(f"   Repository: {project_key}/{repo_slug}")
            logger.info(f"   Author: {pr.get('author', {}).get('user', {}).get('displayName', 'Unknown')}")
            
            # Check if already approved by us
            approval_status = self.stash_client.check_my_approval_status(
                project_key, repo_slug, pr_id
            )
            
            if approval_status == 'APPROVED':
                logger.info(f"✅ Already approved this PR, skipping...")
                return
            
            # Get detailed information
            logger.info("Fetching PR details...")
            pr_details = self.stash_client.get_pull_request_details(
                project_key, repo_slug, pr_id
            )
            
            if not pr_details:
                logger.error("Could not fetch PR details")
                return
            
            # Get changes
            changes = self.stash_client.get_pull_request_changes(
                project_key, repo_slug, pr_id
            )
            pr_details['changes'] = changes
            
            # Get diff
            diff = self.stash_client.get_pull_request_diff(
                project_key, repo_slug, pr_id
            )
            pr_details['diff'] = diff
            
            # Debug: Print diff info
            if diff:
                diff_lines = len(diff.split('\n'))
                logger.info(f"   📄 Diff retrieved: {diff_lines} lines")
                logger.debug(f"   First 500 chars of diff:\n{diff[:500]}")
            else:
                logger.warning(f"   ⚠️  Diff is empty or None!")
            
            # Get activities
            activities = self.stash_client.get_pull_request_activities(
                project_key, repo_slug, pr_id
            )
            pr_details['activities'] = activities
            
            # Calculate stats
            stats = self.pr_analyzer.calculate_pr_stats(pr_details)
            logger.info(f"   Stats: {stats['files_changed']} files, "
                       f"+{stats['additions']} -{stats['deletions']} lines")
            
            # Debug: Print changes info
            logger.info(f"   📦 Changes retrieved: {len(changes)} file(s)")
            if changes:
                for i, change in enumerate(changes[:3]):  # First 3 files
                    file_path = change.get('path', 'unknown')
                    change_type = change.get('type', 'MODIFY')
                    hunks_count = len(change.get('hunks', []))
                    logger.info(f"      {i+1}. {change_type}: {file_path} ({hunks_count} hunk(s))")
            
            # Check basic criteria
            should_analyze, reason = self.pr_analyzer.should_analyze_pr(pr_details)
            if not should_analyze:
                logger.warning(f"⚠️  Skipping PR: {reason}")
                return
            
            # Check if this is an oversized PR
            from pr_analyzer import is_oversized_pr
            is_oversized = is_oversized_pr(pr_details, self.config)
            auto_approve_oversized = self.config.get('approval_criteria', {}).get('auto_approve_oversized', False)
            
            analysis = None
            fallback_reason = ""
            
            if is_oversized and auto_approve_oversized:
                logger.warning(f"⚠️  PR boyutu limit aşımı - AI analizi atlanıyor")
                logger.info(f"✅ Oversized PR otomatik approve (ayarlardan etkin)")
                fallback_reason = "oversized PR, AI analysis skipped"
                should_approve = True
                approve_reason = f"Oversized PR auto-approved: {stats['files_changed']} files, {stats['total_changes']} lines"
            else:
                # AI Analysis
                logger.info("🤖 Running AI analysis...")
                analysis = self.ai_agent.analyze_pull_request(pr_details)
                
                if analysis:
                    logger.info(f"   AI Decision: {'✅ APPROVE' if analysis.get('approve') else '❌ DO NOT APPROVE'}")
                    logger.info(f"   Confidence: {analysis.get('confidence_score')}%")
                    logger.info(f"   Reasoning: {analysis.get('reasoning')}")
                    
                    if analysis.get('concerns'):
                        logger.warning(f"   Concerns: {', '.join(analysis.get('concerns'))}")
                else:
                    logger.error("❌ AI analysis failed")
                    auto_approve_on_failure = self.config.get('approval_criteria', {}).get('auto_approve_on_ai_failure', False)
                    if auto_approve_on_failure:
                        logger.warning("⚠️  AI hatası - ancak otomatik onay aktif")
                        fallback_reason = "AI service unavailable"
                    else:
                        logger.info("❌ AI hatası ve otomatik onay kapalı - PR atlanıyor")
                        return
                
                # Check if should approve
                should_approve, approve_reason = self.pr_analyzer.should_approve_based_on_ai(analysis, pr_details)
                
                if not should_approve:
                    logger.info(f"❌ Not approving: {approve_reason}")
                    
                    # Handle rejection based on config
                    self._handle_rejection(pr_details, project_key, repo_slug, pr_id, analysis, approve_reason)
                    return
            
            logger.info(f"✅ Decision: APPROVE - {approve_reason}")
            
            # Approve PR
            if self.dry_run:
                logger.info("🔸 DRY RUN - Would have approved this PR")
                # Log to database even in dry run
                self._log_pr_to_database(pr_details, project_key, repo_slug, pr_id, 
                                        'approved', analysis, stats)
            else:
                # Add comment
                comment = self.ai_agent.get_approval_comment(analysis, fallback_reason)
                comment_success = self.stash_client.add_comment_to_pull_request(
                    project_key, repo_slug, pr_id, comment
                )
                
                # Approve
                if self.stash_client.approve_pull_request(project_key, repo_slug, pr_id):
                    logger.info("🎉 Successfully approved PR!")
                    # Log to database
                    self._log_pr_to_database(pr_details, project_key, repo_slug, pr_id, 
                                            'approved', analysis, stats)
                else:
                    logger.error("Failed to approve PR")
                    
        except Exception as e:
            logger.error(f"Error processing PR: {e}", exc_info=True)
    
    def run_once(self) -> None:
        """Run once and exit"""
        logger.info("Running in single-run mode...")
        self.process_pull_requests()
        logger.info("Single run completed")
    
    def run_continuous(self) -> None:
        """Run continuously with scheduled checks"""
        logger.info(f"Running in continuous mode (check every {self.check_interval}s)")
        
        # Schedule the job
        schedule.every(self.check_interval).seconds.do(self.process_pull_requests)
        
        # Run immediately on start
        self.process_pull_requests()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")


def main():
    """Main entry point"""
    app = StashAgentApp()
    
    # Check if should run once or continuously
    run_mode = os.getenv('RUN_MODE', 'continuous')
    
    if run_mode == 'once':
        app.run_once()
    else:
        app.run_continuous()


if __name__ == '__main__':
    main()
