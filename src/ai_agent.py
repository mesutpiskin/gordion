"""
AI Agent for analyzing pull requests
"""

import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class AIAgent:
    """AI agent for PR analysis"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", 
                 temperature: float = 0.3, max_tokens: int = 2000):
        """
        Initialize AI agent
        
        Args:
            api_key: OpenAI API key
            model: Model to use
            temperature: Temperature parameter
            max_tokens: Maximum tokens
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
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
    
    def analyze_pull_request(self, pr_info: Dict) -> Optional[Dict]:
        """
        Analyze a pull request using AI
        
        Args:
            pr_info: Dictionary containing PR information
            
        Returns:
            Analysis result dictionary with approve decision, or None if AI fails
        """
        logger.info(f"Analyzing PR #{pr_info.get('id')} with AI...")
        
        # Prepare PR summary for AI
        pr_summary = self._prepare_pr_summary(pr_info)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": pr_summary}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=30  # 30 saniye timeout
            )
            
            content = response.choices[0].message.content
            logger.debug(f"AI Response: {content}")
            
            # Parse JSON response
            result = json.loads(content)
            
            # Validate result
            required_fields = ['approve', 'confidence_score', 'reasoning']
            if not all(field in result for field in required_fields):
                logger.error("AI response missing required fields")
                return None
            
            logger.info(f"AI Analysis: approve={result['approve']}, "
                       f"confidence={result['confidence_score']}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.warning("⚠️  AI JSON parse hatası - AI analizi başarısız")
            return None
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            logger.warning("⚠️  AI bağlantı/analiz hatası - AI kullanılamıyor")
            return None
    
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
