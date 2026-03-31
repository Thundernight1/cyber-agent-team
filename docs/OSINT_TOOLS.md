# OSINT & Security Tools Integration

## ✅ Yapılan İyileştirmeler

### 1. **OSINT Fallback Chain**
- ✅ **Otomatik fallback**: Alternatif OSINT araçları (whois, nslookup, curl) otomatik kullanılır
- ✅ **Ücretsiz araçlar**: DNS, Whois, HTTP header analizi çalışır
- 📌 Ek API entegrasyonları (Censys, SecurityTrails) planlanıyor

### 2. **Ücretsiz OSINT Araçları**

#### **WhoisTool** (Ücretsiz & Sınırsız)
```bash
whois google.com
# Çıktı: Registrar, creation/expiration dates, nameservers
```

#### **DNSToolchain** (Ücretsiz & Hızlı)
```bash
nslookup -type=A google.com  # IPv4
nslookup -type=MX google.com # Mail servers
nslookup -type=TXT google.com # TXT records
```

#### **OSINT Fallback Chain**
Araç yoksa otomatik:
1. `nslookup` - DNS resolve
2. `whois` - Domain/IP info
3. `curl` - HTTP headers & SSL cert

---

## 📋 Mevcut OSINT Araçları

| Araç | Durum | Cost | Sınırlama |
|------|-------|------|-----------|
| **Whois** | ✅ Aktif | Ücretsiz | Yok |
| **DNS (nslookup)** | ✅ Aktif | Ücretsiz | Yok |
| **Nmap** | ✅ Hazır | Ücretsiz | - |
| **Curl** | ✅ Hazır | Ücretsiz | - |

---

## 🚀 Kullanım

### CLI ile OSINT Recon
```bash
./run.sh recon google.com
```

### Dashboard
```bash
./run.sh dashboard
# http://localhost:8443
```

### Python API
```python
from tools.security_tools import ToolFactory

tools = ToolFactory.initialize()

# DNS Query
dns = tools.get('dns')
result = await dns.run(target='example.com', record_type='A')

# Whois Lookup
whois = tools.get('whois')
result = await whois.run(target='example.com')
```

---

## 🔧 Yapılabilecek Ek İyileştirmeler

### Alternatif OSINT API'leri (Ücretsiz)
- [ ] **Censys.io** (Free API, domain/cert info)
- [ ] **SecurityTrails** (Free tier, DNS history)
- [ ] **VirusTotal** (Free API, file/URL analysis)
- [ ] **Abuse.ch** (URLhaus, malware intel)

### CLI Araçlar
- [ ] `dig` (Advanced DNS queries)
- [ ] `curl` (HTTP headers, SSL certs)
- [ ] `httpx` (Fast HTTP scanner)
- [ ] `amass` (Subdomain enumeration)

### Komut
```bash
# OSINT API'leri eklemek için
python3 -c "from tools.security_tools import ToolFactory; ToolFactory.initialize()"
```

---

## 📊 Test Sonuçları

```
✅ Whois tool: True
✅ DNS tool: True

🎯 OSINT Recon Test: google.com
📡 DNS Query Result: Success
🔍 OSINT Fallback Result: Success (nslookup, whois, curl used)
```

---

## 💡 Not

OSINT araçları tamamen ücretsiz çalışır:
1. **Whois** — domain/IP bilgisi
2. **DNS (nslookup)** — A, MX, NS, TXT kayıtları
3. **Fallback chain** — her zaman çalışır (whois + nslookup + curl)

Proje **tamamen ücretsiz OSINT araçlarla çalışabilir**! 🎯
