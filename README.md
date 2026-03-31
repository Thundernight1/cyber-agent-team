# 🛡️ Cyber Agent Team — AI-Powered Purple Team Security Platform

**Autonomous penetration testing and vulnerability assessment powered by 17 AI agents.**

[![CI/CD](https://github.com/CyberSurX/cyber-agent-team/actions/workflows/ci.yml/badge.svg)](https://github.com/CyberSurX/cyber-agent-team/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)

---

## 🎯 Overview

Cyber Agent Team is an AI-driven cybersecurity platform that automates vulnerability assessments and red team operations. Using a **3-layer agent architecture** (Operator → Analysis → Decision), the system performs:

- **Passive OSINT** — DNS, Whois, domain reconnaissance
- **Network Scanning** — Nmap port discovery, service enumeration
- **Vulnerability Assessment** — SQL injection, web vulnerabilities, misconfigurations
- **Attack Path Analysis** — Identifying exploitation chains
- **Professional Reporting** — Executive summaries + technical findings

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- macOS / Linux
- [Ollama](https://ollama.ai/) (local LLM) or Ollama Cloud API key

### Setup

```bash
git clone https://github.com/CyberSurX/cyber-agent-team.git
cd cyber-agent-team

# Create virtual environment & install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
make test

# Start interactive CLI
python cli/main_cli.py
```

---

## 📊 Architecture

### 3-Layer Agent System (17 Agents)

```
OPERATOR LAYER (Data Collection)
├─ NetScan         Network discovery (nmap)
├─ WifiRecon       Wireless analysis
├─ PassiveEye      Passive traffic monitoring
└─ PhysRecon       Physical observation

ANALYSIS LAYER (Vulnerability Discovery)
├─ AssetMap        Asset correlation
├─ VulnHunter      Vulnerability scanning
├─ CredCheck       Credential analysis
└─ ExposureRadar   Exposure analysis

DECISION LAYER (Attack Planning)
├─ PathFinder      Attack path identification
├─ RiskEngine      Risk prioritization
├─ BlindSpot       Detection gap analysis
├─ ShieldPlanner   Remediation strategy
└─ ReportGen       Report generation

SUPPORT LAYER (Infrastructure)
├─ FullStack       Backend API
├─ UIForge         Web dashboard
├─ PurpleLead      Team orchestrator
└─ SecOps          DevSecOps integration
```

### Core Components

| Module | Description |
|--------|-------------|
| `core/base_agent.py` | BaseAgent class, TaskResult, SharedState (Blackboard pattern) |
| `core/llm_client.py` | OllamaClient — Cloud + Local LLM integration |
| `core/ai_router.py` | AIRouter — strict sequential LLM execution |
| `core/validator.py` | EvidenceValidator — No-Fake mandate enforcement |
| `core/tool_wrapper.py` | ToolWrapper — subprocess execution handler |
| `tools/security_tools.py` | ToolFactory — nmap, whois, dns, sqlmap, etc. |
| `orchestrator/purple_lead.py` | PurpleLeadOrchestrator — task queue & evidence flow |
| `dashboard/app.py` | Flask web dashboard for reports |
| `cli/main_cli.py` | Interactive CLI entry point |

---

## 🛠 Security Tools

| Tool | Category | Description |
|------|----------|-------------|
| **nmap** | Network | Port scanning & service discovery |
| **whois** | OSINT | Domain/IP registration info |
| **nslookup** | OSINT | DNS enumeration (A, MX, NS, TXT) |
| **sqlmap** | Web | SQL injection testing |
| **metasploit** | Exploit | Exploitation framework |
| **nuclei** | Web | Template-based vulnerability scanner |
| **nikto** | Web | Web server scanner |
| **trivy** | Container | Container security scanning |

---

## 🧪 Testing

```bash
make test          # Run all tests (pytest)
make test-cov      # Tests with coverage report
make lint          # flake8, black --check, isort --check
make format        # Auto-format with black + isort
make security      # bandit + safety checks
make all-checks    # lint + test + security
```

---

## 🐳 Docker

```bash
make docker        # Build and run on :8443
make docker-test   # Run tests in Docker
docker-compose up -d
```

---

## 📁 Project Structure

```
cyber-agent-team/
├── agents/              # Agent implementations (operator/analysis/decision)
├── cli/                 # Interactive CLI
├── config/              # Settings & agent profiles
├── core/                # Core framework (base_agent, llm_client, ai_router)
├── dashboard/           # Flask web dashboard
├── docs/                # Documentation
├── orchestrator/        # PurpleLead team orchestrator
├── tests/               # pytest test suite
├── tools/               # Security tool integrations
├── .github/workflows/   # CI/CD pipeline
├── Makefile             # Build automation
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Dev/test dependencies
```

---

## ⚖️ Legal & Compliance

> **This tool is for authorized security testing only.**

- Always obtain written permission before testing
- Comply with all applicable laws and regulations
- See [LICENSE](LICENSE) for full terms

---

## 👤 Author

**Mehmet Zümrüt** — [CyberSurX](https://github.com/CyberSurX)

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Made with ❤️ for the security community**
