# ⚙️ Configuration Guide

## 📋 Overview

This document explains all configuration options for Stash PR Agent.

---

## 📁 Configuration Files

### 1. `.env` - Environment Variables
```env
# Stash Configuration
STASH_URL=https://stash.yourcompany.com.tr
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
language: en  # en (English) or tr (Turkish)

# English prompts
en:
  pr_analysis_system_prompt: |
    You are an experienced senior software engineer...
  
  rejection_comment_template: |
    🤖 **AI Code Review - NOT APPROVED**
    ...

# Turkish prompts
tr:
  pr_analysis_system_prompt: |
    Sen deneyimli bir senior software engineer...
  
  rejection_comment_template: |
    🤖 **AI Code Review - ONAYLANMADI**
    ...
```

---

## 🎯 Key Settings

### Confidence Score
```yaml
min_confidence_score: 70  # 0-100
```
- AI rejects PR if score is below this
- **Recommended:** 70-80
- **Low value (50-60):** Fewer rejections
- **High value (80-90):** More selective

### Check Interval
```yaml
check_interval: 300  # seconds
```
- How often to check for PRs
- **Minimum:** 60 seconds
- **Recommended:** 300 seconds (5 minutes)
- **Fast testing:** 60 seconds

### File/Line Limits
```yaml
max_files_changed: 50
max_lines_changed: 1000
```
- Limits for oversized PRs
- If exceeded, follows `auto_approve_oversized` setting

### Auto Approve on AI Failure
```yaml
auto_approve_on_ai_failure: true
```
- **true:** Auto-approve if AI crashes
- **false:** Skip PR if AI crashes
- **Recommended:** true (uninterrupted operation)

### Comment on Reject
```yaml
comment_on_reject: true
```
- **true:** Add comment when rejecting
- **false:** Silent reject
- **Recommended:** true (transparency)

### Mark as Needs Work
```yaml
mark_needs_work_on_reject: true
```
- **true:** Mark PR as "Needs Work"
- **false:** Only add comment
- **Recommended:** true

### Decline on Reject (RISKY!)
```yaml
decline_on_reject: false
```
- **true:** Completely closes (decline) the PR
- **false:** Only marks as needs work
- **Recommended:** false (too aggressive)

### Inline Comments
```yaml
add_inline_comments_on_reject: true
```
- **true:** Add detailed line-by-line comments
- **false:** Only general comment
- **Recommended:** true (more detail)

---

## 🤖 AI Model Selection

### Ollama Models
```yaml
ollama_model: "deepseek-coder:33b"
```

**Available Models:**
- **deepseek-coder:33b** - Most powerful (16GB RAM, slow)
- **deepseek-coder:6.7b** - Balanced (8GB RAM, recommended)
- **llama3.1:8b** - Fast (4GB RAM)
- **codellama:13b** - Code-focused (8GB RAM)

**Model Selection Guide:**
- **Production:** deepseek-coder:6.7b
- **Testing:** llama3.1:8b
- **Powerful:** deepseek-coder:33b
- **Fast:** llama3.1:8b

---

## 🌍 Language Configuration

### Changing Language

**Option 1: Dashboard**
1. Sidebar → Settings
2. Language → Select (🇹🇷 / 🇬🇧)
3. Restart agent

**Option 2: Config File**
```yaml
# config/prompts.yaml
language: en  # or 'tr'
```

### Custom Prompts

Edit `config/prompts.yaml`:
```yaml
en:
  pr_analysis_system_prompt: |
    # Add your custom prompt here
    You are a code review expert...
    
    # Custom evaluation criteria
    Evaluation criteria:
    1. [YOUR CRITERION]
    2. [YOUR CRITERION]
```

---

## 📝 Inline Comment Configuration

### Comment Format
```yaml
en:
  inline_review_system_prompt: |
    COMMENT FORMAT (Must follow this order):
    1. 🎯 ISSUE: Brief summary
    2. 🔍 WHY: Technical explanation
    3. ⚠️ RISK: What could happen
    4. ✅ SOLUTION: How to fix
    5. 📚 REFERENCE: Related documentation
```

### Severity Levels
```yaml
inline_comment_prefix:
  critical: "🔴 **Sardis AI Review - Critical**"
  warning: "⚠️ **Sardis AI Review - Warning**"
  info: "ℹ️ **Sardis AI Review - Info**"
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

### 1. Conservative
```yaml
approval_criteria:
  min_confidence_score: 80
  auto_approve_on_ai_failure: false
  decline_on_reject: false
  mark_needs_work_on_reject: true
```

### 2. Balanced
```yaml
approval_criteria:
  min_confidence_score: 70
  auto_approve_on_ai_failure: true
  decline_on_reject: false
  mark_needs_work_on_reject: true
```

### 3. Aggressive
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

- [User Guide](USER_GUIDE.md) - Usage guide
- [Multi-Language](MULTI_LANGUAGE.md) - Language support
- [Authentication](AUTHENTICATION.md) - Authentication methods
- [Dashboard](DASHBOARD.md) - Dashboard features

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
