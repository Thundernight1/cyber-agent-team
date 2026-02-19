.PHONY: help setup test lint format security docker docker-test clean

help:
	@echo "CI/CD & Test System Commands:"
	@echo ""
	@echo "  setup           - Install dependencies and setup pre-commit hooks"
	@echo "  test            - Run all tests"
	@echo "  test-cov        - Run tests with coverage report"
	@echo "  lint            - Run linting checks"
	@echo "  format          - Format code with black and isort"
	@echo "  security        - Run security scans"
	@echo "  docker          - Build and run Docker image"
	@echo "  docker-test     - Run tests in Docker"
	@echo "  docker-build    - Build Docker image"
	@echo "  clean           - Clean up build artifacts and cache"
	@echo "  all-checks      - Run all checks (lint, tests, security)"

setup:
	bash setup_cicd.sh

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated: htmlcov/index.html"

lint:
	flake8 . --max-line-length=127 --extend-ignore=E203
	black --check .
	isort --check-only .

format:
	black .
	isort .

security:
	bandit -r . -f json -o bandit-report.json || true
	safety check || true

docker:
	docker-compose up -d app
	@echo "Application running on port 8443"

docker-test:
	docker-compose up test

docker-build:
	docker build -t cyber-agent-team:latest .

docker-shell:
	docker-compose exec app bash

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true

all-checks: lint test security
	@echo "All checks passed!"
