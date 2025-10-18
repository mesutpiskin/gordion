# 🎨 Stash PR Agent - Kullanım Kılavuzu

## 📋 İçindekiler
1. [Kurulum](#kurulum)
2. [Dashboard Kullanımı](#dashboard-kullanımı)
3. [Temel İşlemler](#temel-işlemler)
4. [Ayarlar](#ayarlar)
5. [Sorun Giderme](#sorun-giderme)

---

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Git
- Ollama (AI modeli için)

### 2. Projeyi İndirin
```bash
git clone <repository-url>
cd stash-agent
```

### 3. Ortam Dosyasını Oluşturun
```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin
nano .env
```

**Doldurmanız gerekenler:**
```properties
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=KULLANICI_ADINIZ
STASH_PASSWORD=ŞIFRENIZ
OLLAMA_MODEL=deepseek-coder:33b
```

### 4. Ollama'yı Kurun
```bash
# macOS için
brew install ollama

# Ollama'yı başlatın
ollama serve &

# AI modelini indirin (ilk seferinde 15-20GB indirir)
ollama pull deepseek-coder:33b

# Daha küçük model isterseniz (hızlı):
ollama pull deepseek-coder:6.7b
```

### 5. Dashboard'u Başlatın
```bash
./start_dashboard.sh
```

✅ Tarayıcınızda otomatik açılacak: `http://localhost:8501`

---

## 🎨 Dashboard Kullanımı

### Ana Ekran

```
┌─────────────────────────────────────────┐
│   🤖 Gordion PR Agent Dashboard          │
├─────────────────────────────────────────┤
│                                         │
│  📊 Overview  📋 PRs  📈 Analytics     │
│                                         │
│  Today's PRs: 5                         │
│  Approved: 4    Rejected: 1            │
│                                         │
│  [Son 24 saat grafik]                  │
└─────────────────────────────────────────┘
```

### Yan Panel (Sol Taraf)

#### ⚙️ Agent Control
- **● Running / ○ Stopped**: Agent durumu
- **▶️ Start**: Agent'ı başlatır
- **⏹️ Stop**: Agent'ı durdurur
- **↻ Restart**: Agent'ı yeniden başlatır

#### 🔧 Settings
- **AI Model**: Kullanılacak AI modeli
  - `deepseek-coder:33b` - En güçlü (yavaş)
  - `deepseek-coder:6.7b` - Dengeli (önerilen)
  - `llama3.1:8b` - Hızlı
  
- **Check Interval**: PR kontrolü sıklığı (saniye)
  - Varsayılan: 300s (5 dakika)
  - Minimum: 60s
  
- **Min Confidence Score**: Otomatik onay eşiği
  - AI bu skorun altındaysa reddet
  - Varsayılan: 70%

#### 🗑️ Actions
- **Clear History**: Tüm PR geçmişini sil

---

## 📊 Sekmeler

### 1. 📊 Overview (Genel Bakış)
**Günlük İstatistikler:**
- Today's PRs: Bugün işlenen PR sayısı
- Approved: Onaylanan PR'lar
- Rejected: Reddedilen PR'lar
- Avg Confidence: Ortalama güven skoru

**Haftalık Özet:**
- Total PRs: Toplam işlenen PR
- Files Changed: Değişen dosya sayısı
- Lines Added/Deleted: Eklenen/silinen satırlar

**Grafik:** Son 7 günün günlük PR trendi

### 2. 📋 Recent PRs (Son PR'lar)
**Tablo Görünümü:**
- PR ID, Proje, Repo
- Başlık, Yazar
- Durum (✅ Approved, ❌ Rejected, ⚠️ Needs Work)
- Güven skoru (progress bar)
- Dosya sayısı, Zaman

**Detaylı Görünüm:**
- PR seçerek detaylarını görebilirsiniz
- AI'ın reasoning'ini (karar nedenini) okuyabilirsiniz
- Concern'leri (endişeleri) görebilirsiniz

### 3. 📈 Analytics (Analitik)
**Zaman Aralığı Seçimi:**
- Last 7 Days
- Last 30 Days
- All Time

**Görselleştirmeler:**
- PR Status Distribution (Pasta grafik)
  - Approved/Rejected/Needs Work dağılımı
- Approval Trends (Çizgi grafik)
  - Zaman içinde onay trendi
- İstatistikler:
  - Total PRs Processed
  - Approval Rate (Onay oranı)
  - Average Confidence

### 4. 📝 Logs (Loglar)
**Live Log Viewer:**
- Son N satırı gösterir (50-500 arası)
- 🔄 Refresh: Manuel yenileme
- Auto-refresh: 5 saniyede bir otomatik yenileme

**Log Renkleri:**
- 🟢 INFO: Normal bilgi
- 🟡 WARNING: Uyarı
- 🔴 ERROR: Hata

---

## 🎮 Temel İşlemler

### Agent'ı Başlatmak
1. Dashboard'u açın: `./start_dashboard.sh`
2. Sol panelde **▶️ Start** butonuna tıklayın
3. Agent arka planda çalışmaya başlar
4. Durum: **● Running** olur

### Agent'ı Durdurmak
1. Sol panelde **⏹️ Stop** butonuna tıklayın
2. Agent duracaktır
3. Durum: **○ Stopped** olur

### Model Değiştirmek
1. Sol panelde **Settings** bölümüne gidin
2. **AI Model** dropdown'ından model seçin
3. Otomatik kaydedilir
4. Agent'ı restart edin: **↻ Restart**

### PR Geçmişini Görmek
1. **📋 Recent PRs** sekmesine gidin
2. Tabloda tüm PR'ları görürsünüz
3. PR seçerek detaylarına bakabilirsiniz

### İstatistikleri Görmek
1. **📈 Analytics** sekmesine gidin
2. Zaman aralığı seçin
3. Grafikleri ve metrikleri inceleyin

### Logları Takip Etmek
1. **📝 Logs** sekmesine gidin
2. **Auto-refresh** checkbox'ını işaretleyin
3. Gerçek zamanlı log akışını izleyin

---

## ⚙️ Ayarlar

### config/config.yaml

```yaml
# Check interval (saniye)
check_interval: 300

# PR Onay Kriterleri
approval_criteria:
  min_confidence_score: 70        # AI güven skoru (0-100)
  max_files_changed: 50           # Max dosya sayısı
  max_lines_changed: 1000         # Max satır değişikliği
  
  auto_approve_on_ai_failure: true    # AI hata verirse onay
  auto_approve_oversized: true        # Çok büyük PR'ları onay
  
  comment_on_reject: true             # Reddettiğinde yorum ekle
  mark_needs_work_on_reject: true     # "Needs Work" işaretle
  decline_on_reject: false            # PR'ı decline et (riskli!)
  add_inline_comments_on_reject: true # Satır satır yorum ekle

# AI Modeli
ai:
  ollama_model: "deepseek-coder:33b"
  temperature: 0.3
  max_tokens: 2000
```

### .env Dosyası

```properties
# Stash bilgileri
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=KULLANICI_ADI
STASH_PASSWORD=ŞİFRE

# Ollama ayarları
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:33b

# Agent ayarları
CHECK_INTERVAL=300
DRY_RUN=false
RUN_MODE=continuous
```

---

## 🔧 Sorun Giderme

### Dashboard açılmıyor
```bash
# Paketleri yeniden kur
pip install -r requirements.txt

# Dashboard'u manuel başlat
streamlit run src/dashboard.py
```

### Ollama bağlanamıyor
```bash
# Ollama çalışıyor mu kontrol et
pgrep ollama

# Çalışmıyorsa başlat
ollama serve &

# Modeli kontrol et
ollama list

# Model yoksa indir
ollama pull deepseek-coder:33b
```

### Agent başlamıyor
1. **Logs** sekmesine gidin
2. Hata mesajlarını okuyun
3. Yaygın sorunlar:
   - `.env` dosyası eksik/hatalı
   - Ollama çalışmıyor
   - Model indirilmemiş
   - Stash bağlantı hatası

### Stash'e bağlanamıyor
```bash
# .env dosyasını kontrol et
cat .env | grep STASH

# Stash URL'i test et
curl -u USERNAME:PASSWORD https://stash.yourcompany.com.tr/rest/api/1.0/users
```

### Model çok yavaş
1. Daha küçük model kullanın:
   ```
   OLLAMA_MODEL=deepseek-coder:6.7b
   ```

2. veya
   ```
   OLLAMA_MODEL=llama3.1:8b
   ```

### Database hataları
```bash
# Database'i sıfırla
rm data/pr_history.db

# Dashboard'u yeniden başlat
./start_dashboard.sh
```

---

## 💡 İpuçları

### Performans
- **deepseek-coder:33b**: En iyi analiz, yavaş (16GB RAM)
- **deepseek-coder:6.7b**: Dengeli (8GB RAM)
- **llama3.1:8b**: Hızlı, genel amaçlı (4GB RAM)

### Güvenlik
- `.env` dosyasını **asla** commit etmeyin
- Token kullanmayı tercih edin (şifre yerine)
- `DRY_RUN=true` ile önce test edin

### Kullanım
- İlk başta `min_confidence_score: 80` ile başlayın
- Sonuçları izleyin, gerekirse düşürün
- `comment_on_reject: true` mutlaka aktif olsun
- `decline_on_reject: false` olarak bırakın (riskli)

---

## 🆘 Destek

Sorun mu yaşıyorsunuz?
1. **Logs** sekmesini kontrol edin
2. GitHub Issues'da sorun açın
3. Ekip liderinize ulaşın

---

## 📚 Daha Fazla Bilgi

- [README.md](../README.md) - Genel bilgiler
- [QUICKSTART.md](QUICKSTART.md) - Hızlı başlangıç
- [AUTHENTICATION.md](AUTHENTICATION.md) - Kimlik doğrulama
- [OLLAMA.md](OLLAMA.md) - Ollama kurulumu
- [PROMPTS_CONFIG.md](PROMPTS_CONFIG.md) - Prompt ayarları

---

**🎉 İyi kullanımlar!**
