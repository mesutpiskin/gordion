"""
AI Agent for analyzing pull requests
"""

import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI
from .repository_rules import RepositoryRulesManager

logger = logging.getLogger(__name__)


class AIAgent:
    """AI agent for PR analysis"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", 
                 temperature: float = 0.3, max_tokens: int = 2000,
                 rules_config_path: str = "config/repository_rules.yaml"):
        """
        Initialize AI agent
        
        Args:
            api_key: OpenAI API key
            model: Model to use
            temperature: Temperature parameter
            max_tokens: Maximum tokens
            rules_config_path: Path to repository rules config
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.rules_manager = RepositoryRulesManager(rules_config_path)
        
        self.system_prompt = """Sen bir kod review uzmanısın. Sana bir Pull Request'in detayları verilecek.
Görevin, PR'ı analiz edip approve edilmesi gerekip gerekmediğini değerlendirmek.

Değerlendirme kriterleri:
1. Kod değişiklikleri mantıklı ve temiz mi?
2. Potansiyel bug'lar var mı?
3. Security riskleri var mı?
4. Best practice'lere uyuyor mu?
5. Test dosyaları dahil mi?
6. Değişiklik miktarı makul mü?

Cevabını şu JSON formatında ver (sadece JSON, başka açıklama ekleme):
{
  "approve": true/false,
  "confidence_score": 0-100 arası sayı,
  "reasoning": "detaylı açıklama",
  "concerns": ["endişe 1", "endişe 2", ...]
}"""
    
    def _enhance_prompt_with_repo_rules(self, repository_name: str, prompt_type: str, base_prompt: str) -> str:
        """
        Enhance the base prompt with repository specific rules and prompts
        
        Args:
            repository_name: Name of the repository
            prompt_type: Type of prompt (e.g. code_review, pr_analysis)
            base_prompt: Base prompt to enhance
            
        Returns:
            Enhanced prompt with repository rules
        """
        # Get repository specific prompts
        repo_prompts = self.rules_manager.get_repository_prompts(repository_name)
        repo_rules = self.rules_manager.get_repository_rules(repository_name)
        repo_config = self.rules_manager.get_repository_config(repository_name)
        
        # If no repository specific config exists, return base prompt
        if not repo_config:
            return base_prompt
            
        # Build tech stack section
        tech_stack = repo_config.get('tech_stack', {})
        tech_stack_prompt = "\nRepository Technology Stack:\n"
        for key, value in tech_stack.items():
            tech_stack_prompt += f"- {key}: {value}\n"
            
        # Build rules section
        rules_prompt = "\nRepository Specific Rules:\n"
        for rule in repo_rules:
            rules_prompt += f"- {rule}\n"
            
        # Get repository specific prompt for this type if exists
        specific_prompt = repo_prompts.get(prompt_type, "")
        
        # Combine all prompts
        enhanced_prompt = f"""
{base_prompt}

Repository Context:
{tech_stack_prompt}
{rules_prompt}

Repository Specific Guidelines:
{specific_prompt}
"""
        return enhanced_prompt.strip()

    def analyze_pr(self, pr_data: Dict, repository_name: str) -> Dict:
        """
        Analyze a pull request using AI
        
        Args:
            pr_data: Pull request data
            repository_name: Name of the repository
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing PR #{pr_info.get('id')} with AI...")
        
        # Prepare PR summary for AI
        pr_summary = self._prepare_pr_summary(pr_info)
        
        # Get base prompt from config
        base_prompt = "Please review this pull request..."  # Load from config
        
        # Enhance prompt with repository rules
        enhanced_prompt = self._enhance_prompt_with_repo_rules(
            repository_name=repository_name,
            prompt_type="pr_analysis",
            base_prompt=base_prompt
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": json.dumps(pr_data)}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing PR: {str(e)}")
            return {"error": str(e)}
    
    def _prepare_pr_summary(self, pr_info: Dict) -> str:
        """
        Prepare PR summary for AI analysis
        
        Args:
            pr_info: PR information dictionary
            
        Returns:
            Formatted summary string
        """
        # Extract key information
        title = pr_info.get('title', 'No title')
        description = pr_info.get('description', 'No description')
        author = pr_info.get('author', {}).get('user', {}).get('displayName', 'Unknown')
        
        # Changed files info
        changes = pr_info.get('changes', [])
        files_changed = []
        total_additions = 0
        total_deletions = 0
        
        for change in changes:
            # Handle both old dict format and new string format
            path_obj = change.get('path', 'unknown')
            if isinstance(path_obj, dict):
                path = path_obj.get('toString', 'unknown')
            else:
                path = path_obj
            
            change_type = change.get('type', 'MODIFY')
            files_changed.append(f"- {change_type}: {path}")
            
            # Try to count lines (if available in API response)
            # Note: Stash API might not provide exact line counts in changes endpoint
        
        # Get diff if available
        diff = pr_info.get('diff', '')
        if diff:
            # Count additions/deletions from diff
            for line in diff.split('\n'):
                if line.startswith('+') and not line.startswith('+++'):
                    total_additions += 1
                elif line.startswith('-') and not line.startswith('---'):
                    total_deletions += 1
        
        # Comments and activities
        activities = pr_info.get('activities', [])
        comment_count = sum(1 for a in activities if a.get('action') == 'COMMENTED')
        
        # Build summary
        summary = f"""Pull Request Analizi

