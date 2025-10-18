# 🌍 Multi-Language Support

## 📋 Overview

Stash PR Agent now supports AI prompts in **Turkish (tr)** and **English (en)**!

---

## 🎯 Features

### ✅ Supported Languages
- 🇹🇷 **Turkish (Türkçe)** - Default
- 🇬🇧 **English** - Available

### 📝 What's Translated

**AI Prompts:**
- ✅ PR Analysis System Prompt
- ✅ Inline Review System Prompt
- ✅ Rejection Comment Template
- ✅ Approval Comment Template
- ✅ Fallback Comment Template
- ✅ Inline Comment Prefixes (Critical/Warning/Info)

---

## 🚀 How to Use

### Method 1: Dashboard (Recommended)

1. Open Dashboard:
   ```bash
   ./start_dashboard.sh
   ```

2. Go to Sidebar → Settings

3. Select Language:
   - 🇹🇷 Türkçe
   - 🇬🇧 English

4. Restart Agent

### Method 2: Config File

Edit: `config/prompts.yaml`

```yaml
# Change this line:
language: en   # en (English) or tr (Turkish)
```

Then restart agent:
```bash
./agent.sh restart
```

---

## 📖 Examples

### Turkish Output:
```markdown
🤖 **AI Code Review - ONAYLANMADI**

**Güven Skoru:** 65%

**Analiz:**
Line 42: Null pointer riski var. Optional.ofNullable() kullanılmalı.

**Endişeler:**
- Line 42: NullPointerException oluşabilir
- Line 58: SQL injection riski

*Gordion AI Agent tarafından analiz edildi - deepseek-coder:33b*
```

### English Output:
```markdown
🤖 **AI Code Review - NOT APPROVED**

**Confidence Score:** 65%

**Analysis:**
Line 42: Null pointer risk. Should use Optional.ofNullable().

**Concerns:**
- Line 42: Potential NullPointerException
- Line 58: SQL injection risk

*Analyzed by Gordion AI Agent - deepseek-coder:33b*
```

---

## 🔧 Configuration Structure

### File: `config/prompts.yaml`

```yaml
# Active language
language: en  # or 'tr'

# English prompts
en:
  pr_analysis_system_prompt: |
    You are an experienced senior software engineer...
  
  inline_review_system_prompt: |
    You are an experienced code review expert...
  
  rejection_comment_template: |
    🤖 **AI Code Review - NOT APPROVED**
    ...
  
  approval_comment_template: |
    ✅ Auto-approved by Gordion AI Agent
    ...

# Turkish prompts
tr:
  pr_analysis_system_prompt: |
    Sen deneyimli bir senior software engineer...
  
  inline_review_system_prompt: |
    Sen deneyimli bir kod review uzmanısın...
  
  rejection_comment_template: |
    🤖 **AI Code Review - ONAYLANMADI**
    ...
  
  approval_comment_template: |
    ✅ Gordion AI Agent tarafından otomatik onaylandı
    ...
```

---

## 🎨 Customization

### Adding a New Language

1. Edit: `config/prompts.yaml`

2. Add new language section:

```yaml
# French example
fr:
  pr_analysis_system_prompt: |
    Vous êtes un ingénieur logiciel senior expérimenté...
  
  rejection_comment_template: |
    🤖 **Revue de Code IA - NON APPROUVÉ**
    ...
```

3. Update dashboard:

In `src/dashboard.py`, add to language selectbox:
```python
language = st.selectbox(
    "🌍 Language",
    ['tr', 'en', 'fr'],  # Add 'fr'
    format_func=lambda x: {
        'tr': '🇹🇷 Türkçe',
        'en': '🇬🇧 English',
        'fr': '🇫🇷 Français'
    }[x]
)
```

### Customizing Existing Prompts

Edit the prompt section in `config/prompts.yaml`:

```yaml
en:
  pr_analysis_system_prompt: |
    # Add your custom English prompt here
    
    You are a [CUSTOM ROLE]...
    
    Evaluation criteria:
    1. [CUSTOM CRITERION]
    2. [CUSTOM CRITERION]
    ...
```

---

## 💡 Best Practices

### For Turkish Teams:
- ✅ Keep `language: tr` (default)
- ✅ AI will respond in Turkish
- ✅ All comments will be in Turkish
- ✅ Better cultural context for Turkish developers

### For International Teams:
- ✅ Set `language: en`
- ✅ AI will respond in English
- ✅ Standard international terminology
- ✅ Better for global collaboration

### For Mixed Teams:
- 💡 Choose team's primary language
- 💡 Can switch anytime from dashboard
- 💡 Each user can use their own instance with their preferred language

---

## 🔍 Language-Specific Features

### Turkish (tr):
- **Endişeler** section in comments
- **Güven Skoru** in metrics
- **Kritik/Uyarı/Bilgi** severity labels
- Turkish technical terminology

### English (en):
- **Concerns** section in comments
- **Confidence Score** in metrics
- **Critical/Warning/Info** severity labels
- Standard English technical terminology

---

## 🐛 Troubleshooting

### Language not changing:

1. Check `config/prompts.yaml`:
   ```bash
   cat config/prompts.yaml | grep "language:"
   ```

2. Restart agent:
   ```bash
   ./agent.sh restart
   ```

3. Check logs:
   ```bash
   tail -f logs/agent.log | grep "language"
   ```

### Dashboard shows wrong language:

1. Clear browser cache
2. Refresh dashboard
3. Check file permissions:
   ```bash
   ls -la config/prompts.yaml
   ```

### AI still responds in wrong language:

- Agent needs restart after language change
- Check if `language:` is at root level in YAML
- Verify YAML syntax (indentation matters!)

---

## 📊 Dashboard Language Indicator

Dashboard shows active language:

```
⚙️ Settings
─────────────
🌍 Language: 🇹🇷 Türkçe   [ ]
           🇬🇧 English   [✓]
```

---

## 🎯 Language Detection

Agent automatically:
1. Reads `config/prompts.yaml`
2. Loads `language` setting (default: `tr`)
3. Loads language-specific prompts
4. Falls back to Turkish if language not found
5. Logs active language on startup

Log output:
```
INFO - Ollama agent initialized with language: en
```

---

## 🚀 Quick Switch

### From Dashboard:
1. Sidebar → 🌍 Language
2. Select language
3. Click "↻ Restart"

### From Terminal:
```bash
# Switch to English
sed -i '' 's/language: tr/language: en/' config/prompts.yaml
./agent.sh restart

# Switch to Turkish
sed -i '' 's/language: en/language: tr/' config/prompts.yaml
./agent.sh restart
```

---

## 📚 Related Documentation

- [Configuration Guide](CONFIGURATION.md) - Configuration settings
- [User Guide](USER_GUIDE.md) - Usage guide
- [Dashboard Guide](DASHBOARD.md) - Dashboard features

---

## 🎉 Summary

**Turkish (Türkçe):**
- ✅ Turkish is default language
- ✅ Easy switching from dashboard
- ✅ All AI responses in Turkish
- ✅ Customizable prompts

**English:**
- ✅ Full English support
- ✅ Easy switching from dashboard
- ✅ All AI responses in English
- ✅ Customizable prompts

---

**Need help?**
- Check logs: `tail -f logs/agent.log`
- Open issue on GitHub
- Contact your team lead
