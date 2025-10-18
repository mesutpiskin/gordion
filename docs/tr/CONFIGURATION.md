# ⚙️ Configuration Guide - Yapılandırma Kılavuzu

## 📋 Overview / Genel Bakış

Bu dokümanda Stash PR Agent'ın tüm yapılandırma seçenekleri açıklanmaktadır.

---

## 📁 Configuration Files / Yapılandırma Dosyaları

### 1. `.env` - Environment Variables
```env
# Stash Configuration
STASH_URL=https://stash.company.com.tr
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=YOUR_PASSWORD
# or use token:
# STASH_TOKEN=your_token_here

# AI Provider
AI_PROVIDER=ollama  # ollama or openai

# Ollama Settings
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:33b

# Agent Settings
CHECK_INTERVAL=300  # seconds
DRY_RUN=false
RUN_MODE=continuous  # or 'once'
LOG_LEVEL=INFO
```

### 2. `config/config.yaml` - Main Configuration
```yaml
# Check interval (seconds)
check_interval: 300

# Approval criteria
approval_criteria:
  min_confidence_score: 70
  max_files_changed: 50
  max_lines_changed: 1000
  
  auto_approve_on_ai_failure: true
  auto_approve_oversized: true
  
  comment_on_reject: true
  mark_needs_work_on_reject: true
  decline_on_reject: false
  add_inline_comments_on_reject: true

# AI Model
ai:
  ollama_model: "deepseek-coder:33b"
  temperature: 0.3
  max_tokens: 2000

# Logging
logging:
  level: "INFO"
  file: "logs/agent.log"
  console: true
```

### 3. `config/prompts.yaml` - AI Prompts (Multi-Language)
```yaml
# Active language
language: tr  # tr (Turkish) or en (English)

# Turkish prompts
tr:
  pr_analysis_system_prompt: |
    Sen deneyimli bir senior software engineer...
  
  rejection_comment_template: |
    🤖 **AI Code Review - ONAYLANMADI**
    ...

# English prompts
en:
  pr_analysis_system_prompt: |
    You are an experienced senior software engineer...
  
  rejection_comment_template: |
    🤖 **AI Code Review - NOT APPROVED**
    ...
```

---

## 🎯 Key Settings / Önemli Ayarlar

### Confidence Score (Güven Skoru)
```yaml
min_confidence_score: 70  # 0-100
```
- AI bu skorun altındaysa PR'ı reddeder
- **Önerilen:** 70-80 arası
- **Düşük değer (50-60):** Daha az reddetme
- **Yüksek değer (80-90):** Daha seçici

### Check Interval (Kontrol Aralığı)
```yaml
check_interval: 300  # seconds
```
- PR'ları ne sıklıkla kontrol eder
- **Minimum:** 60 saniye
- **Önerilen:** 300 saniye (5 dakika)
- **Hızlı test:** 60 saniye

### File/Line Limits (Dosya/Satır Limitleri)
```yaml
max_files_changed: 50
max_lines_changed: 1000
```
- Çok büyük PR'lar için limitler
- Aşılırsa `auto_approve_oversized` ayarına göre davranır

### Auto Approve on AI Failure
```yaml
auto_approve_on_ai_failure: true
```
- **true:** AI çökmesi durumunda otomatik onay
- **false:** AI çökmesi durumunda PR'ı atla
- **Önerilen:** true (kesintisiz çalışma)

### Comment on Reject
```yaml
comment_on_reject: true
```
- **true:** Reddettiğinde PR'a yorum ekler
- **false:** Sessizce reddeder
- **Önerilen:** true (şeffaflık)

### Mark as Needs Work
```yaml
mark_needs_work_on_reject: true
```
- **true:** PR'ı "Needs Work" olarak işaretler
- **false:** Sadece yorum yapar
- **Önerilen:** true

### Decline on Reject (RİSKLİ!)
```yaml
decline_on_reject: false
```
- **true:** PR'ı tamamen kapatır (decline)
- **false:** Sadece needs work işaretler
- **Önerilen:** false (çok agresif)

### Inline Comments
```yaml
add_inline_comments_on_reject: true
```
- **true:** Kod satırlarına detaylı yorum ekler
- **false:** Sadece genel yorum
- **Önerilen:** true (daha fazla detay)

---

## 🤖 AI Model Selection

### Ollama Models
```yaml
ollama_model: "deepseek-coder:33b"
```

**Available Models:**
- **deepseek-coder:33b** - En güçlü (16GB RAM, yavaş)
- **deepseek-coder:6.7b** - Dengeli (8GB RAM, önerilen)
- **llama3.1:8b** - Hızlı (4GB RAM)
- **codellama:13b** - Kod odaklı (8GB RAM)

