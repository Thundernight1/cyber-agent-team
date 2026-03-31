# Purple Team Security - AI-Powered Pentesting

**An autonomous security team powered by AI agents. Automated penetration testing, vulnerability scanning, and red team operations.**

---

## 🎯 Overview

Purple Team Security is an AI-driven cybersecurity platform that automates vulnerability assessments and red team operations. Using a 3-layer agent architecture (Operator → Analysis → Decision), the system performs:

- **Passive OSINT** (DNS, Whois, domain reconnaissance)
- **Network scanning** (Nmap port discovery, service enumeration)
- **Vulnerability assessment** (SQL injection, web vulnerabilities, misconfigurations)
- **Attack path analysis** (identifying exploitation chains)
- **Professional reporting** (executive summaries + technical findings)

**Result**: Security assessments in 2-3 days instead of 4+ weeks. At 1/3 the cost of traditional consultancies.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- macOS/Linux/Windows with Bash
- Ollama (local) or Ollama Cloud API key (optional)

### Setup (5 minutes)

```bash
# Clone repo
git clone https://github.com/Thundernight1/cyber-agent-team.git
cd cyber-agent-team

# Install dependencies
make setup

# Run tests
make test

# Start dashboard
./run.sh dashboard
# → http://localhost:8443
```

### Run a Scan

```bash
# Quick OSINT recon
./run.sh recon example.com

# Full assessment
./run.sh scan example.com

# Interactive CLI
./run.sh cli
```

---

## 📊 Architecture

### 3-Layer Agent System

```
OPERATOR LAYER (Data Collection)
├─ NetScan: Network discovery (nmap)
├─ WifiRecon: Wireless analysis
├─ PassiveEye: Passive traffic monitoring
└─ PhysRecon: Physical observation

ANALYSIS LAYER (Vulnerability Discovery)
├─ AssetMap: Asset correlation
├─ VulnHunter: Vulnerability scanning
├─ CredCheck: Credential analysis
└─ ExposureRadar: Exposure analysis

DECISION LAYER (Attack Planning)
├─ PathFinder: Attack path identification
├─ RiskEngine: Risk prioritization
├─ BlindSpot: Detection gap analysis
├─ ShieldPlanner: Remediation strategy
└─ ReportGen: Report generation

SUPPORT LAYER (Infrastructure)
├─ FullStack: Backend API
├─ UIForge: Web dashboard
├─ PurpleLead: Team orchestrator
└─ SecOps: DevSecOps integration
```

**Total: 17 AI agents**

---

## 🛠 Security Tools

### Active Tools
- **nmap** - Network port scanning
- **whois** - Domain/IP information
- **dns (nslookup)** - DNS enumeration
- **sqlmap** - SQL injection testing
- **metasploit** - Exploitation framework

### Available Tools (Install as needed)
- nuclei - Template-based vulnerability scanner
- nikto - Web server scanner
- trivy - Container security
- zap - OWASP ZAP integration


### OSINT
- Whois lookups
- DNS enumeration (A, MX, NS, TXT records)
- OSINT fallback chain (whois/nslookup/curl)

---

## 📈 Service Offerings

### Quick Scan
- **Duration**: 2-3 days
- **Price**: $7,500
- **Includes**: OSINT + port scanning + basic vulnerability assessment
- **Margin**: 93%

### Standard Assessment
- **Duration**: 1 week
- **Price**: $25,000
- **Includes**: Full recon + vulnerability scanning + attack path analysis
- **Margin**: 88%

### Enterprise Assessment
- **Duration**: 2 weeks
- **Price**: $50,000+
- **Includes**: Full red team simulation + manual exploitation + detailed remediation
- **Margin**: 90%

### Monthly Retainer
- **Price**: $3,000/month
- **Includes**: Monthly scans + quarterly deep dives + continuous monitoring
- **Margin**: 83%

---

## 💰 Business Model

**Target Market**: Mid-market tech companies (Seattle area)

