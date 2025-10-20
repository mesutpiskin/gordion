"""
Prompt configuration manager
"""

import yaml
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages prompts from configuration"""
    
    def __init__(self, prompts_path: str = "config/prompts.yaml"):
        """
        Initialize prompt manager
        
        Args:
            prompts_path: Path to prompts config file
        """
        self.prompts_path = prompts_path
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict:
        """Load prompts from config file"""
        try:
            with open(self.prompts_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            logger.error(f"Error loading prompts config: {str(e)}")
            return {}
            
    def get_active_language(self) -> str:
        """Get active language from config"""
        return self.prompts.get('language', 'tr')
        
    def get_prompt(self, prompt_type: str) -> Optional[str]:
        """
        Get prompt by type for active language
        
        Args:
            prompt_type: Type of prompt (e.g. pr_analysis_system_prompt)
            
        Returns:
            Prompt text if found, None otherwise
        """
        lang = self.get_active_language()
        lang_prompts = self.prompts.get(lang, {})
        return lang_prompts.get(prompt_type)