#!/bin/bash
# ============================================================
# Cyber Agent Team - Launcher Script (Strict Mode)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

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

# 1. Dependency Check (Binaries)
echo -e "${YELLOW}[*] Checking system dependencies...${NC}"
REQUIRED_TOOLS=("python3" "nmap" "git")
MISSING_TOOLS=0

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        echo -e "${RED}[✗] Missing tool: $tool${NC}"
        MISSING_TOOLS=1
    else
        echo -e "${GREEN}[✓] Found: $tool${NC}"
    fi
done

if [ $MISSING_TOOLS -eq 1 ]; then
    echo -e "${RED}[!] Critical dependencies missing. Aborting.${NC}"
    exit 1
fi

# 2. Virtual Environment Check
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[!] venv not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
else
    source venv/bin/activate
    # Check if packages are installed (simple check)
    if ! python3 -m pip freeze | grep -q "aiohttp"; then
        echo -e "${YELLOW}[!] Dependencies seem missing. Installing...${NC}"
        python3 -m pip install -r requirements.txt
    else
        echo -e "${GREEN}[✓] Virtual environment activated${NC}"
    fi
fi

# 3. Environment Variable Check
if [ -f ".env" ]; then
    echo -e "${GREEN}[✓] .env file found${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}[✗] .env file NOT found!${NC}"
    echo "    Please copy .env.example to .env and configure API keys."
    exit 1
fi

# Check critical keys
if [ -z "$OLLAMA_API_KEY" ] && [ -z "$OLLAMA_API_KEY_1" ]; then
    echo -e "${YELLOW}[!] Warning: OLLAMA_API_KEY is not set. Using Local Mode only.${NC}"
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