**Customer Profile**:
- Series A/B SaaS startups ($50M-$500M valuation)
- FinTech companies
- E-commerce platforms
- Healthcare tech (HIPAA compliance)

**Go-To-Market**:
1. Cold email outreach (Apollo.io)
2. LinkedIn + Hunter.io prospecting
3. Personalized security findings (run real scans on their domain)
4. Discovery calls
5. Close within 2-3 weeks

**Target**: 10 customers/month = $75,000/month revenue

See [LAUNCH_PLAN.md](LAUNCH_PLAN.md) for detailed 30-day strategy.

---

## 📚 Documentation

- **[AGENTS.md](AGENTS.md)** - Technical specifications for AI agents
- **[GO_TO_MARKET.md](GO_TO_MARKET.md)** - 30-60 day business strategy
- **[LAUNCH_PLAN.md](LAUNCH_PLAN.md)** - Day-by-day action plan
- **[COLD_EMAIL_TEMPLATES.md](COLD_EMAIL_TEMPLATES.md)** - 8 ready-to-use sales templates
- **[OSINT_TOOLS.md](OSINT_TOOLS.md)** - Tool documentation + free alternatives

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
pytest tests/test_unit.py::TestClass::test_name -v

# Lint + format
make lint
make format

# All checks
make all-checks
```

---

## 🔧 Development

### Project Structure
```
.
├── agents/              # Agent implementations
│   ├── operator/       # Scanning agents
│   ├── analysis/       # Analysis agents
│   └── decision/       # Decision agents
├── core/               # Core framework
│   ├── base_agent.py  # BaseAgent class
│   └── llm_client.py  # LLM integration
├── tools/              # Security tool integrations
├── orchestrator/       # Team coordination
├── dashboard/          # Web UI
├── config/             # Configuration
├── tests/              # Test suite
└── docs/               # Documentation
```

### Add a New Tool

```python
# tools/security_tools.py
class MyNewTool(BaseTool):
    def __init__(self):
        super().__init__("mytool", "category", "executable_path")
    
    async def run(self, **kwargs) -> ToolResult:
        cmd = ["mytool", "arg1", "arg2"]
        return await self._execute_command(cmd)

# Register in ToolFactory.initialize()
cls._tools["mytool"] = MyNewTool()
```

---

## 📊 Verified Results

All tools tested with real data:

```
✅ DNS Lookup: github.com → 140.82.116.4
✅ Whois: github.com → MarkMonitor registrar (2007 registration)
✅ Nmap Port Scan: Found 6 open ports (5000, 5432, 8443, etc)
✅ OSINT Fallback: nslookup + whois + curl chain working
✅ Dashboard: 17 agents running, API responding
✅ Tests: 4/4 passing
```

---

## 🚀 Deployment

### Docker
```bash
make docker              # Build and run Docker image
make docker-test        # Run tests in Docker
docker-compose up -d    # Start all services
```

### Production
- FastAPI + Uvicorn
- Dashboard: https://localhost:8443
- API: /api/status, /api/tools, /api/scan
- WebSocket: /ws (live updates)

---

## ⚖️ Legal & Compliance

**Important**: This tool is intended for authorized security testing only.

- Always get written permission before testing
- Terms of service included in service agreements
- E&O Insurance recommended ($5-10K/year)
- CVSS scoring and risk assessment provided

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Mehmet Zümrüt**

- GitHub: [@Thundernight1](https://github.com/Thundernight1)
- Project: Purple Team Security

---

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: See /docs directory
- **Email**: [contact info to be added]

---

## 🎯 Roadmap


- [ ] Nuclei template automation
- [ ] Advanced exploitation chains
- [ ] Machine learning vulnerability prediction
- [ ] SaaS multi-tenant platform
- [ ] Mobile app (iOS/Android)
- [ ] Real-time threat intelligence feeds

---

## 🙏 Acknowledgments

- Ollama for LLM infrastructure
- Nmap for network discovery
- Open source security community
- All contributors and testers

---

**Made with ❤️ for the security community**
