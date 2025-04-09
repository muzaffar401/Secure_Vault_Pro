
# 🔐 Secure Vault Pro

**Military-Grade Data Protection using Python & Streamlit**

Secure Vault Pro is an advanced encryption application providing AES-256 encryption and PBKDF2-based key derivation to protect your sensitive data. Built with simplicity and security in mind, it ensures your data is safe—even if the encrypted files are exposed.

---

## 🌟 Features

- **Bank-Level Security**: AES-256 encryption with PBKDF2 key derivation
- **Zero-Knowledge Protocol**: We never store or see your passkeys
- **Military Compliance**: Meets strict security standards
- **User-Friendly Interface**: Simple and intuitive design
- **Data Organization**: Name and categorize your encrypted items
- **Secure Sharing**: Encrypted data can be safely shared

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- `pip` package manager

### Installation

```bash
git clone https://github.com/yourusername/secure-vault-pro.git
cd secure-vault-pro
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run secure_vault.py
```

---

## 🧭 Navigation Guide

### 📊 Dashboard
- Shows your security status and encrypted item count.

### 🔐 Store Data
- Enter your sensitive info
- Create & confirm a strong passkey
- Optionally name the entry
- Copy and store the encrypted output

### 🔓 Retrieve Data
- Paste encrypted data
- Enter your passkey to decrypt and view

### 🗄️ Data Vault
- View and manage all encrypted items
- Click to decrypt or view metadata

---

## 🔒 Security Features

### 🔧 Encryption Process
- AES-128 (via Fernet) in CBC mode
- PBKDF2-HMAC-SHA256 with 100,000 iterations
- Unique 16-byte salt per encryption

### 🔐 Account Protection
- 3 failed attempts = 5-minute lockout
- Master password required for critical operations
- Session-based security controls using Streamlit session state

---

## 💡 Best Practices

### Passkey Creation
- Use 12+ characters
- Combine uppercase, lowercase, numbers, and symbols
- Prefer passphrases like `CorrectHorseBatteryStaple42!`

### Data Storage
- Store encrypted data and passkeys separately
- Keep backups
- Use a password manager for keys

### Sharing Data
- Share data and passkeys via different secure channels
- Use expiration dates when possible

---

## 🛠️ Technical Details

- **Encryption Stack**:
  - `Fernet`: AES-128, CBC mode, PKCS7 padding
  - `PBKDF2`: SHA-256, 100,000 iterations
  - 16-byte random salt for each encryption

- **Data Storage**:
  - Encrypted data in `encrypted_data.json`
  - Encryption key in `secret.key` (auto-generated on first run)

- **Session Management**:
  - Streamlit session state for:
    - Lockout timers
    - Failed attempt tracking
    - Navigation memory

---

## 📜 License

MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit** – for their powerful UI framework
- **Cryptography.io** – for robust encryption libraries
- **Open Source Community** – for inspiration & collaboration

---

## 🎥 Demo Walkthrough

### ✅ Storing Data

1. Navigate to **Store Data**
2. Enter sensitive data (e.g., API keys, passwords)
3. Set a strong passkey (e.g., `Secur3P@sskey2023!`)
4. Name your entry (optional)
5. Click **Encrypt & Store**
6. Copy the encrypted output and store it securely

### 🔓 Retrieving Data

1. Go to **Retrieve Data**
2. Paste encrypted string
3. Enter passkey
4. Click **Decrypt Data**
5. View your original content

### 🗄️ Managing Your Vault

- Navigate to **Data Vault**
- View all saved encrypted entries
- Click **Retrieve** to decrypt
- View metadata like storage date

---

## ❓ FAQ

**Q: What if I forget my passkey?**  
A: Unfortunately, recovery is not possible. This ensures maximum security.

**Q: Is data still safe if someone gets `encrypted_data.json`?**  
A: Yes. Without your passkey, the data is practically unbreakable.

**Q: Can I use this on multiple devices?**  
A: Yes. Just securely transfer `encrypted_data.json` and `secret.key`.

**Q: How do I change the master password?**  
A: Edit the `MASTER_PASSWORD` constant in the code manually.

**Q: Is this suitable for enterprise use?**  
A: For enterprises, we recommend adding extra layers like hardware-based security and centralized key management.

---

**Secure Vault Pro** – Because your privacy deserves military-grade protection.
