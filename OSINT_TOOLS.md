# OSINT & Security Tools Integration

## ✅ Yapılan İyileştirmeler

### 1. **Shodan - Free Tier Optimizasyonu**
- ✅ **Shodan CLI fallback**: Eğer `shodan` CLI yoksa, alternatif araçlar otomatik kullanılır
- ✅ **Free tier desteği**: myip, dns, host lookup çalışır
- 📌 Paid features (search, scan) sınırlı ama fallback'ler var

### 2. **Yeni Ücretsiz OSINT Araçları Eklendi**

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

#### **Shodan Fallback Chain**
Shodan CLI yoksa otomatik:
1. `nslookup` - DNS resolve
2. `whois` - Domain/IP info
3. `curl` - HTTP headers & SSL cert

---

## 📋 Mevcut OSINT Araçları

| Araç | Durum | Cost | Sınırlama |
|------|-------|------|-----------|
| **Whois** | ✅ Aktif | Ücretsiz | Yok |
| **DNS (nslookup)** | ✅ Aktif | Ücretsiz | Yok |
| **Shodan CLI** | ⚠️ Fallback | Free+Paid | API key gerekli |
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

# Shodan (Fallback otomatik)
shodan = tools.get('shodan')
result = await shodan.run(target='example.com', search_type='host')
```

---

## 🔧 Yapılabilecek Ek İyileştirmeler

### Alternatif OSINT API'leri (Ücretsiz)
- [ ] **Censys.io** (Free API, domain/cert info)
- [ ] **SecurityTrails** (Free tier, DNS history)
- [ ] **VirusTotal** (Free API, file/URL analysis)
- [ ] **Abuse.ch** (URLhaus, malware intel)
- [ ] **Shodan MCP** (Eğer MCP server ayarlanmışsa)

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
✅ Shodan tool (CLI): False (fallback aktif)

🎯 OSINT Recon Test: google.com
📡 DNS Query Result: Success
🔍 OSINT Fallback Result: Success (nslookup, whois, curl used)
```

---

## 💡 Not

Shodan'ın paid planı gereklidir ama:
1. **Free tier** myip, dns, host lookup ile çalışır
2. **Fallback chain** her zaman çalışır (whois + nslookup + curl)
3. **MCP Connector** varsa daha yetkili erişim olur

Proje **tamamen ücretsiz OSINT araçlarla çalışabilir**! 🎯
