# CI/CD ve Test Sistemi

Bu proje için eksiksiz bir CI/CD ve test sistemi kurulmuştur.

## 📋 Bileşenler

### 1. **GitHub Actions CI/CD Pipeline** (`.github/workflows/ci.yml`)
Otomatik olarak aşağıdaları çalıştırır:
- **Testler**: Python 3.9, 3.10, 3.11 için pytest
- **Linting**: flake8, black, isort kontrolü
- **Güvenlik Taraması**: bandit ve safety
- **Docker Build**: İmaj oluşturma doğrulaması
- **Coverage Report**: Codecov'a yükleme

Tetikleyiciler:
- Push to `main` veya `develop`
- Pull request açılması

### 2. **Yerel Test Ortamı**

#### Pytest Konfigürasyonu (`pytest.ini`)
- Test keşfi ve marker desteği
- Async test desteği (`pytest-asyncio`)
- Coverage raporlama

#### Test Dosyaları (`tests/`)
- `test_unit.py` - Unit testler
- `test_async.py` - Async testler

### 3. **Docker Desteği**

#### Dockerfile (Multi-stage)
```
Build Stage:
├── Python 3.11-slim
├── Build tools yüklemesi
└── Dependencies kurulması

Runtime Stage:
├── Python 3.11-slim
├── Non-root user (appuser)
├── Health check
└── Optimized image
```

#### Dockerfile.test
Test ortamı için ayrı Dockerfile:
- Tüm test araçlarıyla birlikte
- pytest, coverage, linting, security tools

#### docker-compose.yml
```yaml
services:
  app        # Çalışan uygulama (port 8443)
  test       # Test suite çalıştırıcı
```

### 4. **Pre-commit Hooks** (`.pre-commit-config.yaml`)
Commit öncesi otomatik kontroller:
- Trailing whitespace temizliği
- File ending düzeltmesi
- YAML/JSON doğrulaması
- Black formatting
- isort (import sırası)
- flake8 linting
- bandit security check

### 5. **Code Quality Tools**

#### Yüklü Araçlar:
- **black** - Code formatter
- **isort** - Import optimizer
- **flake8** - Linter
- **bandit** - Security scanner
- **safety** - Dependency vulnerabilities
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting

## 🚀 Hızlı Başlangıç

### 1. Setup (Tek seferlik)
```bash
# Tüm dependencies ve pre-commit hooks kur
make setup
# veya
bash setup_cicd.sh
```

### 2. Testleri Çalıştır

```bash
# Temel test
make test
pytest tests/ -v

# Coverage raporu ile
make test-cov
pytest tests/ -v --cov=. --cov-report=html

# Specific test dosyası
pytest tests/test_unit.py -v

# Specific marker ile
pytest -m unit
pytest -m asyncio
```

### 3. Linting & Formatting

```bash
# Tüm linting kontrolleri
make lint

# Kodu otomatik format et
make format

# Bileşen bazında
black .              # Code formatting
isort .              # Import sorting
flake8 .             # Linting
```

### 4. Güvenlik Taraması

```bash
make security

# Veya bağlantılı olarak
bandit -r .
safety check
```

### 5. Docker ile Çalıştırma

```bash
# Build (otomatik)
docker build -t cyber-agent-team:latest .

# Run
make docker
docker-compose up app

# Test in Docker
make docker-test
docker-compose up test

# Shell erişimi
docker-compose exec app bash

# Logs
docker-compose logs -f app
```

### 6. Tüm Kontroller

```bash
# Linting + Tests + Security
make all-checks
```

## 📁 Dosya Yapısı

```
.
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions pipeline
├── tests/
│   ├── __init__.py
│   ├── test_unit.py                 # Unit testler
│   └── test_async.py                # Async testler
├── Dockerfile                        # Production Dockerfile
├── Dockerfile.test                   # Test Dockerfile
├── docker-compose.yml                # Docker Compose config
├── pytest.ini                        # Pytest configuration
├── .pre-commit-config.yaml           # Pre-commit hooks
├── .bandit                           # Bandit config
├── .dockerignore                     # Docker ignore patterns
├── .gitignore                        # Git ignore patterns
├── requirements.txt                  # Production deps
├── requirements-dev.txt              # Dev deps
├── Makefile                          # Convenience commands
└── setup_cicd.sh                     # Setup script
```

