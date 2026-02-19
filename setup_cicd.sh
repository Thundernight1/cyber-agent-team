#!/bin/bash
# ============================================================
# CI/CD and Test System Setup Script
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════╗"
echo "║   CI/CD & Test System Setup                   ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# Create tests directory
echo -e "${YELLOW}[→] Creating tests directory...${NC}"
mkdir -p tests
touch tests/__init__.py

# Install development dependencies
if [ -f "requirements-dev.txt" ]; then
    echo -e "${YELLOW}[→] Installing development dependencies...${NC}"
    pip install -r requirements-dev.txt
fi

# Setup pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    echo -e "${YELLOW}[→] Setting up pre-commit hooks...${NC}"
    pre-commit install || echo "Pre-commit already installed"
fi

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════╗"
echo "║   Setup Complete!                             ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Available commands:${NC}"
echo "  • Run tests locally:"
echo "    ${GREEN}pytest tests/ -v${NC}"
echo ""
echo "  • Run tests with coverage:"
echo "    ${GREEN}pytest tests/ -v --cov=. --cov-report=html${NC}"
echo ""
echo "  • Run linting:"
echo "    ${GREEN}flake8 .${NC}"
echo ""
echo "  • Format code:"
echo "    ${GREEN}black .${NC}"
echo ""
echo "  • Run all checks:"
echo "    ${GREEN}pre-commit run --all-files${NC}"
echo ""
echo "  • Run in Docker:"
echo "    ${GREEN}docker-compose up app${NC}"
echo ""
echo "  • Run tests in Docker:"
echo "    ${GREEN}docker-compose up test${NC}"
echo ""
