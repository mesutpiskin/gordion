"""
Stash/Bitbucket Server API Client
"""

import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class StashClient:
    """Stash/Bitbucket Server API client"""
    
    def __init__(self, base_url: str, username: str = None, password: str = None, token: str = None):
        """
        Initialize Stash client
        
        Args:
            base_url: Stash server URL (e.g., https://stash.yourcompany.com.tr)
            username: Stash username (required for Basic Auth)
            password: Stash password (required for Basic Auth)
            token: Personal Access Token (alternative to username/password)
            
        Note:
            Either (username + password) OR token must be provided.
            Token takes precedence if both are provided.
        """
        self.base_url = base_url.rstrip('/')
        
        # YourCompany Stash uses /git prefix
        if not self.base_url.endswith('/git'):
            self.base_url += '/git'
        
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()
        
        # Choose authentication method
        if token:
            # Use Bearer Token authentication (Personal Access Token)
            logger.info("Using Bearer Token authentication")
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            })
            # For API calls that need username, try to get it from token validation
            if not username:
                self.username = self._get_current_user()
        elif username and password:
            # Use Basic Authentication (username + password)
            logger.info(f"Using Basic Authentication for user: {username}")
            self.session.auth = (username, password)
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
        else:
            raise ValueError("Either (username + password) or token must be provided")
    
    def _get_current_user(self) -> str:
        """
        Get current authenticated user's username
        
        Returns:
            Username string
        """
        try:
            response = self._make_request('GET', '/users')
            if response.status_code == 200:
                # If this endpoint works, try to get current user
                pass
            
            # Try getting current user from a different endpoint
            # Most Stash instances support this
            endpoint = '/application-properties'
            response = self._make_request('GET', endpoint)
            
            # Fallback: use 'unknown' if we can't determine
            return 'unknown'
        except Exception as e:
            logger.warning(f"Could not determine current user: {e}")
            return 'unknown'
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request to Stash API"""
        url = f"{self.base_url}/rest/api/1.0{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get_assigned_pull_requests(self) -> List[Dict]:
        """
        Get pull requests assigned to the current user as reviewer
        
        Returns:
            List of pull request dictionaries
        """
        logger.info("Fetching assigned pull requests...")
        
        try:
            # Try different API endpoints for Bitbucket Server
            # Method 1: Inbox API (more common in newer versions)
            endpoint = f"/inbox/pull-requests"
            params = {
                'role': 'REVIEWER',
                'state': 'OPEN',
                'limit': 100,
                'start': 0
            }
            
            try:
                response = self._make_request('GET', endpoint, params=params)
                data = response.json()
                pull_requests = data.get('values', [])
                logger.info(f"Found {len(pull_requests)} assigned pull requests (inbox API)")
                return pull_requests
            except Exception as e1:
                logger.debug(f"Inbox API failed, trying alternative: {e1}")
                
                # Method 2: Try getting PRs from all projects
                # First, get current user info
                try:
                    user_endpoint = "/users"
                    user_params = {'filter': self.username, 'limit': 1}
                    user_response = self._make_request('GET', user_endpoint, params=user_params)
                    user_data = user_response.json()
                    
                    if not user_data.get('values'):
                        logger.error(f"Could not find user: {self.username}")
                        return []
                    
                    # Get all projects and search for PRs
                    projects_endpoint = "/projects"
                    projects_params = {'limit': 1000}
                    projects_response = self._make_request('GET', projects_endpoint, params=projects_params)
                    projects_data = projects_response.json()
                    
                    all_prs = []
                    for project in projects_data.get('values', [])[:20]:  # Limit to first 20 projects
                        project_key = project.get('key')
                        
                        # Get repos in project
                        repos_endpoint = f"/projects/{project_key}/repos"
                        repos_params = {'limit': 100}
                        repos_response = self._make_request('GET', repos_endpoint, params=repos_params)
                        repos_data = repos_response.json()
                        
                        for repo in repos_data.get('values', []):
                            repo_slug = repo.get('slug')
                            
                            # Get PRs in repo
                            pr_endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests"
                            pr_params = {'state': 'OPEN', 'limit': 50}
                            
                            try:
                                pr_response = self._make_request('GET', pr_endpoint, params=pr_params)
                                pr_data = pr_response.json()
                                
                                # Filter PRs where current user is reviewer
                                for pr in pr_data.get('values', []):
                                    reviewers = pr.get('reviewers', [])
                                    for reviewer in reviewers:
                                        if reviewer.get('user', {}).get('name') == self.username:
                                            all_prs.append(pr)
                                            break
                            except:
                                continue
                    
                    logger.info(f"Found {len(all_prs)} assigned pull requests (scanning projects)")
                    return all_prs
                    
                except Exception as e2:
                    logger.error(f"Alternative API methods failed: {e2}")
                    return []
            
        except Exception as e:
            logger.error(f"Failed to fetch pull requests: {e}")
            return []
    
    def get_pull_request_details(self, project_key: str, repo_slug: str, pr_id: int) -> Optional[Dict]:
        """
        Get detailed information about a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Pull request details dictionary
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}"
            response = self._make_request('GET', endpoint)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch PR details: {e}")
            return None
    
    def get_pull_request_changes(self, project_key: str, repo_slug: str, pr_id: int) -> List[Dict]:
        """
        Get file changes in a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            List of changed files
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/changes"
            params = {'limit': 1000}
            response = self._make_request('GET', endpoint, params=params)
            data = response.json()
            return data.get('values', [])
        except Exception as e:
            logger.error(f"Failed to fetch PR changes: {e}")
            return []
    
    def get_pull_request_diff(self, project_key: str, repo_slug: str, pr_id: int) -> str:
        """
        Get diff of a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Diff as string
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/diff"
            params = {'contextLines': 3}
            response = self._make_request('GET', endpoint, params=params)
            
            # Parse diff response
            data = response.json()
            diffs = data.get('diffs', [])
            
            diff_text = ""
            for diff in diffs:
                # Handle None values for source/destination
                source_obj = diff.get('source')
                destination_obj = diff.get('destination')
                
                if source_obj and isinstance(source_obj, dict):
                    source = source_obj.get('toString', 'unknown')
                else:
                    source = 'unknown'
                
                if destination_obj and isinstance(destination_obj, dict):
                    destination = destination_obj.get('toString', 'unknown')
                else:
                    destination = 'unknown'
                
                diff_text += f"\n--- {source}\n+++ {destination}\n"
                
                for hunk in diff.get('hunks', []):
                    for segment in hunk.get('segments', []):
                        lines = segment.get('lines', [])
                        for line in lines:
                            line_content = line.get('line', '') if isinstance(line, dict) else str(line)
                            diff_text += line_content + '\n'
            
            return diff_text
        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            return ""
    
    def get_pull_request_activities(self, project_key: str, repo_slug: str, pr_id: int) -> List[Dict]:
        """
        Get activities (comments, approvals, etc.) for a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            List of activities
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/activities"
            params = {'limit': 100}
            response = self._make_request('GET', endpoint, params=params)
            data = response.json()
            return data.get('values', [])
        except Exception as e:
            logger.error(f"Failed to fetch PR activities: {e}")
            return []
    
    def approve_pull_request(self, project_key: str, repo_slug: str, pr_id: int) -> bool:
        """
        Approve a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/approve"
            response = self._make_request('POST', endpoint)
            logger.info(f"Successfully approved PR #{pr_id} in {project_key}/{repo_slug}")
            return True
        except Exception as e:
            logger.error(f"Failed to approve PR: {e}")
            return False
    
    def add_comment_to_pull_request(self, project_key: str, repo_slug: str, 
                                   pr_id: int, comment_text: str) -> bool:
        """
        Add a general comment to a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            comment_text: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/comments"
            payload = {'text': comment_text}
            response = self._make_request('POST', endpoint, json=payload)
            logger.info(f"Successfully added comment to PR #{pr_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add comment: {e}")
            return False
    
    def add_inline_comment(self, project_key: str, repo_slug: str, pr_id: int,
                          file_path: str, line_number: int, comment_text: str,
                          line_type: str = "ADDED") -> bool:
        """
        Add an inline comment to a specific line in a file
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            file_path: Path to file in the repository
            line_number: Line number to comment on
            comment_text: Comment text
            line_type: Type of line - "ADDED", "REMOVED", or "CONTEXT"
            
        Returns:
            True if successful, False otherwise
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/comments"
            
            # Payload for inline comment (anchored to specific file and line)
            payload = {
                'text': comment_text,
                'anchor': {
                    'path': file_path,
                    'line': line_number,
                    'lineType': line_type,
                    'fileType': 'TO'  # TO = destination (new version), FROM = source (old version)
                }
            }
            
            response = self._make_request('POST', endpoint, json=payload)
            logger.info(f"Successfully added inline comment to {file_path}:{line_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to add inline comment: {e}")
            return False
    
    def get_pull_request_changes(self, project_key: str, repo_slug: str, pr_id: int) -> List[Dict]:
        """
        Get detailed file changes for a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            List of file changes with hunks and line information
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/changes"
            params = {'limit': 1000}  # Get all changes
            response = self._make_request('GET', endpoint, params=params)
            
            data = response.json()
            changes = data.get('values', [])
            
            # Process changes to make them easier to work with
            processed_changes = []
            for change in changes:
                file_info = {
                    'path': change.get('path', {}).get('toString', 'unknown'),
                    'type': change.get('type', 'MODIFY'),  # MODIFY, ADD, DELETE, etc.
                    'hunks': []
                }
                
                # Extract hunks (changed sections)
                for hunk in change.get('hunks', []):
                    hunk_info = {
                        'source_line': hunk.get('sourceLine', 0),
                        'source_span': hunk.get('sourceSpan', 0),
                        'dest_line': hunk.get('destinationLine', 0),
                        'dest_span': hunk.get('destinationSpan', 0),
                        'segments': []
                    }
                    
                    # Extract segments (individual line changes)
                    for segment in hunk.get('segments', []):
                        segment_info = {
                            'type': segment.get('type', 'CONTEXT'),  # ADDED, REMOVED, CONTEXT
                            'lines': []
                        }
                        
                        for line in segment.get('lines', []):
                            line_info = {
                                'source': line.get('source', 0),
                                'destination': line.get('destination', 0),
                                'line': line.get('line', ''),
                                'truncated': line.get('truncated', False)
                            }
                            segment_info['lines'].append(line_info)
                        
                        hunk_info['segments'].append(segment_info)
                    
                    file_info['hunks'].append(hunk_info)
                
                processed_changes.append(file_info)
            
            logger.info(f"Retrieved {len(processed_changes)} file changes for PR #{pr_id}")
            return processed_changes
            
        except Exception as e:
            logger.error(f"Failed to get PR changes: {e}")
            return []
    
    def decline_pull_request(self, project_key: str, repo_slug: str, 
                            pr_id: int, version: int) -> bool:
        """
        Decline/reject a pull request
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            version: PR version (for optimistic locking)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/decline"
            payload = {'version': version}
            response = self._make_request('POST', endpoint, json=payload)
            logger.info(f"Successfully declined PR #{pr_id} in {project_key}/{repo_slug}")
            return True
        except Exception as e:
            logger.error(f"Failed to decline PR: {e}")
            return False
    
    def mark_needs_work(self, project_key: str, repo_slug: str, pr_id: int) -> bool:
        """
        Mark pull request as "Needs Work"
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}/participants/{self.username}"
            payload = {
                'user': {'name': self.username},
                'status': 'NEEDS_WORK'
            }
            response = self._make_request('PUT', endpoint, json=payload)
            logger.info(f"Successfully marked PR #{pr_id} as NEEDS_WORK in {project_key}/{repo_slug}")
            return True
        except Exception as e:
            logger.error(f"Failed to mark PR as needs work: {e}")
            return False
    
    def check_my_approval_status(self, project_key: str, repo_slug: str, pr_id: int) -> Optional[str]:
        """
        Check if current user has already approved the PR (current status, not history)
        
        Args:
            project_key: Project key
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            'APPROVED' if approved, 'UNAPPROVED' if not, None if error
        """
        try:
            # First, try to get current participant status (more accurate)
            endpoint = f"/projects/{project_key}/repos/{repo_slug}/pull-requests/{pr_id}"
            response = self._make_request('GET', endpoint)
            pr_data = response.json()
            
            # Check reviewers/participants
            reviewers = pr_data.get('reviewers', [])
            for reviewer in reviewers:
                user = reviewer.get('user', {})
                if user.get('name') == self.username:
                    status = reviewer.get('status', 'UNAPPROVED')
                    logger.debug(f"Current approval status for {self.username}: {status}")
                    return status
            
            # If not in reviewers list, check if in participants
            participants = pr_data.get('participants', [])
            for participant in participants:
                user = participant.get('user', {})
                if user.get('name') == self.username:
                    status = participant.get('status', 'UNAPPROVED')
                    logger.debug(f"Current participant status for {self.username}: {status}")
                    return status
            
            # User not found in reviewers or participants - not approved
            logger.debug(f"User {self.username} not found in reviewers/participants - UNAPPROVED")
            return 'UNAPPROVED'
            
        except Exception as e:
            logger.error(f"Failed to check approval status: {e}")
            # Fallback: check activities (less accurate, shows history)
            try:
                logger.debug("Falling back to activities check...")
                activities = self.get_pull_request_activities(project_key, repo_slug, pr_id)
                
                # Get the LATEST approval status by checking activities in reverse order
                latest_status = None
                for activity in reversed(activities):
                    action = activity.get('action')
                    user = activity.get('user', {})
                    
                    if user.get('name') == self.username:
                        if action == 'APPROVED':
                            latest_status = 'APPROVED'
                            break
                        elif action == 'UNAPPROVED':
                            latest_status = 'UNAPPROVED'
                            break
                
                return latest_status if latest_status else 'UNAPPROVED'
            except Exception as fallback_error:
                logger.error(f"Fallback approval check also failed: {fallback_error}")
                return None
