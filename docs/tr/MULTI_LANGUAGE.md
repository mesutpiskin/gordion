# 🌍 Multi-Language Support - Çoklu Dil Desteği

## 📋 Overview / Genel Bakış

Stash PR Agent artık **Türkçe (tr)** ve **İngilizce (en)** dillerinde AI promptları destekliyor!

The Stash PR Agent now supports AI prompts in **Turkish (tr)** and **English (en)**!

---

## 🎯 Features / Özellikler

### ✅ Supported Languages / Desteklenen Diller
- 🇹🇷 **Türkçe (Turkish)** - Default / Varsayılan
- 🇬🇧 **English** - Available / Mevcut

### 📝 What's Translated / Neler Çevrildi

**AI Prompts:**
- ✅ PR Analysis System Prompt
- ✅ Inline Review System Prompt
- ✅ Rejection Comment Template
- ✅ Approval Comment Template
- ✅ Fallback Comment Template
- ✅ Inline Comment Prefixes (Critical/Warning/Info)

---

## 🚀 How to Use / Nasıl Kullanılır

### Method 1: Dashboard (Recommended / Önerilen)

1. Open Dashboard / Dashboard'u Aç:
   ```bash
   ./start_dashboard.sh
   ```

2. Go to Sidebar → Settings / Yan Panel → Ayarlar

3. Select Language / Dil Seç:
   - 🇹🇷 Türkçe
   - 🇬🇧 English

4. Restart Agent / Agent'ı Yeniden Başlat

### Method 2: Config File / Konfigurasyon Dosyası

Edit / Düzenle: `config/prompts.yaml`

```yaml
# Change this line / Bu satırı değiştir:
language: tr   # tr (Türkçe) veya en (English)
```

Then restart agent / Sonra agent'ı yeniden başlat:
```bash
./agent.sh restart
```

---

## 📖 Examples / Örnekler

### Turkish Output / Türkçe Çıktı:
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

### English Output / İngilizce Çıktı:
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

## 🔧 Configuration Structure / Konfigurasyon Yapısı

### File: `config/prompts.yaml`

```yaml
# Active language
language: tr  # or 'en'

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
```

---

## 🎨 Customization / Özelleştirme

### Adding a New Language / Yeni Dil Eklemek

1. Edit / Düzenle: `config/prompts.yaml`

2. Add new language section / Yeni dil bölümü ekle:

```yaml
# French example / Fransızca örnek
fr:
  pr_analysis_system_prompt: |
    Vous êtes un ingénieur logiciel senior expérimenté...
  
  rejection_comment_template: |
    🤖 **Revue de Code IA - NON APPROUVÉ**
    ...
```

3. Update dashboard / Dashboard'u güncelle:

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

### Customizing Existing Prompts / Mevcut Promptları Özelleştirmek

Edit the prompt section in `config/prompts.yaml`:

```yaml
tr:
  pr_analysis_system_prompt: |
    # Add your custom Turkish prompt here
    # Buraya özel Türkçe promptunuzu ekleyin
    
    Sen bir [CUSTOM ROLE]...
    
    Değerlendirme kriterleri:
    1. [CUSTOM CRITERION]
    2. [CUSTOM CRITERION]
    ...
```

---

## 💡 Best Practices / En İyi Uygulamalar

### For Turkish Teams / Türk Ekipler İçin:
- ✅ Keep `language: tr` (default)
- ✅ AI will respond in Turkish
- ✅ All comments will be in Turkish
- ✅ Better cultural context for Turkish developers

### For International Teams / Uluslararası Ekipler İçin:
- ✅ Set `language: en`
- ✅ AI will respond in English
- ✅ Standard international terminology
- ✅ Better for global collaboration

### For Mixed Teams / Karışık Ekipler İçin:
- 💡 Choose team's primary language
- 💡 Can switch anytime from dashboard
- 💡 Each user can use their own instance with their preferred language

---

## 🔍 Language-Specific Features / Dile Özel Özellikler

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

## 🐛 Troubleshooting / Sorun Giderme

### Language not changing / Dil değişmiyor:

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

### Dashboard shows wrong language / Dashboard yanlış dil gösteriyor:

1. Clear browser cache
2. Refresh dashboard
3. Check file permissions:
   ```bash
   ls -la config/prompts.yaml
   ```

### AI still responds in wrong language / AI hala yanlış dilde cevaplıyor:

- Agent needs restart after language change
- Check if `language:` is at root level in YAML
- Verify YAML syntax (indentation matters!)

---

## 📊 Dashboard Language Indicator / Dashboard Dil Göstergesi

Dashboard'da aktif dil gösterilir:

```
⚙️ Settings
─────────────
🌍 Language: 🇹🇷 Türkçe   [✓]
           🇬🇧 English   [ ]
```

---

## 🎯 Language Detection / Dil Tespiti

Agent automatically:
1. Reads `config/prompts.yaml`
2. Loads `language` setting (default: `tr`)
3. Loads language-specific prompts
4. Falls back to Turkish if language not found
5. Logs active language on startup

Log output:
```
INFO - Ollama agent initialized with language: tr
```

---

## 🚀 Quick Switch / Hızlı Geçiş

### From Dashboard / Dashboard'dan:
1. Sidebar → 🌍 Language
2. Select language
3. Click "↻ Restart"

### From Terminal / Terminal'den:
```bash
# Switch to English
sed -i '' 's/language: tr/language: en/' config/prompts.yaml
./agent.sh restart

# Switch to Turkish
sed -i '' 's/language: en/language: tr/' config/prompts.yaml
./agent.sh restart
```

---

## 📚 Related Documentation / İlgili Dokümantasyon

- [Prompts Configuration](PROMPTS_CONFIG.md) - Prompt yapılandırması
- [User Guide](USER_GUIDE.md) - Kullanım kılavuzu
- [Dashboard Guide](DASHBOARD.md) - Dashboard rehberi

---

## 🎉 Summary / Özet

**Turkish (Türkçe):**
- ✅ Türkçe default dil
- ✅ Dashboard'dan kolayca değiştirilebilir
- ✅ Tüm AI yanıtları Türkçe
- ✅ Özelleştirilebilir promptlar

**English:**
- ✅ Full English support
- ✅ Easy switching from dashboard
- ✅ All AI responses in English
- ✅ Customizable prompts

---

**Need help? / Yardıma mı ihtiyacınız var?**
- Check logs: `tail -f logs/agent.log`
- Open issue on GitHub
- Contact your team lead
