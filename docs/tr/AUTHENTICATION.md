# 🔐 Authentication Methods

Stash Agent, iki farklı authentication yöntemi destekler:

## 1️⃣ Personal Access Token (Önerilen) ⭐

### Avantajları:
- ✅ **Daha güvenli** - Şifre yerine token
- ✅ **Revoke edilebilir** - Token'ı iptal edebilirsin
- ✅ **Scope kontrolü** - Sadece gerekli izinler
- ✅ **Süre sınırı** - Token expiration ayarlanabilir
- ✅ **Modern** - Yeni Stash/Bitbucket versiyonlarında desteklenir

### Kurulum:

#### Adım 1: Token Oluştur

**Stash/Bitbucket'ta:**
1. Settings → Personal Access Tokens
2. "Create a token" tıkla
3. Token adı ver (örn: "PR Auto-Approve Agent")
4. Permissions seç:
   - **REPO_READ** - Repository okuma
   - **REPO_WRITE** - PR onaylama
5. "Create" tıkla
6. Token'ı kopyala (bir daha gösterilmez!)

#### Adım 2: .env Dosyasını Güncelle

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Token'ınız
STASH_USERNAME=YOURUSER  # Opsiyonel, log'larda görünür
```

**Not:** `STASH_TOKEN` varsa, `STASH_PASSWORD` kullanılmaz.

#### Adım 3: Test Et

```bash
python3 tests/test_connection.py
```

Beklenen çıktı:
```
Testing connection to: https://stash.yourcompany.com.tr
Using Personal Access Token authentication
Username: YOURUSER
✅ Success! Found X assigned PR(s)
```

---

## 2️⃣ Username + Password (Legacy)

### Ne Zaman Kullanılır:
- ❌ Eski Stash versiyonları (Personal Access Token desteği yok)
- ❌ Token oluşturamıyorsanız
- ⚠️ Güvenlik daha düşük

### Kurulum:

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=YOURUSER
STASH_PASSWORD=your_password_here
```

**Not:** `STASH_TOKEN` yoksa, username/password kullanılır.

---

## 🔄 Geçiş (Password → Token)

### Adım 1: Token Oluştur
Yukarıdaki "Personal Access Token" bölümüne bak.

### Adım 2: .env Güncelle

```bash
# Önce (Password)
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=YOURUSER
STASH_PASSWORD=YOUR_PASSWORD

# Sonra (Token) ✅
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGc...
STASH_USERNAME=YOURUSER  # Opsiyonel
# STASH_PASSWORD=...  # Artık gerekli değil, silebilir veya comment yapabilirsin
```

### Adım 3: Test

```bash
python3 tests/test_connection.py
```

### Adım 4: Eski Password'ü Sil

Token çalıştığını doğruladıktan sonra:

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGc...
STASH_USERNAME=YOURUSER
# STASH_PASSWORD removed for security ✅
```

---

## 🆚 Karşılaştırma

| Özellik | Personal Access Token | Username + Password |
|---------|----------------------|---------------------|
| **Güvenlik** | ⭐⭐⭐⭐⭐ Çok yüksek | ⭐⭐ Düşük |
| **Revoke** | ✅ Kolayca iptal edilebilir | ❌ Şifre değiştirmek gerekir |
| **Scope** | ✅ Sınırlı izinler | ❌ Tüm izinler |
| **Expiration** | ✅ Süre sınırı ayarlanabilir | ❌ Süresiz |
| **Audit** | ✅ Token kullanım logları | ⚠️ Şifre kullanım logları |
| **Desteklenen Versiyon** | Stash 5.5+ | Tüm versiyonlar |
| **Önerilen** | ✅ **Evet** | ❌ Hayır (sadece eski versiyonlar) |

---

## 🔧 Troubleshooting

### Problem: "401 Unauthorized" (Token ile)

**Nedeni:**
- Token expired
- Token revoke edilmiş
- Yetersiz permission

**Çözüm:**
```bash
# Yeni token oluştur
# Stash → Settings → Personal Access Tokens → Create

# .env'de güncelle
STASH_TOKEN=new_token_here

# Test et
python3 tests/test_connection.py
```

---

### Problem: "403 Forbidden" (Token ile)

**Nedeni:**
- Token'ın gerekli permission'ları yok

**Çözüm:**
```bash
# Token'ı sil ve yeni token oluştur
# Permissions:
#   - REPO_READ ✅
#   - REPO_WRITE ✅
```

---

### Problem: "Token çalışmıyor, Password ile çalışıyor"

**Nedeni:**
- Eski Stash versiyonu (< 5.5)
- Personal Access Token feature devre dışı

**Çözüm:**
```bash
# Password ile devam et
STASH_USERNAME=YOURUSER
STASH_PASSWORD=your_password

# Token'ı comment yap
# STASH_TOKEN=...
```

---

### Problem: "Hangi auth method kullanıldığını nasıl anlarım?"

**Çözüm:**
```bash
# Log'lara bak
python3 src/main.py

# Çıktı:
# Using Personal Access Token authentication ✅
# veya
# Using Basic Authentication for user: YOURUSER
```

---

## 💡 Best Practices

### 1. Token Kullan (Mümkünse)
```bash
STASH_TOKEN=eyJhbGc...  # ✅ Önerilen
```

### 2. Token Permission'larını Sınırla
Sadece gerekli izinleri ver:
- ✅ REPO_READ
- ✅ REPO_WRITE
- ❌ ADMIN (gerekli değil)

### 3. Token Expiration Ayarla
- 90 gün veya 1 yıl
- Otomatik renewal sistemi kur

### 4. Token'ı Güvenli Tut
```bash
# .env dosyası git'e commit edilmemeli
echo ".env" >> .gitignore

# Token'ı paylaşma
# Token'ı log'lara yazma
```

### 5. Rotate Token (Düzenli Değiştir)
```bash
# Her 3-6 ayda bir yeni token oluştur
# Eski token'ı revoke et
# .env'de güncelle
```

---

## 📚 Örnekler

### Örnek 1: Token ile Production

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
STASH_USERNAME=YOURUSER

AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

### Örnek 2: Password ile Legacy

```bash
# .env
STASH_URL=https://stash-old.yourcompany.com.tr
STASH_USERNAME=YOURUSER
STASH_PASSWORD=MySecretPassword123

AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

### Örnek 3: Her İkisi de Var (Token Öncelikli)

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGc...  # ✅ Bu kullanılır
STASH_USERNAME=YOURUSER
STASH_PASSWORD=backup_password  # Token fail olursa değil, token varsa ignore edilir
```

**Not:** Token varsa, password ignore edilir.

---

## 🎓 Sonuç

**Önerilen kurulum:**

```bash
# Modern Stash (5.5+) için
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=your_token_here  # ⭐ Önerilen
STASH_USERNAME=YOURUSER

# Legacy Stash için
STASH_URL=https://stash-old.yourcompany.com.tr
STASH_USERNAME=YOURUSER
STASH_PASSWORD=your_password
```

**Token oluştur:** Settings → Personal Access Tokens → Create  
**Test et:** `python3 tests/test_connection.py`  
**Çalıştır:** `python3 src/main.py`

**🔐 Güvenli ve kolay authentication!**
