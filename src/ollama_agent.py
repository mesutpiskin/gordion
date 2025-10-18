"""
Gordion AI Code Review Agent for analyzing pull requests locally
"""

import json
import logging
import requests
from typing import Dict, List, Optional
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class OllamaAgent:
    """Local AI agent using Ollama for PR analysis"""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "llama3.1:8b",
                 temperature: float = 0.3):
        """
        Initialize Ollama agent
        
        Args:
            base_url: Ollama API URL (default: http://localhost:11434)
            model: Model to use (e.g., llama3.1:8b, codellama:13b, mistral:7b)
            temperature: Temperature parameter
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        
        # Load prompts from config with language support
        self.prompts = self._load_prompts()
        self.language = self.prompts.get('language', 'tr')
        
        # Get language-specific prompts
        lang_prompts = self.prompts.get(self.language, self.prompts.get('tr', {}))
        
        self.system_prompt = lang_prompts.get('pr_analysis_system_prompt', self._get_default_system_prompt())
        self.inline_review_prompt = lang_prompts.get('inline_review_system_prompt', self._get_default_inline_prompt())
        self.rejection_template = lang_prompts.get('rejection_comment_template', '')
        self.approval_template = lang_prompts.get('approval_comment_template', '')
        self.fallback_template = lang_prompts.get('fallback_approval_comment', '')
        self.inline_prefix = lang_prompts.get('inline_comment_prefix', {})
        
        logger.info(f"Ollama agent initialized with language: {self.language}")
    
    def _load_prompts(self) -> Dict:
        """Load prompts from prompts.yaml"""
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'prompts.yaml'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("prompts.yaml not found, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Error loading prompts.yaml: {e}")
            return {}
    
    def _get_default_system_prompt(self) -> str:
        """Fallback system prompt if config fails"""
        return """You are a code review expert. You will be given Pull Request details.
Your task is to analyze the PR and evaluate whether it should be approved.

Respond in JSON format:
{
  "approve": true/false,
  "confidence_score": 0-100,
  "reasoning": "detailed explanation",
  "concerns": ["concern 1", "concern 2", ...]
}"""
    
    def _get_default_inline_prompt(self) -> str:
        """Fallback inline prompt if config fails"""
        return """You are a code review expert. You will be given file changes.
Provide inline comment suggestions.

