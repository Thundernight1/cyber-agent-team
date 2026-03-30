#!/usr/bin/env bash

# Quick Reference Card for CI/CD System

cat << 'EOF'

╔════════════════════════════════════════════════════════════════╗
║                  CI/CD & TEST SYSTEM                          ║
║                   QUICK REFERENCE                             ║
╚════════════════════════════════════════════════════════════════╝

📦 SETUP (ilk defa)
  $ make setup
  $ pre-commit install

🧪 TESTING
  $ make test                    # Tüm testler
  $ make test-cov                # Coverage raporu ile
  $ pytest tests/ -v -s          # Verbose + stdout
  $ pytest tests/test_unit.py    # Specific dosya
  $ pytest -m unit               # Marker ile
  $ pytest -k test_name          # İsme göre

📋 CODE QUALITY
  $ make lint                    # Linting kontrol
  $ make format                  # Otomatik format
  $ black .                      # Format
  $ isort .                      # Import sırası
  $ flake8 .                     # Linting

🔐 SECURITY
  $ make security                # Tüm taramalar
  $ bandit -r .                  # Code security
  $ safety check                 # Dependencies

🐳 DOCKER
  $ make docker                  # Build + Run
  $ make docker-test             # Test ortamı
  $ docker-compose up app        # Çalışan app
  $ docker-compose up test       # Test suite
  $ docker-compose logs -f app   # Logs
  $ docker-compose exec app bash # Shell

🔧 TOOLS
  $ make all-checks              # Tüm kontroller
  $ make clean                   # Cleanup
  $ make help                    # Bu menu

📊 OUTPUTS
  Coverage HTML:     htmlcov/index.html
  Bandit Report:     bandit-report.json
  Test Results:      pytest output

🚀 GITHUB ACTIONS
  • Auto runs on push to main/develop
  • Pull request validations
  • Tests Python 3.9, 3.10, 3.11
  • Codecov integration

💡 WORKFLOW
  1. Code yaz → 2. Pre-commit hook çalışır → 
  3. Git commit → 4. Push → 5. GitHub Actions tetiklenir →
  6. Tests/Lint/Security checks → 7. Deploy (if passing)

📚 DOCS
  CI_CD_SYSTEM.md - Detaylı dökümantasyon

═══════════════════════════════════════════════════════════════════

EOF
