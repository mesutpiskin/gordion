# 🔐 Authentication Methods

Stash Agent supports two authentication methods:

## 1️⃣ Personal Access Token (Recommended) ⭐

### Advantages:
- ✅ **More secure** - Token instead of password
- ✅ **Revocable** - Can revoke the token
- ✅ **Scope control** - Only necessary permissions
- ✅ **Expiration** - Can set token expiration
- ✅ **Modern** - Supported in newer Stash/Bitbucket versions

### Setup:

#### Step 1: Create Token

**In Stash/Bitbucket:**
1. Settings → Personal Access Tokens
2. Click "Create a token"
3. Name the token (e.g., "PR Auto-Approve Agent")
4. Select permissions:
   - **REPO_READ** - Repository read
   - **REPO_WRITE** - PR approval
5. Click "Create"
6. Copy the token (won't be shown again!)

#### Step 2: Update .env File

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Your token
STASH_USERNAME=YOUR_USERNAME  # Optional, shows in logs
```

**Note:** If `STASH_TOKEN` exists, `STASH_PASSWORD` is not used.

#### Step 3: Test

```bash
python3 tests/test_connection.py
```

Expected output:
```
Testing connection to: https://stash.yourcompany.com.tr
Using Personal Access Token authentication
Username: YOUR_USERNAME
✅ Success! Found X assigned PR(s)
```

---

## 2️⃣ Username + Password (Legacy)

### When to Use:
- ❌ Old Stash versions (no Personal Access Token support)
- ❌ Cannot create token
- ⚠️ Lower security

### Setup:

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=your_password_here
```

**Note:** If `STASH_TOKEN` doesn't exist, username/password is used.

---

## 🔄 Migration (Password → Token)

### Step 1: Create Token
See "Personal Access Token" section above.

### Step 2: Update .env

```bash
# Before (Password)
STASH_URL=https://stash.yourcompany.com.tr
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=YOUR_PASSWORD

# After (Token) ✅
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGc...
STASH_USERNAME=YOUR_USERNAME  # Optional
# STASH_PASSWORD=...  # No longer needed, can delete or comment out
```

### Step 3: Test

```bash
python3 tests/test_connection.py
```

### Step 4: Remove Old Password

After confirming token works:

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGc...
STASH_USERNAME=YOUR_USERNAME
# STASH_PASSWORD removed for security ✅
```

---

## 🆚 Comparison

| Feature | Personal Access Token | Username + Password |
|---------|----------------------|---------------------|
| **Security** | ⭐⭐⭐⭐⭐ Very High | ⭐⭐ Low |
| **Revoke** | ✅ Easy to revoke | ❌ Must change password |
| **Scope** | ✅ Limited permissions | ❌ All permissions |
| **Expiration** | ✅ Configurable expiration | ❌ No expiration |
| **Audit** | ✅ Token usage logs | ⚠️ Password usage logs |
| **Supported Version** | Stash 5.5+ | All versions |
| **Recommended** | ✅ **Yes** | ❌ No (only for old versions) |

---

## 🔧 Troubleshooting

### Problem: "401 Unauthorized" (with Token)

**Cause:**
- Token expired
- Token revoked
- Insufficient permissions

**Solution:**
```bash
# Create new token
# Stash → Settings → Personal Access Tokens → Create

# Update in .env
STASH_TOKEN=new_token_here

# Test
python3 tests/test_connection.py
```

---

### Problem: "403 Forbidden" (with Token)

**Cause:**
- Token doesn't have required permissions

**Solution:**
```bash
# Delete token and create new one
# Permissions:
#   - REPO_READ ✅
#   - REPO_WRITE ✅
```

---

### Problem: "Token doesn't work, Password works"

**Cause:**
- Old Stash version (< 5.5)
- Personal Access Token feature disabled

**Solution:**
```bash
# Continue with password
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=your_password

# Comment out token
# STASH_TOKEN=...
```

---

### Problem: "How do I know which auth method is used?"

**Solution:**
```bash
# Check logs
python3 src/main.py

# Output:
# Using Personal Access Token authentication ✅
# or
# Using Basic Authentication for user: YOUR_USERNAME
```

---

## 💡 Best Practices

### 1. Use Token (If Possible)
```bash
STASH_TOKEN=eyJhbGc...  # ✅ Recommended
```

### 2. Limit Token Permissions
Give only necessary permissions:
- ✅ REPO_READ
- ✅ REPO_WRITE
- ❌ ADMIN (not necessary)

### 3. Set Token Expiration
- 90 days or 1 year
- Set up automatic renewal system

### 4. Keep Token Secure
```bash
# .env file should not be committed to git
echo ".env" >> .gitignore

# Don't share token
# Don't write token to logs
```

### 5. Rotate Token (Regular Changes)
```bash
# Create new token every 3-6 months
# Revoke old token
# Update in .env
```

---

## 📚 Examples

### Example 1: Token for Production

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
STASH_USERNAME=YOUR_USERNAME

AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

### Example 2: Password for Legacy

```bash
# .env
STASH_URL=https://stash-old.yourcompany.com.tr
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=MySecretPassword123

AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

### Example 3: Both Present (Token Takes Priority)

```bash
# .env
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=eyJhbGc...  # ✅ This is used
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=backup_password  # Not used if token exists, token is ignored
```

**Note:** If token exists, password is ignored.

---

## 🎓 Conclusion

**Recommended setup:**

```bash
# For Modern Stash (5.5+)
STASH_URL=https://stash.yourcompany.com.tr
STASH_TOKEN=your_token_here  # ⭐ Recommended
STASH_USERNAME=YOUR_USERNAME

# For Legacy Stash
STASH_URL=https://stash-old.yourcompany.com.tr
STASH_USERNAME=YOUR_USERNAME
STASH_PASSWORD=your_password
```

**Create token:** Settings → Personal Access Tokens → Create  
**Test:** `python3 tests/test_connection.py`  
**Run:** `python3 src/main.py`

**🔐 Secure and easy authentication!**
