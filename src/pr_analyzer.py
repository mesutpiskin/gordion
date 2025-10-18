"""
PR Analyzer - Combines Stash client and AI agent
"""

import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


def is_oversized_pr(pr: Dict, config: Dict) -> bool:
    """
    Check if PR exceeds size limits
    
    Args:
        pr: Pull request dictionary
        config: Configuration dictionary
        
    Returns:
        True if PR is oversized
    """
    criteria = config.get('approval_criteria', {})
    changes = pr.get('changes', [])
    files_changed = len(changes)
    
    max_files = criteria.get('max_files_changed', 50)
    if files_changed > max_files:
        return True
    
    # Check line changes if available
    stats = calculate_pr_stats(pr)
    max_lines = criteria.get('max_lines_changed', 1000)
    if stats['total_changes'] > max_lines:
        return True
    
    return False


def calculate_pr_stats(pr: Dict) -> Dict:
    """
    Calculate statistics for PR (standalone function)
    
    Args:
        pr: Pull request with changes and diff
        
    Returns:
        Dictionary with stats
    """
    changes = pr.get('changes', [])
    diff = pr.get('diff', '')
    
    stats = {
        'files_changed': len(changes),
        'additions': 0,
        'deletions': 0,
        'total_changes': 0
    }
    
    # Count lines from diff
    if diff:
        for line in diff.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                stats['additions'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                stats['deletions'] += 1
    
    stats['total_changes'] = stats['additions'] + stats['deletions']
    
    return stats


class PRAnalyzer:
    """Analyze pull requests and make approval decisions"""
    
    def __init__(self, config: Dict):
        """
        Initialize PR analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.approval_criteria = config.get('approval_criteria', {})
    
    def should_analyze_pr(self, pr: Dict) -> tuple[bool, str]:
        """
        Check if PR should be analyzed based on basic criteria
        
        Args:
            pr: Pull request dictionary
            
        Returns:
            Tuple of (should_analyze, reason)
        """
        # Check if PR is open
        if pr.get('state') != 'OPEN':
            return False, "PR is not open"
        
        # Check for critical files first (always skip these)
        changes = pr.get('changes', [])
        critical_patterns = self.approval_criteria.get('critical_file_patterns', [])
        for change in changes:
            # Handle both old format (dict with toString) and new format (string)
            path_obj = change.get('path', '')
            if isinstance(path_obj, dict):
                file_path = path_obj.get('toString', '')
            else:
                file_path = path_obj
            
            if self._is_critical_file(file_path, critical_patterns):
                return False, f"Contains critical file: {file_path}"
        
        # Get file count
        files_changed = len(changes)
        
        # Check if oversized PRs should be auto-approved
        auto_approve_oversized = self.approval_criteria.get('auto_approve_oversized', False)
        max_files = self.approval_criteria.get('max_files_changed', 50)
        
        if files_changed > max_files:
            if auto_approve_oversized:
                return True, f"Oversized PR (auto-approve enabled): {files_changed} files"
            else:
                return False, f"Too many files changed ({files_changed} > {max_files})"
        
        return True, "Passed basic criteria"
    
    def _is_critical_file(self, file_path: str, patterns: List[str]) -> bool:
        """
        Check if file path matches critical file patterns
        
        Args:
            file_path: File path to check
            patterns: List of patterns to match against
            
        Returns:
            True if file is critical
        """
        for pattern in patterns:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            if re.match(regex_pattern, file_path):
                return True
        return False
    
    def calculate_pr_stats(self, pr: Dict) -> Dict:
        """
        Calculate statistics for PR
        
        Args:
            pr: Pull request with changes and diff
            
        Returns:
            Dictionary with stats
        """
        changes = pr.get('changes', [])
        diff = pr.get('diff', '')
        
        stats = {
            'files_changed': len(changes),
            'additions': 0,
            'deletions': 0,
            'total_changes': 0
        }
        
        # Count lines from diff
        if diff:
            for line in diff.split('\n'):
                if line.startswith('+') and not line.startswith('+++'):
                    stats['additions'] += 1
                elif line.startswith('-') and not line.startswith('---'):
                    stats['deletions'] += 1
        
        stats['total_changes'] = stats['additions'] + stats['deletions']
        
        return stats
    
    def should_approve_based_on_ai(self, analysis: Optional[Dict], pr: Dict) -> tuple[bool, str]:
        """
        Determine if PR should be approved based on AI analysis
        
        Args:
            analysis: AI analysis result (can be None if AI failed)
            pr: Pull request dictionary
            
        Returns:
            Tuple of (should_approve, reason)
        """
        # Check if AI analysis is available
        if not analysis:
            auto_approve_on_failure = self.approval_criteria.get('auto_approve_on_ai_failure', False)
            if auto_approve_on_failure:
                logger.warning("⚠️  AI analizi başarısız oldu, ancak otomatik onay aktif")
                return True, "AI unavailable - auto-approved (configured)"
            else:
                return False, "AI analysis failed and auto-approve disabled"
        
        # Check AI decision
        ai_approve = analysis.get('approve', False)
        if not ai_approve:
            reasoning = analysis.get('reasoning', 'AI recommended not to approve')
            return False, f"AI decision: {reasoning}"
        
        # Check confidence score
        confidence = analysis.get('confidence_score', 0)
        min_confidence = self.approval_criteria.get('min_confidence_score', 70)
        
        if confidence < min_confidence:
            return False, f"Confidence score too low ({confidence} < {min_confidence})"
        
        return True, f"AI approved with {confidence}% confidence"
    
    def extract_pr_identifiers(self, pr: Dict) -> Optional[tuple[str, str, int]]:
        """
        Extract project key, repo slug, and PR ID from PR object
        
        Args:
            pr: Pull request dictionary
            
        Returns:
            Tuple of (project_key, repo_slug, pr_id) or None
        """
        try:
            # Extract from toRef (destination)
            to_ref = pr.get('toRef', {})
            repository = to_ref.get('repository', {})
            
            project_key = repository.get('project', {}).get('key')
            repo_slug = repository.get('slug')
            pr_id = pr.get('id')
            
            if not all([project_key, repo_slug, pr_id]):
                logger.error("Could not extract PR identifiers")
                return None
            
            return project_key, repo_slug, pr_id
            
        except Exception as e:
            logger.error(f"Failed to extract PR identifiers: {e}")
            return None
