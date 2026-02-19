#!/bin/bash
# ============================================================
# Cyber Agent Team - Launcher Script
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}[✓] Virtual environment activated${NC}"
else
    echo -e "${RED}[✗] venv not found. Please create it first:${NC}"
    echo "    python3 -m venv venv"
    echo "    source venv/bin/activate"
    echo "    pip install -r requirements.txt"
    exit 1
fi

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════╗"
echo "║   CYBER AGENT TEAM LAUNCHER         ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# .env file check
if [ -f ".env" ]; then
    echo -e "${GREEN}[✓] .env file found${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}[!] .env file not found. Copy .env.example:${NC}"
    echo "    cp .env.example .env"
fi

# Mode selection
case "${1:-interactive}" in
    cli|c)
        echo -e "${GREEN}[→] Starting CLI mode...${NC}"
        python3 cli/main_cli.py "${@:2}"
        ;;
    dashboard|d|web)
        echo -e "${GREEN}[→] Starting web dashboard (port: ${DASHBOARD_PORT:-8443})...${NC}"
        python3 -m uvicorn dashboard.app:app --host "${DASHBOARD_HOST:-0.0.0.0}" --port "${DASHBOARD_PORT:-8443}" --reload
        ;;
    scan|s)
        if [ -z "$2" ]; then
            echo -e "${RED}[✗] Target not provided. Usage: ./run.sh scan <target>${NC}"
            exit 1
        fi
        echo -e "${GREEN}[→] Running direct scan: $2${NC}"
        python3 cli/main_cli.py --scan "$2"
        ;;
    recon|r)
        if [ -z "$2" ]; then
            echo -e "${RED}[✗] Target not provided. Usage: ./run.sh recon <target>${NC}"
            exit 1
        fi
        echo -e "${GREEN}[→] Running recon scan: $2${NC}"
        python3 cli/main_cli.py --recon "$2"
        ;;
    interactive|i|*)
        echo -e "${GREEN}[→] Starting interactive CLI...${NC}"
        python3 cli/main_cli.py
        ;;
esac
