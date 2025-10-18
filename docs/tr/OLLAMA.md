# Ollama Entegrasyonu

Bu döküman, Stash Agent'ta **yerel AI** kullanımı için **Ollama** entegrasyonunu açıklar.

## 📖 İçindekiler

1. [Ollama Nedir?](#ollama-nedir)
2. [Neden Ollama?](#neden-ollama)
3. [Kurulum](#kurulum)
4. [Model Seçimi](#model-seçimi)
5. [Kullanım](#kullanım)
6. [OpenAI vs Ollama](#openai-vs-ollama)
7. [Troubleshooting](#troubleshooting)

---

## 🤖 Ollama Nedir?

**Ollama**, açık kaynak AI modellerini (Llama, Mistral, CodeLlama vb.) **yerel bilgisayarınızda** çalıştırmanızı sağlayan bir araçtır.

### Avantajlar:
- ✅ **Ücretsiz** - API ücretleri yok
- ✅ **Gizlilik** - Kodunuz dışarı çıkmaz
- ✅ **Hız** - M4 Pro Max ile çok hızlı
- ✅ **Offline çalışma** - İnternet bağlantısı gerektirmez
- ✅ **Sınırsız kullanım** - Rate limit yok

### Dezavantajlar:
- ❌ RAM kullanımı (4-40GB arası)
- ❌ İlk indirme büyük (4-40GB arası)
- ❌ OpenAI GPT-4 kadar güçlü değil (daha küçük modellerde)

---

## 🎯 Neden Ollama?

### YourCompany Kullanımı İçin İdeal

1. **Maliyet Tasarrufu**
   - OpenAI API ücreti: ~$0.03 / 1K token
   - Ollama: **Ücretsiz** (sadece elektrik)
   - Yüzlerce PR için: **$$$$ tasarruf**

2. **Güvenlik & Compliance**
   - Kodunuz YourCompany dışına çıkmaz
   - GDPR/ISO 27001 uyumlu
   - On-premise deployment

3. **Performans**
   - M4 Pro Max ile **8B model**: ~50 token/s
   - M4 Pro Max ile **70B model**: ~10-20 token/s
   - PR analizi: 10-30 saniye

---

## 🚀 Kurulum

### Otomatik Kurulum (Önerilen)

```bash
./scripts/setup_ollama.sh
```

Bu script:
1. ✅ Ollama'yı yükler (Homebrew ile)
2. ✅ Servisi başlatır
3. ✅ Model seçimi sunar
4. ✅ Modeli indirir
5. ✅ `.env` dosyasını günceller

### Manuel Kurulum

#### 1. Ollama Yükleme

```bash
# Homebrew ile
brew install ollama

# Veya manuel
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Servisi Başlatma

```bash
# Arka planda başlat
ollama serve &

# Veya ön planda (log görmek için)
ollama serve
```

#### 3. Model İndirme

```bash
# Önerilen: Llama 3.1 8B (hızlı, dengeli)
ollama pull llama3.1:8b

# Alternatif: CodeLlama 13B (kod odaklı)
ollama pull codellama:13b

# Alternatif: Mistral 7B (en hızlı)
ollama pull mistral:7b
```

#### 4. .env Yapılandırması

```bash
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

---

## 🎯 Model Seçimi

### M4 Pro Max İçin Önerilen Modeller

| Model | Boyut | RAM | Hız | Kalite | Kullanım |
|-------|-------|-----|-----|--------|----------|
| **llama3.1:8b** | 4.7GB | 8GB | ⚡⚡⚡ | ⭐⭐⭐ | **Önerilen** - Genel amaçlı |
| **mistral:7b** | 4.1GB | 8GB | ⚡⚡⚡⚡ | ⭐⭐ | En hızlı, kompakt |
| **codellama:7b** | 3.8GB | 8GB | ⚡⚡⚡ | ⭐⭐⭐ | Kod için optimize |
| **llama3.1:13b** | 7.4GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐ | Daha iyi kalite |
| **codellama:13b** | 7.3GB | 16GB | ⚡⚡ | ⭐⭐⭐⭐ | Kod için en iyi |
| **llama3.1:70b** | 40GB | 64GB | ⚡ | ⭐⭐⭐⭐⭐ | En güçlü (yavaş) |

### Öneriler

#### Genel Kullanım (Önerilen)
```bash
ollama pull llama3.1:8b
```
- Hızlı ve dengeli
- PR analizinde iyi performans
- 8GB RAM yeterli

#### Kod Odaklı
```bash
ollama pull codellama:13b
```
- Kod review'da daha iyi
- Syntax ve best practice'lere odaklı
- 16GB RAM gerekli

#### En Hızlı
```bash
ollama pull mistral:7b
```
- Çok hızlı response
- Basit PR'lar için yeterli
- 8GB RAM yeterli

#### En Güçlü (M4 Pro Max Max için)
```bash
ollama pull llama3.1:70b
```
- GPT-4 seviyesinde
- Kompleks PR'lar için
- 64GB RAM önerilir
- Yavaş (10-30 token/s)

---

## 🎮 Kullanım

### 1. Test

```bash
# Ollama bağlantısını test et
python3 tests/test_ollama.py
```

Çıktı:
```
✅ Ollama server is running
✅ Model 'llama3.1:8b' is available
⏳ Analyzing with Ollama AI...
✅ Analysis Successful!

Approve: True
Confidence: 85%

Reasoning:
  The PR fixes a critical authentication bug with proper test coverage.
  Code changes are minimal and focused. No security concerns detected.
```

### 2. Dry-Run

```bash
# .env dosyasında
AI_PROVIDER=ollama
DRY_RUN=true
RUN_MODE=once

# Çalıştır
python3 src/main.py
```

### 3. Production

```bash
# .env dosyasında
AI_PROVIDER=ollama
DRY_RUN=false
RUN_MODE=continuous

# Başlat
./agent.sh start

# Logları izle
./agent.sh logs
```

---

## ⚖️ OpenAI vs Ollama

### Karşılaştırma Tablosu

| Özellik | OpenAI (GPT-4) | Ollama (Llama 3.1 8B) | Ollama (Llama 3.1 70B) |
|---------|----------------|----------------------|------------------------|
| **Maliyet** | ~$0.03/1K token | Ücretsiz | Ücretsiz |
| **Gizlilik** | ❌ Dışarı gönderir | ✅ Yerel | ✅ Yerel |
| **Hız** | 1-5 saniye | 10-20 saniye | 30-60 saniye |
| **Kalite** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **RAM** | - | 8GB | 64GB |
| **Offline** | ❌ İnternet gerekli | ✅ Offline çalışır | ✅ Offline çalışır |
| **Rate Limit** | ✅ Var (10K RPM) | ✅ Yok | ✅ Yok |

### Ne Zaman OpenAI?

- ✅ En iyi kalite gerekiyorsa
- ✅ Hız kritikse (1-5 saniye)
- ✅ RAM sınırlıysa
- ✅ Setup yapmak istemiyorsanız

### Ne Zaman Ollama?

- ✅ Maliyet önemliyse (ücretsiz)
- ✅ Gizlilik kritikse (on-premise)
- ✅ Sınırsız kullanım gerekiyorsa
- ✅ Offline çalışma istiyorsanız
- ✅ M4 Pro Max gibi güçlü Mac'iniz varsa

---

## 🔧 Troubleshooting

### Problem: Ollama'ya bağlanamıyor

```
⚠️  Cannot connect to Ollama server
```

**Çözüm:**
```bash
# Servis çalışıyor mu kontrol et
curl http://localhost:11434/api/tags

# Eğer çalışmıyorsa başlat
ollama serve &

# Veya ön planda
ollama serve
```

---

### Problem: Model bulunamıyor

```
⚠️  Model 'llama3.1:8b' not available
```

**Çözüm:**
```bash
# Modeli indir
ollama pull llama3.1:8b

# İndirilen modelleri listele
ollama list
```

---

### Problem: Çok yavaş

```
⏳ Analysis taking more than 60 seconds...
```

**Çözümler:**

1. **Daha küçük model kullan:**
   ```bash
   ollama pull mistral:7b
   # .env: OLLAMA_MODEL=mistral:7b
   ```

2. **Metal acceleration kontrol et:**
   ```bash
   # M4 GPU kullanıldığını doğrula
   ollama run llama3.1:8b "test"
   # Log'da "using metal" görmeli
   ```

3. **RAM yeterli mi kontrol et:**
   ```bash
   # Activity Monitor'de RAM kullanımına bak
   # 8B model: 8GB
   # 13B model: 16GB
   # 70B model: 64GB
   ```

---

### Problem: JSON parse hatası

```
⚠️  Ollama JSON parse hatası
```

**Neden:** Model bazen JSON dışında text ekliyor.

**Çözüm:** Kod zaten otomatik JSON extraction yapıyor. Eğer problem devam ediyorsa:

1. Model değiştir (Llama daha tutarlı)
2. Temperature azalt (0.1 - 0.3 arası)
3. Prompt'u geliştir

---

### Problem: Out of Memory

```
Error: failed to load model: out of memory
```

**Çözüm:**
```bash
# Daha küçük model kullan
ollama pull mistral:7b

# Veya quantized model
ollama pull llama3.1:8b-q4_0  # 4-bit quantized
```

---

### Problem: Agent AI hatası diyor ama fallback mode çalışıyor

```
⚠️  AI analizi başarısız - fallback mode aktif
✅ Auto-approved (AI failure fallback)
```

**Bu normal!** Agent, AI başarısız olsa bile PR'ları approve eder (fallback mode).

**Eğer AI'yi düzeltmek isterseniz:**

1. Test scripti çalıştır: `python3 tests/test_ollama.py`
2. Log'ları incele: `tail -f logs/agent.log`
3. Model değiştir veya Ollama'yı restart et

---

## 🎓 İleri Seviye

### Custom Model Kullanma

```bash
# Kendi modelinizi Modelfile ile oluşturun
cat > Modelfile << 'EOF'
FROM llama3.1:8b

PARAMETER temperature 0.2
PARAMETER num_ctx 4096

SYSTEM """Sen bir YourCompany kod review uzmanısın..."""
EOF

ollama create yourcompany-reviewer -f Modelfile

# .env'de kullan
OLLAMA_MODEL=yourcompany-reviewer
```

### GPU Monitoring

```bash
# Metal performansını izle
sudo powermetrics --samplers gpu_power -i 1000

# Ollama GPU kullanımını gör
ollama ps
```

### Model Quantization

Daha az RAM için quantized modeller:

```bash
# 4-bit quantized (2x daha az RAM)
ollama pull llama3.1:8b-q4_0

# 8-bit quantized (1.5x daha az RAM)
ollama pull llama3.1:8b-q8_0
```

---

## 📊 Performans Metrikleri (M4 Pro Max)

### Llama 3.1 8B
- **Load time:** 2-3 saniye
- **Token/s:** 45-55 token/s
- **PR analizi:** 10-15 saniye
- **RAM:** ~8GB
- **Kalite:** GPT-3.5 seviyesi

### Llama 3.1 70B
- **Load time:** 10-15 saniye
- **Token/s:** 8-12 token/s
- **PR analizi:** 40-60 saniye
- **RAM:** ~50GB
- **Kalite:** GPT-4 seviyesi

### CodeLlama 13B
- **Load time:** 4-5 saniye
- **Token/s:** 30-40 token/s
- **PR analizi:** 15-20 saniye
- **RAM:** ~12GB
- **Kalite:** Kod için optimize

---

## 🔗 Faydalı Linkler

- [Ollama Official Site](https://ollama.com/)
- [Ollama Models](https://ollama.com/library)
- [Llama 3.1 Model Card](https://ollama.com/library/llama3.1)
- [CodeLlama Model Card](https://ollama.com/library/codellama)
- [Ollama API Docs](https://github.com/ollama/ollama/blob/main/docs/api.md)

---

## 💡 Best Practices

1. **İlk Kullanımda Test Edin**
   ```bash
   ./scripts/setup_ollama.sh
   python3 tests/test_ollama.py
   ```

2. **Küçük Başlayın**
   - İlk `llama3.1:8b` ile başlayın
   - Performans yeterliyse bu modeli kullanmaya devam edin
   - Kalite gerekiyorsa `codellama:13b` veya `llama3.1:70b` deneyin

3. **Fallback Mode'u Aktif Tutun**
   ```yaml
   auto_approve_on_ai_failure: true
   ```
   AI başarısız olsa bile agent çalışmaya devam eder

4. **Monitoring Yapın**
   ```bash
   ./agent.sh logs
   tail -f logs/agent.log | grep -i ollama
   ```

5. **Periyodik Restart**
   ```bash
   # Haftada bir Ollama'yı restart edin (memory leak önleme)
   pkill ollama
   ollama serve &
   ```

---

**🎉 Artık YourCompany Stash Agent, tamamen yerel AI ile çalışıyor!**
