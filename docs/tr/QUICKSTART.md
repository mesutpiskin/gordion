# Hızlı Başlangıç Rehberi

## 1. Kurulum

```bash
cd /Users/YOURUSER/Desktop/stash-agent
./setup.sh
```

## 2. Konfigürasyon

### .env Dosyasını Düzenleyin

```bash
nano .env
```

Aşağıdaki değerleri kendi bilgilerinizle değiştirin:

```env
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=your_username
STASH_PASSWORD=your_password
OPENAI_API_KEY=your_openai_api_key
```

### Kimlik Doğrulama (Authentication)

**Önemli Not:** YourCompany Stash (eski Bitbucket Server versiyonu) Personal Access Token desteklemiyor. Bu nedenle **Basic Authentication** (kullanıcı adı + şifre) kullanılıyor.

- `STASH_USERNAME`: Stash kullanıcı adınız
- `STASH_PASSWORD`: Stash şifreniz

**Güvenlik Notu:** 
- Şifrenizi `.env` dosyasında saklayın
- `.env` dosyası asla git'e commit edilmez (`.gitignore`'da)
- Production sunucusunda dosya izinlerini `chmod 600 .env` ile sınırlayın

## 3. Test

### Bağlantı Testi
```bash
python3 tests/test_connection.py
```

Başarılı olursa, Stash'e bağlanabildiğinizi ve assign edilmiş PR'ları görebileceğinizi gösterir.

### AI Agent Testi
```bash
python3 tests/test_ai.py
```

OpenAI API'nin çalıştığını doğrular.

## 4. Çalıştırma

### Ön Plan (Test için)
```bash
python3 src/main.py
```

CTRL+C ile durdurun.

### Arka Plan (Production)

#### Yöntem 1: agent.sh scripti ile
```bash
# Başlat
./agent.sh start

# Durumu kontrol et
./agent.sh status

# Logları izle
./agent.sh logs

# Durdur
./agent.sh stop

# Yeniden başlat
./agent.sh restart
```

#### Yöntem 2: nohup ile
```bash
nohup python3 src/main.py > logs/agent.log 2>&1 &
echo $! > logs/agent.pid
```

Durdurmak için:
```bash
kill $(cat logs/agent.pid)
```

#### Yöntem 3: screen ile
```bash
screen -S stash-agent
python3 src/main.py

# CTRL+A+D ile detach
# Geri bağlanmak için:
screen -r stash-agent
```

## 5. macOS'ta Otomatik Başlatma (launchd)

```bash
# plist dosyasını kopyala
cp com.yourcompany.stash-agent.plist ~/Library/LaunchAgents/

# plist dosyasını düzenle ve yolları düzelt
nano ~/Library/LaunchAgents/com.yourcompany.stash-agent.plist

# Servisi yükle
launchctl load ~/Library/LaunchAgents/com.yourcompany.stash-agent.plist

# Servisi başlat
launchctl start com.yourcompany.stash-agent

# Durumu kontrol et
launchctl list | grep stash-agent

# Logları kontrol et
tail -f logs/launchd.log
```

### Servisi Durdurma/Kaldırma
```bash
launchctl stop com.yourcompany.stash-agent
launchctl unload ~/Library/LaunchAgents/com.yourcompany.stash-agent.plist
```

## 6. Ayarları Özelleştirme

`config/config.yaml` dosyasını düzenleyin:

```yaml
# Kontrol aralığı (saniye)
check_interval: 300  # 5 dakika

# Dry run modu (test için)
dry_run: false

# Onay kriterleri
approval_criteria:
  min_confidence_score: 70  # AI güven skoru
  max_files_changed: 50     # Max dosya sayısı
  max_lines_changed: 1000   # Max satır değişikliği
```

## 7. Logları İzleme

```bash
# Gerçek zamanlı log takibi
tail -f logs/agent.log

# Son 100 satır
tail -n 100 logs/agent.log

# Sadece ERROR logları
grep ERROR logs/agent.log

# Sadece approved PR'lar
grep "approved PR" logs/agent.log
```

## 8. Sorun Giderme

### "Missing Stash configuration" Hatası
- `.env` dosyasının var olduğundan emin olun
- `.env` dosyasındaki değerlerin doğru olduğunu kontrol edin

### "Failed to fetch pull requests" Hatası
- Stash URL'inin doğru olduğunu kontrol edin
- Personal Access Token'ın geçerli olduğunu kontrol edin
- Token'ın gerekli izinlere sahip olduğunu kontrol edin

### "AI analysis failed" Hatası
- OpenAI API key'in geçerli olduğunu kontrol edin
- İnternet bağlantınızı kontrol edin
- OpenAI hesabınızda kredi olduğunu kontrol edin

### Agent Çalışmıyor
```bash
# Durumu kontrol et
./agent.sh status

# Logları kontrol et
./agent.sh logs

# Yeniden başlat
./agent.sh restart
```

## 9. Güvenlik Notları

- ⚠️ `.env` dosyasını asla git'e commit etmeyin
- ⚠️ Token'ları güvenli bir şekilde saklayın
- ⚠️ Uygulamayı güvenli bir sunucuda çalıştırın
- ✅ Düzenli olarak token'ları yenileyin
- ✅ Gereksiz izinleri kaldırın

## 10. Yararlı Komutlar

```bash
# Tüm Python süreçlerini göster
ps aux | grep python

# Agent'ı manuel durdur
pkill -f "stash-agent"

# Disk kullanımını kontrol et
du -sh logs/

# Eski logları temizle
find logs/ -name "*.log" -mtime +30 -delete
```

## Destek

Sorun yaşarsanız:
1. Logları kontrol edin
2. Test scriptlerini çalıştırın
3. Konfigürasyonu kontrol edin