## 🔧 Özelleştirme

### Test Marker Ekleme

`pytest.ini` içinde:
```ini
markers =
    unit: unit tests
    integration: integration tests
    slow: slow tests
```

Test dosyasında:
```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass
```

### Pre-commit Hooks Konfigürasyonu

`.pre-commit-config.yaml` içinde hook ekle/kaldır.

Kur:
```bash
pre-commit install
```

Manual çalıştır:
```bash
pre-commit run --all-files
```

### CI/CD Workflow Düzenleme

`.github/workflows/ci.yml` içinde:
- Branch filter
- Python versiyonları
- Yeni job/step ekle

## ✅ Best Practices

1. **Pre-commit Hooks Kur**
   ```bash
   pre-commit install
   ```

2. **Her Zaman Coverage Kontrol Et**
   ```bash
   pytest --cov=. --cov-report=term-missing
   ```

3. **Linting Sonrası Commit Et**
   ```bash
   make format && make lint && git add .
   ```

4. **Branch Protection Kuralları**
   - Settings → Branches → Add rule
   - "Require status checks to pass"
   - `test`, `lint`, `security` seç

5. **Test Yazarken**
   - Unit test = hızlı, izole
   - Integration test = harici bağımlılıklar
   - Async test = coroutine functions

## 🐛 Troubleshooting

### Pre-commit Hook'lar Çalışmıyor
```bash
pre-commit install --install-hooks
pre-commit run --all-files
```

### Docker Build Başarısız
```bash
# Cache temizle
docker system prune -a

# Dockerfile'ı kontrol et
docker build -t cyber-agent-team:latest . --no-cache
```

### Test Hataları
```bash
# Verbose çıktı
pytest tests/ -vv -s

# Specific test
pytest tests/test_unit.py::TestUtilities::test_basic_arithmetic -v

# Traceback hep göster
pytest --tb=long
```

### Docker Compose Sorunları
```bash
# Build yenile
docker-compose build --no-cache

# Container temizle
docker-compose down -v

# Logs kontrol et
docker-compose logs test
```

## 📊 Coverage Raporu

Test coverage'ı HTML olarak görüntüle:
```bash
pytest tests/ -v --cov=. --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

## 🔐 Güvenlik

1. **Dependency Vulnerabilities**
   ```bash
   safety check
   ```

2. **Code Security Issues**
   ```bash
   bandit -r .
   ```

3. **Secrets Scanning** (GitHub otomatik)
   - `.env` dosyası asla commit etme
   - Secrets in GitHub Settings → Secrets

## 📝 Komut Özeti

| Komut | Açıklama |
|-------|----------|
| `make setup` | Tüm kurulumları yap |
| `make test` | Testleri çalıştır |
| `make test-cov` | Coverage ile test |
| `make lint` | Linting kontrol |
| `make format` | Kodu format et |
| `make security` | Security taraması |
| `make docker` | Docker'da çalıştır |
| `make docker-test` | Docker'da test |
| `make clean` | Artifact'ları temizle |
| `make all-checks` | Tüm kontroller |

## 🎯 Sonraki Adımlar

1. **Test Kapsamını Artır**: `tests/` içine daha fazla test dosyası ekle
2. **CI/CD Workflow Genişlet**: `.github/workflows/ci.yml` içine deployment step ekle
3. **Docker Registry**: Docker Hub/ECR'a push etmek için `.github/workflows/ci.yml` güncelle
4. **Kubernetes Deployment**: `k8s/` klasörü oluştur ve manifesto ekle
5. **Monitoring**: Application logs ve metrics için ELK/Prometheus ekle

---

**Not**: Tüm konfigurasyonlar production-ready'dir. Gerekli ayarlamaları yaparak kullanabilirsiniz.
