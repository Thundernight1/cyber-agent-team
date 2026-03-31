# Makefile for Cyber Agent Team

.PHONY: setup test clean run

setup:
	@echo "Setting up environment..."
	./run.sh interactive

test:
	@echo "Running tests..."
	venv/bin/pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	venv/bin/pytest tests/ -v --cov=. --cov-report=html

lint:
	venv/bin/flake8 agents core tools || echo "flake8 bulunamadı"
	venv/bin/black --check agents core tools || echo "black bulunamadı"
	venv/bin/isort --check agents core tools || echo "isort bulunamadı"

format:
	@echo "Formatting code..."
	venv/bin/black . || echo "black bulunamadı"
	venv/bin/isort . || echo "isort bulunamadı"

security:
	@echo "Running security checks..."
	venv/bin/bandit -r agents core tools || echo "bandit atlandı"
	venv/bin/safety check || echo "safety atlandı"

docker:
	@echo "Running in Docker..."
	docker-compose up -d app

docker-test:
	@echo "Testing in Docker..."
	docker-compose run --rm test

all-checks: format lint test security
	@echo "Tüm kontroller tamamlandı."

clean:
	@echo "Cleaning up..."
	rm -rf venv
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -rf {} +

run:
	./run.sh interactive

# --- Commands from Agent Starter Pack ---

eval:
	@echo "==============================================================================="
	@echo "| Running Agent Evaluation                                                    |"
	@echo "==============================================================================="
	uv sync --dev --extra eval
	uv run adk eval ./tests $${EVALSET:-tests/eval/evalsets/basic.evalset.json} \
		$(if $(EVAL_CONFIG),--config_file_path=$(EVAL_CONFIG),$(if $(wildcard tests/eval/eval_config.json),--config_file_path=tests/eval/eval_config.json,))

eval-all:
	@echo "==============================================================================="
	@echo "| Running All Evalsets                                                        |"
	@echo "==============================================================================="
	@for evalset in tests/eval/evalsets/*.evalset.json; do \
		echo ""; \
		echo "▶ Running: $$evalset"; \
		$(MAKE) eval EVALSET=$$evalset || exit 1; \
	done
	@echo ""
	@echo "✅ All evalsets completed"

install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

	uv sync

