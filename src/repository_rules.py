"""
Repository rules manager for customizing prompts and rules per repository
"""

import os
import yaml
from typing import Dict, Optional

class RepositoryRulesManager:
    """Manages repository-specific rules and prompts"""
    
    def __init__(self, config_path: str = "config/repository_rules.yaml"):
        """
        Initialize repository rules manager
        
        Args:
            config_path: Path to repository rules config file
        """
        self.config_path = config_path
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict:
        """Load repository rules from yaml file"""
        if not os.path.exists(self.config_path):
            return {}
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_repository_config(self, repository_name: str) -> Optional[Dict]:
        """
        Get repository specific configuration
        
        Args:
            repository_name: Name of the repository
            
        Returns:
            Repository configuration if exists, None otherwise
        """
        return self.rules.get('repositories', {}).get(repository_name)
    
    def get_repository_prompts(self, repository_name: str) -> Dict[str, str]:
        """
        Get repository specific prompts
        
        Args:
            repository_name: Name of the repository
            
        Returns:
            Dictionary of prompt types and their values
        """
        config = self.get_repository_config(repository_name)
        if not config:
            return {}
        return config.get('prompts', {})
    
    def get_repository_rules(self, repository_name: str) -> list:
        """
        Get repository specific rules
        
        Args:
            repository_name: Name of the repository
            
        Returns:
            List of rules for the repository
        """
        config = self.get_repository_config(repository_name)
        if not config:
            return []
        return config.get('rules', [])