Respond in JSON format:
{
  "comments": [
    {
      "line": line number,
      "comment": "comment text",
      "severity": "info/warning/critical"
    }
  ]
}"""
    
    def check_connection(self) -> bool:
        """
        Check if Ollama server is running and accessible
        
        Returns:
            True if Ollama is accessible
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama server is running")
                return True
            else:
                logger.warning(f"⚠️  Ollama server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️  Cannot connect to Ollama: {e}")
            return False
    
    def check_model_available(self) -> bool:
        """
        Check if the specified model is available
        
        Returns:
            True if model is available
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [m.get('name') for m in models]
                
                if self.model in available_models:
                    logger.info(f"✅ Model '{self.model}' is available")
                    return True
                else:
                    logger.warning(f"⚠️  Model '{self.model}' not found. Available models: {available_models}")
                    logger.warning(f"💡 Run: ollama pull {self.model}")
                    return False
            return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    def analyze_pull_request(self, pr_info: Dict) -> Optional[Dict]:
        """
        Analyze a pull request using local Ollama AI
        
        Args:
            pr_info: Dictionary containing PR information
            
        Returns:
            Analysis result dictionary with approve decision, or None if AI fails
        """
        logger.info(f"Analyzing PR #{pr_info.get('id')} with Ollama ({self.model})...")
        
        # Prepare PR summary for AI
        pr_summary = self._prepare_pr_summary(pr_info)
        
        try:
            # Call Ollama chat API
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": pr_summary}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": 2000  # max tokens
                    }
                },
                timeout=60  # Ollama can be slower, give 60 seconds
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API returned status {response.status_code}: {response.text}")
                logger.warning("⚠️  Ollama API hatası - AI analizi başarısız")
                return None
            
            response_data = response.json()
            content = response_data.get('message', {}).get('content', '')
            
            if not content:
                logger.error("Ollama returned empty response")
                return None
            
            logger.debug(f"Ollama Response: {content}")
            
            # Try to extract JSON from response (Ollama sometimes adds extra text)
            result = self._extract_json(content)
            
            if not result:
                logger.error("Failed to extract valid JSON from Ollama response")
                return None
            
            # Validate result
            required_fields = ['approve', 'confidence_score', 'reasoning']
            if not all(field in result for field in required_fields):
                logger.error("Ollama response missing required fields")
                return None
            
            logger.info(f"Ollama Analysis: approve={result['approve']}, "
                       f"confidence={result['confidence_score']}")
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out after 60 seconds")
            logger.warning("⚠️  Ollama timeout - AI analizi başarısız")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response as JSON: {e}")
            logger.warning("⚠️  Ollama JSON parse hatası - AI analizi başarısız")
            return None
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            logger.warning("⚠️  Ollama hatası - AI analizi başarısız")
            return None
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from text (handles cases where model adds extra text)
        
        Args:
            text: Text containing JSON
            
        Returns:
            Parsed JSON dictionary or None
        """
        # Try to parse directly
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON block in text
        try:
            # Look for { ... } pattern
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _prepare_pr_summary(self, pr_info: Dict) -> str:
        """
        Prepare PR summary for AI analysis
        
        Args:
            pr_info: PR information dictionary
            
        Returns:
            Formatted summary string
        """
        title = pr_info.get('title', 'N/A')
        description = pr_info.get('description', 'No description')
        author = pr_info.get('author', {}).get('name', 'Unknown')
        
        # Get file changes
        changes = pr_info.get('changes', [])
        total_files = len(changes)
        
        # Calculate additions/deletions
        total_additions = sum(c.get('additions', 0) for c in changes)
        total_deletions = sum(c.get('deletions', 0) for c in changes)
        
        # Get file list (handle both old dict format and new string format)
        files_changed = []
        for c in changes[:20]:
            path_obj = c.get('path', 'unknown')
            if isinstance(path_obj, dict):
                path = path_obj.get('toString', 'unknown')
            else:
                path = path_obj
            files_changed.append(path)
        
        if total_files > 20:
            files_changed.append(f"... and {total_files - 20} more files")
        
        # Get diff content
        diff = pr_info.get('diff', '')
        diff_preview = ""
        if diff:
            # Truncate diff if too long (max 3000 chars for context)
            if len(diff) > 3000:
                diff_preview = diff[:3000] + "\n\n... (diff truncated)"
            else:
                diff_preview = diff
        
        summary = f"""Pull Request Analizi

Başlık: {title}
Yazar: {author}
Açıklama: {description}

İstatistikler:
- Değişen dosya sayısı: {total_files}
- Eklenen satır: {total_additions}
- Silinen satır: {total_deletions}

Değişen dosyalar:
{chr(10).join(f"- {f}" for f in files_changed)}"""

        # Add diff content if available
        if diff_preview:
            summary += f"""

Kod Değişiklikleri (Diff):
```
{diff_preview}
```

Bu diff'i incele ve approve edilip edilmemesi gerektiğini değerlendir."""
        else:
            summary += "\n\nBu PR'ı analiz et ve approve edilip edilmemesi gerektiğini değerlendir."

        return summary
    
    def get_approval_comment(self, analysis: Optional[Dict] = None, fallback_reason: str = "") -> str:
        """
        Generate approval comment based on AI analysis
        
        Args:
            analysis: AI analysis result (can be None if AI failed)
            fallback_reason: Reason for fallback approval (if AI failed)
            
        Returns:
            Comment string
        """
        # Use fallback template if AI failed
        if analysis is None:
            if self.fallback_template:
                return self.fallback_template.format(reason=fallback_reason or "AI analysis unavailable")
            if fallback_reason:
                return f"✅ Auto-approved by Gordion AI Code Review Agent ({fallback_reason})"
            return "✅ Auto-approved by Gordion AI Code Review Agent (AI analysis failed - fallback mode)"
        
        confidence = analysis.get('confidence_score', 0)
        reasoning = analysis.get('reasoning', 'No specific reasoning provided')
        concerns = analysis.get('concerns', [])
        
        # Build concerns section
        concerns_section = ""
        if concerns:
            if self.language == 'tr':
                concerns_section = "**Potansiyel Endişeler:**\n"
            else:
                concerns_section = "**Potential Concerns:**\n"
            for concern in concerns:
                concerns_section += f"- {concern}\n"
        
        # Use template if available
        if self.approval_template:
            return self.approval_template.format(
                confidence=confidence,
                reasoning=reasoning,
                concerns_section=concerns_section,
                model=self.model
            )
        
        # Fallback to hardcoded format
        comment = f"✅ Auto-approved by Gordion AI Code Review Agent\n\n"
        comment += f"**Confidence Score:** {confidence}%\n\n"
        comment += f"**Analysis:**\n{reasoning}\n"
        
        if concerns_section:
            comment += f"\n{concerns_section}"
        
        comment += f"\n*Analyzed by: {self.model}*"
        
        return comment
    
    def analyze_file_changes(self, file_path: str, file_changes: List[Dict]) -> Optional[Dict]:
        """
        Analyze specific file changes and generate inline comment suggestions
        
        Args:
            file_path: Path to the file being changed
            file_changes: List of hunks/segments with line changes
            
        Returns:
            Dictionary with inline comment suggestions, or None if analysis fails
        """
        logger.info(f"Analyzing file changes for: {file_path}")
        
        # Prepare change summary for AI
        change_summary = self._prepare_file_change_summary(file_path, file_changes)
        
        # Skip if no meaningful changes
        if not change_summary or len(change_summary) < 50:
            logger.debug(f"Skipping {file_path} - no meaningful changes")
            return {'comments': []}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.inline_review_prompt},
                        {"role": "user", "content": change_summary}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": 1500
                    }
                },
                timeout=45
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API returned status {response.status_code}")
                return None
            
            response_data = response.json()
            content = response_data.get('message', {}).get('content', '')
            
            if not content:
                logger.error("Ollama returned empty response")
                return None
            
            # Extract JSON
            result = self._extract_json(content)
            
            if not result or 'comments' not in result:
                logger.debug(f"No inline comments suggested for {file_path}")
                return {'comments': []}
            
            logger.info(f"Generated {len(result['comments'])} inline comment(s) for {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze file changes: {e}")
            return None
    
    def _prepare_file_change_summary(self, file_path: str, hunks: List[Dict]) -> str:
        """
        Prepare file change summary for inline review
        
        Args:
            file_path: Path to file
            hunks: List of hunks with segments
            
        Returns:
            Formatted summary string
        """
        summary = f"Dosya: {file_path}\n\n"
        summary += "Değişiklikler:\n\n"
        
        for hunk in hunks:
            for segment in hunk.get('segments', []):
                segment_type = segment.get('type', 'CONTEXT')
                
                # Focus on ADDED and REMOVED lines
                if segment_type in ['ADDED', 'REMOVED']:
                    for line_info in segment.get('lines', []):
                        line_num = line_info.get('destination', 0) if segment_type == 'ADDED' else line_info.get('source', 0)
                        line_text = line_info.get('line', '').strip()
                        
                        if line_text:  # Skip empty lines
                            prefix = '+' if segment_type == 'ADDED' else '-'
                            summary += f"[Satır {line_num}] {prefix} {line_text}\n"
        
        summary += "\n\nBu değişiklikleri incele ve gerekirse inline comment önerileri ver."
        summary += "\nSadece önemli konulara (bug, security, performance, best practices) yorum yap."
        
        return summary
