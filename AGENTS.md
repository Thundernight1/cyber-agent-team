# AGENTS.md - Cyber Agent Team Guidelines

## Build/Test Commands
- **Setup**: `make setup` (installs dependencies, pre-commit hooks)
- **Run all tests**: `make test` - pytest tests/ -v
- **Run single test**: `pytest tests/test_unit.py::TestClass::test_name -v`
- **Tests with coverage**: `make test-cov`
- **Lint**: `make lint` (flake8, black --check, isort --check)
- **Format**: `make format` (black, isort)
- **Security**: `make security` (bandit, safety)
- **Docker**: `make docker` (builds and runs app on :8443)
- **All checks**: `make all-checks` (lint, test, security)

## ⚠️ EXECUTION RULES (2026-02-21 güncellendi)
- **ASLA** `asyncio.gather()` ile paralel LLM çağrısı yapma
- Tüm ajanlar SIRALI çalışır: bir ajan bitmeden sonraki başlamaz
- `run_single_task(task_type, ...)` → sadece 1 model çağrılır
- 17 ajan = tanımlı profil listesi; hepsi aynı anda ÇALIŞMAZ
- Model router: görev tipine göre yalnızca 1 model seçilir

## Architecture & Structure
**3-Layer Agent Architecture**: Operator → Analysis → Decision → Support
**Execution**: STRICTLY SEQUENTIAL — no asyncio.gather on LLM calls

**Core Components**:
- `core/base_agent.py` - BaseAgent class, TaskResult dataclass, AgentLayer/AgentStatus enums
- `core/llm_client.py` - OllamaClient (Cloud + Local), LLMResponse dataclass
- `config/settings.py` - MODEL_ASSIGNMENTS dict, TEAM_ROSTER (AgentProfile), SECURITY_TOOLS config
- `agents/{analysis,decision,operator}/` - Agent implementations per layer
- `orchestrator/purple_lead.py` - Purple team orchestrator
- `tests/` - Unit & async tests with pytest markers
- `tools/` - Security tools integration (nmap, nikto, nuclei, zap, trivy, etc.)

**Dependencies**: FastAPI, Uvicorn, Pydantic, aiohttp, websockets, pyserial

## Code Style
- **Language**: Python 3.11
- **Imports**: Stdlib → third-party → local (organized by isort profile:black)
- **Formatting**: Black (127 char line limit), isort, pycln
- **Typing**: Use dataclasses, Enum, typing.Dict/List/Optional
- **Error Handling**: Use logging module, structured TaskResult for agent outputs
- **Naming**: snake_case for functions/vars, PascalCase for classes/enums
- **Async**: Use asyncio + aiohttp for concurrent operations
- **Logging**: `logger = logging.getLogger("cyber-agent.module")`
- **Pre-commit**: flake8 (max-line=127, ignore E203), trailing-whitespace, check-yaml, bandit