Başlık: {title}

Açıklama:
{description}

Yazar: {author}

Değişen Dosya Sayısı: {len(files_changed)}
Eklenen Satır: ~{total_additions}
Silinen Satır: ~{total_deletions}
Yorum Sayısı: {comment_count}

Değişen Dosyalar:
{chr(10).join(files_changed[:20])}
{f'... ve {len(files_changed) - 20} dosya daha' if len(files_changed) > 20 else ''}

"""
        
        # Add diff summary (truncate if too long)
        if diff:
            summary += "\nKod Değişiklikleri (Özet):\n"
            diff_lines = diff.split('\n')[:100]  # First 100 lines
            summary += '\n'.join(diff_lines)
            if len(diff.split('\n')) > 100:
                summary += "\n... (diff çok uzun, kısaltıldı)"
        
        return summary
    
    def get_approval_comment(self, analysis: Optional[Dict], fallback_reason: str = "") -> str:
        """
        Generate approval comment based on AI analysis
        
        Args:
            analysis: AI analysis result (can be None)
            fallback_reason: Reason to use if AI analysis is not available
            
        Returns:
            Comment text
        """
        if not analysis:
            # AI başarısız oldu, fallback comment
            comment = f"""🤖 **AI Agent Otomatik Approval**

✅ Bu PR otomatik olarak approve edildi.

**Durum:** AI analizi yapılamadı ({fallback_reason})

**Neden Approve Edildi:**
- Otomatik approval ayarları aktif
- Kritik dosya değişikliği yok
- PR temel kriterleri karşılıyor

⚠️ **Önemli:** AI analizi yapılamadığı için bu otomatik bir onay. Manuel review önerilir.
"""
            return comment
        
        reasoning = analysis.get('reasoning', '')
        confidence = analysis.get('confidence_score', 0)
        concerns = analysis.get('concerns', [])
        
        comment = f"""🤖 **AI Agent Otomatik Approval**

✅ Bu PR AI analizi sonucunda approve edildi.

**Güven Skoru:** {confidence}/100

**Değerlendirme:**
{reasoning}
"""
        
        if concerns:
            comment += "\n**Dikkat Edilmesi Gerekenler:**\n"
            for concern in concerns:
                comment += f"- ⚠️ {concern}\n"
        
        comment += "\n_Bu otomatik bir değerlendirmedir. Kritik değişiklikler için manuel review önerilir._"
        
        return comment
