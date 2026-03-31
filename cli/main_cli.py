#!/usr/bin/env python3
"""
Cyber Agent Team - CLI Arayüzü
İnteraktif komut satırı ile ajan ekibini yönet.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import final

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import TEAM_ROSTER  # noqa: E402
from orchestrator.purple_lead import PurpleLeadOrchestrator  # noqa: E402

logger = logging.getLogger("cyber-agent.cli")


# Renk kodları
@final
class C:
    RED: str = "\033[91m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    BLUE: str = "\033[94m"
    MAGENTA: str = "\033[95m"
    CYAN: str = "\033[96m"
    WHITE: str = "\033[97m"
    BOLD: str = "\033[1m"
    DIM: str = "\033[2m"
    RESET: str = "\033[0m"


BANNER = f"""
{C.RED}╔══════════════════════════════════════════════════════════════╗
║  {C.BOLD}{C.WHITE}   ██████╗██╗   ██╗██████╗ ███████╗██████╗               {C.RED}║
║  {C.WHITE}  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗              {C.RED}║
║  {C.WHITE}  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝              {C.RED}║
║  {C.WHITE}  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗              {C.RED}║
║  {C.WHITE}  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║              {C.RED}║
║  {C.WHITE}   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝              {C.RED}║
║                                                              ║
║  {C.CYAN}Purple Team Orchestrator v1.0{C.RED}                               ║
║  {C.DIM}Ollama Cloud + Tool Integrations{C.RED}                          ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
"""


def print_header(text: str):
    print(f"\n{C.CYAN}{'─' * 60}")
    print(f"  {C.BOLD}{text}{C.RESET}")
    print(f"{C.CYAN}{'─' * 60}{C.RESET}")


def print_agent(agent_id: str, profile):
    layer_colors = {
        "operator": C.GREEN,
        "analysis": C.YELLOW,
        "decision": C.RED,
        "support": C.MAGENTA,
    }
    color = layer_colors.get(profile.layer, C.WHITE)
    print(
        f"  {color}[{profile.layer.upper():>10}]{C.RESET} "
        f"{C.BOLD}{profile.name:>15}{C.RESET} "
        f"- {profile.description}"
    )
    print(f"  {C.DIM}{'':>12} Model: {profile.model}{C.RESET}")


def print_tool_status(tools):
    for t in tools:
        status = f"{C.GREEN}✓{C.RESET}" if t["available"] else f"{C.RED}✗{C.RESET}"
        print(f"  {status} {t['name']:>20} ({t['category']})")


async def interactive_mode():
    """Interactive CLI mode."""
    print(BANNER)

    orchestrator = PurpleLeadOrchestrator()
    init_result = await orchestrator.initialize()

    print(f"\n{C.GREEN}✓ System initialized{C.RESET}")
    print(f"  Session: {init_result['session_id']}")
    print(f"  Agents: {init_result.get('agents_defined', 'N/A')}")

    llm_health = init_result.get("llm_health", {"cloud": False, "local": False})
    print(f"  Cloud: {'✓' if llm_health.get('cloud') else '✗'}")
    print(f"  Local: {'✓' if llm_health.get('local') else '✗'}")

    print(f"\n{C.YELLOW}Commands:{C.RESET}")
    print(f"  {C.BOLD}scan <target>{C.RESET}       - Full pentest assessment")
    print(f"  {C.BOLD}recon <target>{C.RESET}      - Recon only (Operator layer)")
    print(f"  {C.BOLD}vuln <target>{C.RESET}       - Vulnerability assessment")
    print(f"  {C.BOLD}tool <tool> <target>{C.RESET} - Run a single tool")
    print(f"  {C.BOLD}agent <id> <task>{C.RESET}   - Run a single agent")
    print(f"  {C.BOLD}team{C.RESET}               - Show team status")
    print(f"  {C.BOLD}tools{C.RESET}              - Show tool status")
    print(f"  {C.BOLD}state{C.RESET}              - Show current state")
    print(f"  {C.BOLD}export{C.RESET}             - Export report")
    print(f"  {C.BOLD}help{C.RESET}               - Help")
    print(f"  {C.BOLD}quit{C.RESET}               - Exit")

    while True:
        try:
            prompt = f"\n{C.MAGENTA}cyber-agent{C.RESET} {C.DIM}>{C.RESET} "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            parts = user_input.split(maxsplit=2)
            cmd = parts[0].lower()

            # === KOMUTLAR ===

            if cmd in ("quit", "exit", "q"):
                print(f"\n{C.YELLOW}Closing session...{C.RESET}")
                await orchestrator.llm.close()
                break

            elif cmd == "scan" and len(parts) >= 2:
                target = parts[1]
                print_header(f"FULL ASSESSMENT: {target}")
                print(f"{C.DIM}This may take a few minutes...{C.RESET}")
                result = await orchestrator.run_full_assessment(target)
                print(f"\n{C.GREEN}✓ Assessment completed{C.RESET}")
                print(f"  Duration: {result['duration_seconds']}s")
                summary = result.get("summary", {})
                print(f"  Hosts: {summary.get('total_hosts', 0)}")
                print(f"  Vulnerabilities: {summary.get('total_vulnerabilities', 0)}")
                print(f"  Attack Paths: {summary.get('total_attack_paths', 0)}")
                print(f"  Critical Risks: {summary.get('critical_risks', 0)}")

            elif cmd == "recon" and len(parts) >= 2:
                target = parts[1]
                print_header(f"RECON: {target}")
                result = await orchestrator.run_recon_only(target)
                print(f"\n{C.GREEN}✓ Recon completed{C.RESET}")
                state = result.get("state", {})
                print(f"  Hosts: {len(state.get('hosts', []))}")
                print(f"  Ports: {len(state.get('ports', []))}")
                print(f"  Services: {len(state.get('services', []))}")

            elif cmd == "vuln" and len(parts) >= 2:
                target = parts[1]
                print_header(f"VULNERABILITY ASSESSMENT: {target}")
                result = await orchestrator.run_vuln_assessment(target)
                vulns = result.get("vulnerabilities", [])
                print(
                    f"\n{C.GREEN}✓ Completed - {len(vulns)} vulnerabilities found{C.RESET}"
                )

            elif cmd == "tool" and len(parts) >= 3:
                tool_name = parts[1]
                target = parts[2]
                print_header(f"TOOL: {tool_name} → {target}")
                result = await orchestrator.run_tool_scan(tool_name, target=target)
                if "error" in result:
                    print(f"{C.RED}✗ Error: {result['error']}{C.RESET}")
                else:
                    print(
                        f"{C.GREEN}✓ Completed ({result.get('duration_ms', 0)}ms){C.RESET}"
                    )
                    if result.get("output"):
                        print(
                            json.dumps(result["output"], indent=2, ensure_ascii=False)[
                                :2000
                            ]
                        )

            elif cmd == "agent" and len(parts) >= 3:
                agent_id = parts[1]
                task = parts[2]
                print_header(f"AGENT: {agent_id}")
                result = await orchestrator.run_single_agent(agent_id, task)
                print(f"  Status: {result.status}")
                if result.output:
                    print(f"  Output: {str(result.output)[:1000]}")
                if result.error:
                    print(f"  {C.RED}Error: {result.error}{C.RESET}")

            elif cmd == "team":
                print_header("AGENT TEAM STATUS")
                for agent_id, profile in TEAM_ROSTER.items():
                    print_agent(agent_id, profile)

            elif cmd == "tools":
                print_header("TOOL STATUS")
                print_tool_status(orchestrator.get_tool_status())

            elif cmd == "state":
                print_header("CURRENT STATE")
                state = orchestrator.get_state()
                print(
                    json.dumps(state, indent=2, ensure_ascii=False, default=str)[:3000]
                )

            elif cmd == "export":
                print_header("REPORT EXPORT")
                state = orchestrator.get_state()
                filename = (
                    f"pentest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                filepath = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "reports",
                    filename,
                )
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False, default=str)
                print(f"{C.GREEN}✓ Report saved: {filepath}{C.RESET}")

            elif cmd == "help":
                print(f"\n{C.BOLD}Usage Examples:{C.RESET}")
                print("  scan 192.168.1.0/24    - Full network assessment")
                print("  scan example.com       - Scan a domain")
                print("  recon 10.0.0.1         - Recon only")
                print("  vuln example.com       - Vulnerability scan")
                print("  tool nmap 192.168.1.1  - Run Nmap only")
                print("  tool nuclei example.com - Run Nuclei scan")
                print("  agent vulnerability_analysis 'Analyze services'")

            else:
                # Serbest metin: orkestratöre gönder
                print(f"{C.DIM}Orchestrator thinking...{C.RESET}")
                result = await orchestrator.run_single_agent("orchestrator", user_input)
                if result.output:
                    print(f"\n{C.CYAN}{result.output}{C.RESET}")
                if result.error:
                    print(f"{C.RED}Error: {result.error}{C.RESET}")

        except KeyboardInterrupt:
            print(f"\n{C.YELLOW}Cancelled.{C.RESET}")
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"{C.RED}Error: {e}{C.RESET}")
            logger.exception("CLI error")


def cli_main():
    """CLI giriş noktası."""
    parser = argparse.ArgumentParser(description="Cyber Agent Team CLI")
    parser.add_argument("--scan", help="Run full assessment on target")
    parser.add_argument("--recon", help="Run recon only")
    parser.add_argument("--tool", help="Run a tool (e.g., nmap)")
    parser.add_argument("--target", help="Target IP/domain")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logs")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.scan:

        async def run():
            orch = PurpleLeadOrchestrator()
            await orch.initialize()
            result = await orch.run_full_assessment(args.scan)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
            await orch.llm.close()

        asyncio.run(run())
    elif args.recon:

        async def run():
            orch = PurpleLeadOrchestrator()
            await orch.initialize()
            result = await orch.run_recon_only(args.recon)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
            await orch.llm.close()

        asyncio.run(run())
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    cli_main()