**Model Selection Guide:**
- **Production:** deepseek-coder:6.7b
- **Testing:** llama3.1:8b
- **Powerful:** deepseek-coder:33b
- **Fast:** llama3.1:8b

---

## 🌍 Language Configuration

### Changing Language / Dil Değiştirme

**Option 1: Dashboard**
1. Sidebar → Settings
2. Language → Select (🇹🇷 / 🇬🇧)
3. Restart agent

**Option 2: Config File**
```yaml
# config/prompts.yaml
language: en  # or 'tr'
```

### Custom Prompts / Özel Promptlar

Edit `config/prompts.yaml`:
```yaml
tr:
  pr_analysis_system_prompt: |
    # Add your custom prompt here
    Sen bir kod review uzmanısın...
    
    # Custom evaluation criteria
    Değerlendirme kriterleri:
    1. [YOUR CRITERION]
    2. [YOUR CRITERION]
```

---

## 📝 Inline Comment Configuration

### Comment Format
```yaml
tr:
  inline_review_system_prompt: |
    YORUM FORMATI (Mutlaka şu sırayla):
    1. 🎯 SORUN: Kısa özet
    2. 🔍 NEDEN: Teknik açıklama
    3. ⚠️ RİSK: Ne olabilir
    4. ✅ ÇÖZÜM: Nasıl düzeltilir
    5. 📚 REFERANS: İlgili doküman
```

### Severity Levels
```yaml
inline_comment_prefix:
  critical: "🔴 **Sardis AI Review - Kritik**"
  warning: "⚠️ **Sardis AI Review - Uyarı**"
  info: "ℹ️ **Sardis AI Review - Bilgi**"
```

---

## 🔒 Authentication Configuration

### Token-Based (Recommended)
```env
STASH_TOKEN=your_personal_access_token
STASH_USERNAME=YOUR_USERNAME  # optional
```

**Advantages:**
- ✅ More secure
- ✅ Can be revoked
- ✅ Granular permissions
- ✅ No password exposure

**How to create:**
1. Stash → Settings → Personal Access Tokens
2. Create token with "Repository read/write" permission
3. Copy token to `.env`

### Password-Based (Legacy)
```env
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=YOUR_PASSWORD
```

**When to use:**
- Stash doesn't support tokens
- Testing/development only
- Not recommended for production

---

## 📊 Dashboard Configuration

Dashboard reads from:
- `config/config.yaml` - Main settings
- `config/prompts.yaml` - Language/prompts
- `.env` - Credentials (not shown in UI)

**Editable from Dashboard:**
- ✅ Language
- ✅ AI Model
- ✅ Check Interval
- ✅ Min Confidence Score

**Not Editable from Dashboard:**
- ❌ Credentials (security)
- ❌ Advanced settings
- ❌ Custom prompts (use file editor)

---

## 🎯 Common Configurations

### 1. Conservative (Güvenli)
```yaml
approval_criteria:
  min_confidence_score: 80
  auto_approve_on_ai_failure: false
  decline_on_reject: false
  mark_needs_work_on_reject: true
```

### 2. Balanced (Dengeli)
```yaml
approval_criteria:
  min_confidence_score: 70
  auto_approve_on_ai_failure: true
  decline_on_reject: false
  mark_needs_work_on_reject: true
```

### 3. Aggressive (Agresif)
```yaml
approval_criteria:
  min_confidence_score: 60
  auto_approve_on_ai_failure: true
  decline_on_reject: true
  mark_needs_work_on_reject: false
```

---

## 🐛 Troubleshooting

### Config not loading
```bash
# Check YAML syntax
cat config/config.yaml | head -20

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

### Language not changing
```bash
# Check prompts.yaml
grep "language:" config/prompts.yaml

# Restart agent
./agent.sh restart
```

### Dashboard settings not saving
```bash
# Check file permissions
ls -la config/

# Make writable
chmod 644 config/config.yaml config/prompts.yaml
```

---

## 📚 Related Documentation

- [User Guide](USER_GUIDE.md) - Kullanım kılavuzu
- [Multi-Language](MULTI_LANGUAGE.md) - Dil desteği
- [Authentication](AUTHENTICATION.md) - Kimlik doğrulama
- [Dashboard](DASHBOARD.md) - Dashboard özellikleri

---

## 💡 Best Practices

1. **Start Conservative:** Begin with `min_confidence_score: 80`
2. **Monitor First:** Use `DRY_RUN=true` to test
3. **Enable Comments:** Keep `comment_on_reject: true`
4. **Use Tokens:** Prefer token-based auth
5. **Keep Prompts Updated:** Review and improve prompts regularly
6. **Backup Config:** Keep a copy of your custom configurations

---

**Need help? Check logs:**
```bash
tail -f logs/agent.log
```
