# Purple Team SOC — Tam Kurulum Rehberi
## Kendi Makinenizde Gerçek Test

---

## 1. OLLAMA CLOUD API KEY

Sisteminiz `https://ollama.com/api` adresini kullanıyor.
Ollama Cloud chat API için token gerekiyor.

**Adımlar:**
1. https://ollama.com → Sign in
2. Settings → API Keys → New Key
3. Key'i kopyalayın

**Terminalden ayarlayın:**
```bash
export OLLAMA_API_KEY="sk-ollama-xxxxx"
```

**Kalıcı ayar (~/.zshrc veya ~/.bashrc):**
```bash
echo 'export OLLAMA_API_KEY="sk-ollama-xxxxx"' >> ~/.zshrc
source ~/.zshrc
```

---

## 2. SHODAN DURUMU

- **MCP Connector** → Zaten bağlı ve çalışıyor (host lookup, search, CVE)
- **Python API Key** (`Jvhe8MRaHvH9u9BU6P40wWgTDSYgODva`) → OSS plan, sorgu kredisi sıfır
  - Tam erişim için: https://account.shodan.io → Upgrade ($49/ay)
  - Veya ek sorgu kredisi satın alın

settings.py'e kaydedildi, key hazır.

---

## 3. DOCKER İLE KALİ LİNUX HEDEF ORTAMI

Terminal 1 — Kali hedef (savunmasız servislerle):
```bash
# Hafif Kali + bazı servisler açık
docker run -d --name kali-target \
  -p 2222:22 \
  -p 8080:80 \
  -p 3306:3306 \
  kalilinux/kali-rolling \
  bash -c "
    apt-get update -q &&
    apt-get install -y openssh-server apache2 mariadb-server -q &&
    service ssh start &&
    service apache2 start &&
    service mariadb start &&
    tail -f /dev/null
  "

# Hedef IP'yi öğrenin:
docker inspect kali-target | grep IPAddress
```

Daha hızlı alternatif — hazır savunmasız VM:
```bash
# Metasploitable2 (kasıtlı savunmasız)
docker pull tleemcjr/metasploitable2
docker run -d --name vuln-target -p 2222:22 -p 8080:80 -p 3306:3306 tleemcjr/metasploitable2
docker inspect vuln-target | grep IPAddress
```

---

## 4. GÜVENLİK ARAÇLARI (macOS)

```bash
# Homebrew ile
brew install nmap
brew install sqlmap
brew install nuclei

# Nikto
brew install nikto

# Trivy (container scanner)
brew install trivy
```

veya Docker üzerinden:
```bash
# Nmap
docker run --rm instrumentisto/nmap -sV 172.17.0.2

# Nuclei
docker run --rm projectdiscovery/nuclei -u http://172.17.0.2
```

---

## 5. SİSTEMİ BAŞLATMA

```bash
cd /path/to/cyber-agent-team

# Env ayarları
export OLLAMA_API_KEY="sk-ollama-xxxxx"
export SHODAN_API_KEY="Jvhe8MRaHvH9u9BU6P40wWgTDSYgODva"

# Test runner (Python-native)
python3 test_runner.py

# Tam sistem (Ollama + araçlar gerektirir)
python3 main.py --target 172.17.0.2

# Dashboard
uvicorn main:app --host 0.0.0.0 --port 8443
```

---

## 6. TEST AKIŞI

```
Kali hedef başlat (Docker)
        ↓
Ollama API key ayarla
        ↓
python3 main.py --target <DOCKER_IP>
        ↓
Operator Layer: Nmap → port/servis tarama
        ↓
Analysis Layer: Nuclei/Nikto → zafiyet analizi
        ↓
Decision Layer: LLM reasoning → saldırı yolları
        ↓
Rapor: reports/ klasörüne kaydedilir
```

---

## 7. MEVCUT DURUM ÖZETİ

| Bileşen | Durum | Not |
|---------|-------|-----|
| Python altyapısı | ✅ Çalışıyor | 17 ajan yüklü |
| SharedState akışı | ✅ Test edildi | 3 katman doğrulandı |
| Shodan MCP | ✅ Çalışıyor | Host lookup, CVE search |
| Shodan Python API | ⚠️ OSS plan | Upgrade gerekli |
| Ollama Cloud | ⚠️ Key lazım | ollama.com'dan al |
| Nmap/Nuclei/Nikto | ❌ Kurulmadı | `brew install` ile kur |
| Docker hedef | ❌ Kurulmadı | Yukarıdaki komut |
| tcpdump | ✅ Mevcut | SharkTap çalışır |
