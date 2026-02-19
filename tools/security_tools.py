"""
Güvenlik Araç Entegrasyonları
Yazılım Araçları: Nmap, Nikto, SQLMap, Nuclei, OWASP ZAP, Trivy, Metasploit, Shodan, Burp Suite
Fiziksel Araçlar: Wi-Fi Pineapple, Flipper Zero, SharkTap
"""
import asyncio
import json
import logging
import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from config.settings import SECURITY_TOOLS

logger = logging.getLogger("cyber-agent.tools")


@dataclass
class ToolResult:
    tool_name: str
    command: str
    status: str  # success | error | timeout
    output: Any = None
    raw_output: str = ""
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "tool_name": self.tool_name,
            "command": self.command,
            "status": self.status,
            "output": self.output,
            "raw_output": self.raw_output[:2000],
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "error": self.error,
        }


class BaseTool(ABC):
    """Tüm araçların temel sınıfı."""

    def __init__(self, name: str, category: str, executable: str = None):
        self.name = name
        self.category = category
        self.executable = executable or name
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        return shutil.which(self.executable) is not None

    @abstractmethod
    async def run(self, **kwargs) -> ToolResult:
        pass

    async def _execute_command(
        self, cmd: List[str], timeout: int = 300
    ) -> ToolResult:
        """Shell komutu güvenli şekilde çalıştır (execFile tarzı, shell=False)."""
        start = datetime.now()
        command_str = " ".join(cmd)
        logger.info(f"[{self.name}] Çalıştırılıyor: {command_str}")

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            duration = int((datetime.now() - start).total_seconds() * 1000)

            if proc.returncode == 0:
                return ToolResult(
                    tool_name=self.name,
                    command=command_str,
                    status="success",
                    raw_output=stdout.decode("utf-8", errors="replace"),
                    duration_ms=duration,
                )
            else:
                return ToolResult(
                    tool_name=self.name,
                    command=command_str,
                    status="error",
                    raw_output=stdout.decode("utf-8", errors="replace"),
                    error=stderr.decode("utf-8", errors="replace"),
                    duration_ms=duration,
                )

        except asyncio.TimeoutError:
            return ToolResult(
                tool_name=self.name,
                command=command_str,
                status="timeout",
                error=f"Komut {timeout}s içinde tamamlanamadı",
                duration_ms=timeout * 1000,
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                command=command_str,
                status="error",
                error=str(e),
            )


# ============================================================
# NETWORK ARAÇLARI
# ============================================================

class NmapTool(BaseTool):
    """Nmap - Ağ keşfi ve port tarama."""

    def __init__(self):
        super().__init__("nmap", "network_discovery", SECURITY_TOOLS["nmap"]["path"])

    async def run(
        self,
        target: str,
        scan_type: str = "quick",
        ports: str = None,
        scripts: str = None,
        extra_args: List[str] = None,
    ) -> ToolResult:
        cmd = [self.executable]

        scan_profiles = {
            "quick": ["-sV", "-T4", "--top-ports", "1000"],
            "full": ["-sV", "-sC", "-p-", "-T4"],
            "stealth": ["-sS", "-T2", "--max-retries", "1"],
            "udp": ["-sU", "-T4", "--top-ports", "100"],
            "vuln": ["-sV", "--script", "vuln", "-T4"],
            "os": ["-O", "-sV", "-T4"],
            "aggressive": ["-A", "-T4"],
        }

        cmd.extend(scan_profiles.get(scan_type, scan_profiles["quick"]))

        if ports:
            cmd.extend(["-p", ports])
        if scripts:
            cmd.extend(["--script", scripts])
        if extra_args:
            cmd.extend(extra_args)

        cmd.extend(["-oX", "-"])
        cmd.append(target)

        result = await self._execute_command(cmd, timeout=600)

        if result.status == "success":
            result.output = self._parse_nmap_xml(result.raw_output)

        return result

    def _parse_nmap_xml(self, xml_data: str) -> Dict:
        """Basit Nmap XML parser."""
        import re
        hosts = []
        host_blocks = re.findall(r'<host.*?</host>', xml_data, re.DOTALL)
        for block in host_blocks:
            ip_match = re.search(r'addr="([^"]+)"', block)
            ports_found = re.findall(
                r'<port protocol="([^"]+)" portid="(\d+)".*?'
                r'state="([^"]+)".*?(?:name="([^"]*)")?',
                block, re.DOTALL
            )
            host = {
                "ip": ip_match.group(1) if ip_match else "unknown",
                "ports": [
                    {"protocol": p[0], "port": int(p[1]), "state": p[2], "service": p[3]}
                    for p in ports_found
                ],
            }
            hosts.append(host)
        return {"hosts": hosts, "total_hosts": len(hosts)}


class NucleiTool(BaseTool):
    """Nuclei - Template tabanlı zafiyet tarayıcı."""

    def __init__(self):
        super().__init__("nuclei", "vulnerability_scanner", SECURITY_TOOLS["nuclei"]["path"])

    async def run(
        self,
        target: str,
        templates: str = None,
        severity: str = None,
        tags: str = None,
        extra_args: List[str] = None,
    ) -> ToolResult:
        cmd = [self.executable, "-u", target, "-json", "-silent"]

        if templates:
            cmd.extend(["-t", templates])
        if severity:
            cmd.extend(["-severity", severity])
        if tags:
            cmd.extend(["-tags", tags])
        if extra_args:
            cmd.extend(extra_args)

        result = await self._execute_command(cmd, timeout=600)

        if result.status == "success":
            findings = []
            for line in result.raw_output.strip().split("\n"):
                if line.strip():
                    try:
                        findings.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            result.output = {"findings": findings, "total": len(findings)}

        return result


class NiktoTool(BaseTool):
    """Nikto - Web sunucu tarayıcı."""

    def __init__(self):
        super().__init__("nikto", "web_scanner", SECURITY_TOOLS["nikto"]["path"])

    async def run(self, target: str, port: int = 80, ssl: bool = False, **kwargs) -> ToolResult:
        cmd = [self.executable, "-h", target, "-p", str(port), "-Format", "json"]
        if ssl:
            cmd.append("-ssl")
        return await self._execute_command(cmd, timeout=600)


class SQLMapTool(BaseTool):
    """SQLMap - SQL injection test aracı."""

    def __init__(self):
        super().__init__("sqlmap", "sql_injection", SECURITY_TOOLS["sqlmap"]["path"])

    async def run(self, url: str, method: str = "GET", data: str = None, level: int = 1, **kwargs) -> ToolResult:
        cmd = [
            self.executable, "-u", url, "--batch", "--level", str(level),
            "--risk", "1", "--output-dir", "/tmp/sqlmap_output",
        ]
        if method.upper() == "POST" and data:
            cmd.extend(["--method", "POST", "--data", data])
        return await self._execute_command(cmd, timeout=300)


# ============================================================
# WEB GÜVENLİK ARAÇLARI
# ============================================================

class OWASPZapTool(BaseTool):
    """OWASP ZAP - Web uygulama güvenlik tarayıcı."""

    def __init__(self):
        super().__init__("zap", "web_security", SECURITY_TOOLS["zap"]["path"])

    async def run(self, target: str, scan_type: str = "quick", **kwargs) -> ToolResult:
        if scan_type == "quick":
            cmd = [self.executable, "quick-scan", "-s", "xss,sqli", target]
        elif scan_type == "full":
            cmd = [self.executable, "active-scan", target]
        elif scan_type == "spider":
            cmd = [self.executable, "spider", target]
        else:
            cmd = [self.executable, "quick-scan", target]
        return await self._execute_command(cmd, timeout=600)


# ============================================================
# KONTEYNER GÜVENLİĞİ
# ============================================================

class TrivyTool(BaseTool):
    """Trivy - Konteyner ve dosya sistemi zafiyet tarayıcı."""

    def __init__(self):
        super().__init__("trivy", "container_security", SECURITY_TOOLS["trivy"]["path"])

    async def run(self, target: str, scan_type: str = "image", severity: str = "CRITICAL,HIGH", **kwargs) -> ToolResult:
        cmd = [self.executable, scan_type, "--format", "json", "--severity", severity, target]
        result = await self._execute_command(cmd, timeout=300)
        if result.status == "success" and result.raw_output:
            try:
                result.output = json.loads(result.raw_output)
            except json.JSONDecodeError:
                pass
        return result


# ============================================================
# EXPLOITATION
# ============================================================

class MetasploitTool(BaseTool):
    """Metasploit Framework - bilgi toplama ve exploit modülleri."""

    def __init__(self):
        super().__init__("metasploit", "exploitation", SECURITY_TOOLS["metasploit"]["path"])

    async def run(self, resource_script: str = None, command: str = None, **kwargs) -> ToolResult:
        if resource_script:
            cmd = [self.executable, "-q", "-r", resource_script]
        elif command:
            cmd = [self.executable, "-q", "-x", command]
        else:
            return ToolResult(
                tool_name=self.name, command="", status="error",
                error="resource_script veya command gerekli",
            )
        return await self._execute_command(cmd, timeout=600)


# ============================================================
# OSINT / RECON
# ============================================================

class ShodanTool(BaseTool):
    """Shodan - İnternet genelinde cihaz/servis keşfi (Free Tier + Alternatifler)."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("SHODAN_API_KEY", "")
        super().__init__("shodan", "osint", SECURITY_TOOLS["shodan"]["path"])

    async def run(self, target: str = None, query: str = None, search_type: str = "host", **kwargs) -> ToolResult:
        """
        Shodan free tier sınırlamaları:
        - host: İP hakkında bilgi (myip, host lookup)
        - search: 1 sayfa (100 sonuç)
        - dns, malware, ssl desteği sınırlı
        
        Fallback: Alternatif OSINT araçlarını (whois, nslookup, curl) kullan
        """
        # CLI çalışmazsa, API fallback'i yap
        if search_type == "host" and target:
            # Önce CLI dene
            if self.is_available:
                cmd = [self.executable, "host", target]
                return await self._execute_command(cmd, timeout=120)
            # CLI yoksa, whois + nslookup kullan
            return await self._osint_fallback(target)
        elif search_type == "myip":
            # Free: Kendi IP'ni göster
            cmd = [self.executable, "myip"]
            return await self._execute_command(cmd, timeout=30)
        elif search_type == "dns" and target:
            # nslookup ile DNS resolve
            cmd = ["nslookup", target]
            return await self._execute_command(cmd, timeout=30)
        else:
            return ToolResult(tool_name=self.name, command="", status="error", error="target veya search_type gerekli")

    async def _osint_fallback(self, target: str) -> ToolResult:
        """Shodan CLI yoksa alternatif araçlar kullan (whois, nslookup, curl)."""
        tools_tried = []
        
        # 1. nslookup (DNS)
        try:
            result = await self._execute_command(["nslookup", target], timeout=30)
            if result.status == "success":
                tools_tried.append({"tool": "nslookup", "status": "success", "output": result.raw_output[:500]})
        except Exception as e:
            tools_tried.append({"tool": "nslookup", "status": "failed", "error": str(e)})
        
        # 2. whois (OSINT)
        if shutil.which("whois"):
            try:
                result = await self._execute_command(["whois", target], timeout=30)
                if result.status == "success":
                    tools_tried.append({"tool": "whois", "status": "success", "output": result.raw_output[:500]})
            except Exception as e:
                tools_tried.append({"tool": "whois", "status": "failed", "error": str(e)})
        
        # 3. curl (HTTP headers, SSL cert info)
        try:
            cmd = ["curl", "-v", f"http://{target}", "-m", "10"]
            result = await self._execute_command(cmd, timeout=15)
            if result.status in ["success", "error"]:
                tools_tried.append({"tool": "curl", "status": "success", "output": result.raw_output[:500]})
        except Exception as e:
            tools_tried.append({"tool": "curl", "status": "failed", "error": str(e)})
        
        return ToolResult(
            tool_name="shodan_fallback",
            command=f"osint_recon({target})",
            status="success",
            output={"osint_tools": tools_tried, "target": target},
            raw_output=json.dumps(tools_tried)
        )


class WhoisTool(BaseTool):
    """Whois - Domain/IP OSINT (Ücretsiz ve sınırsız)."""

    def __init__(self):
        super().__init__("whois", "osint", "whois")

    async def run(self, target: str, **kwargs) -> ToolResult:
        cmd = ["whois", target]
        result = await self._execute_command(cmd, timeout=30)
        if result.status == "success":
            # Parse WHOIS output
            lines = result.raw_output.split("\n")
            parsed = {
                "domain": target,
                "registrar": None,
                "creation_date": None,
                "expiration_date": None,
                "nameservers": []
            }
            for line in lines:
                if "Registrar:" in line:
                    parsed["registrar"] = line.split(":", 1)[1].strip()
                elif "Creation Date:" in line:
                    parsed["creation_date"] = line.split(":", 1)[1].strip()
                elif "Expiration Date:" in line or "Expire Date:" in line:
                    parsed["expiration_date"] = line.split(":", 1)[1].strip()
                elif "Name Server:" in line or "Nameserver:" in line:
                    parsed["nameservers"].append(line.split(":", 1)[1].strip())
            result.output = parsed
        return result


class DNSToolchain(BaseTool):
    """DNS Reconnaissance - nslookup, dig, host (Ücretsiz)."""

    def __init__(self):
        super().__init__("dns", "osint", "nslookup")

    async def run(self, target: str, record_type: str = "A", **kwargs) -> ToolResult:
        """DNS sorgula: A, AAAA, MX, TXT, NS"""
        cmd = ["nslookup", "-type=" + record_type, target]
        result = await self._execute_command(cmd, timeout=30)
        
        if result.status == "success":
            result.output = {
                "domain": target,
                "record_type": record_type,
                "raw_response": result.raw_output[:1000]
            }
        return result


# ============================================================
# FİZİKSEL PENTEST ARAÇLARI
# ============================================================

class WiFiPineappleTool(BaseTool):
    """Wi-Fi Pineapple Tactical VII entegrasyonu (REST API)."""

    def __init__(self, host: str = "172.16.42.1", api_key: str = None):
        self.host = host
        self.pineapple_api_key = api_key
        super().__init__("wifi-pineapple", "wireless")
        self.is_available = True  # API tabanlı

    async def run(self, action: str = "recon", duration: int = 30, **kwargs) -> ToolResult:
        import aiohttp

        base_url = f"http://{self.host}/api"
        headers = {}
        if self.pineapple_api_key:
            headers["Authorization"] = f"Bearer {self.pineapple_api_key}"

        endpoints = {
            "recon": "/recon/start",
            "recon_results": "/recon/results",
            "scan": "/recon/scan",
            "clients": "/clients",
            "status": "/status",
        }

        endpoint = endpoints.get(action, "/status")
        start = datetime.now()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{base_url}{endpoint}", headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    data = await resp.json()
                    duration_ms = int((datetime.now() - start).total_seconds() * 1000)
                    return ToolResult(
                        tool_name=self.name, command=f"GET {base_url}{endpoint}",
                        status="success", output=data, duration_ms=duration_ms,
                    )
        except Exception as e:
            return ToolResult(
                tool_name=self.name, command=f"GET {base_url}{endpoint}",
                status="error", error=str(e),
            )


class FlipperZeroTool(BaseTool):
    """Flipper Zero + WiFi Board entegrasyonu."""

    def __init__(self, port: str = "/dev/ttyACM0"):
        self.port = port
        super().__init__("flipper-zero", "physical")
        self.is_available = Path(port).exists() if port else False

    async def run(self, action: str = "info", subghz_freq: int = None, **kwargs) -> ToolResult:
        executable = os.getenv("FLIPPER_PATH", "flipper")
        flipper_commands = {
            "info": [executable, "info"],
            "subghz_scan": [executable, "subghz", "rx"],
            "nfc_scan": [executable, "nfc", "detect"],
            "rfid_scan": [executable, "rfid", "read"],
            "wifi_scan": [executable, "wifi", "scan"],
            "bt_scan": [executable, "bt", "scan"],
        }
        cmd = flipper_commands.get(action, [executable, "info"])
        if subghz_freq:
            cmd.extend(["--freq", str(subghz_freq)])

        if not shutil.which(executable):
            return await self._serial_command(action, **kwargs)
        return await self._execute_command(cmd, timeout=120)

    async def _serial_command(self, action: str, **kwargs) -> ToolResult:
        try:
            import serial
            ser = serial.Serial(self.port, 115200, timeout=10)
            ser.write(f"{action}\r\n".encode())
            await asyncio.sleep(2)
            response = ser.read_all().decode("utf-8", errors="replace")
            ser.close()
            return ToolResult(
                tool_name=self.name, command=f"serial:{action}",
                status="success", raw_output=response,
            )
        except ImportError:
            return ToolResult(
                tool_name=self.name, command=f"serial:{action}",
                status="error", error="pyserial yüklü değil: pip install pyserial",
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name, command=f"serial:{action}",
                status="error", error=str(e),
            )


class SharkTapTool(BaseTool):
    """SharkTap - Pasif ağ dinleme cihazı (tcpdump wrapper)."""

    def __init__(self, interface: str = "eth1"):
        self.interface = interface
        super().__init__("sharktap", "passive_network")
        self.is_available = shutil.which(os.getenv("TCPDUMP_PATH", "tcpdump")) is not None

    async def run(self, duration: int = 30, filter_expr: str = None, output_file: str = None, **kwargs) -> ToolResult:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_file or f"/tmp/sharktap_{ts}.pcap"
        tcpdump_path = os.getenv("TCPDUMP_PATH", "tcpdump")
        cmd = [tcpdump_path, "-i", self.interface, "-w", output_file, "-c", "10000"]
        if filter_expr:
            cmd.extend(filter_expr.split())
        result = await self._execute_command(cmd, timeout=duration + 10)
        result.output = {"pcap_file": output_file, "interface": self.interface}
        return result


# ============================================================
# ARAÇ FABRİKASI
# ============================================================

class ToolFactory:
    """Tüm araçları merkezi olarak yönetir."""

    _tools: Dict[str, BaseTool] = {}
    _physical_categories = {"wireless", "physical", "passive_network"}

    @classmethod
    def initialize(cls, shodan_api_key: str = None, pineapple_host: str = None):
        pine_host = pineapple_host or os.getenv("PINEAPPLE_HOST") or "172.16.42.1"
        flipper_port = os.getenv("FLIPPER_PORT", "/dev/ttyACM0")
        cls._tools = {
            # Network discovery
            "nmap": NmapTool(),
            # Vulnerability scanning
            "nuclei": NucleiTool(),
            "nikto": NiktoTool(),
            "sqlmap": SQLMapTool(),
            "zap": OWASPZapTool(),
            "trivy": TrivyTool(),
            # Exploitation
            "metasploit": MetasploitTool(),
            # OSINT - Shodan + Free alternatives
            "shodan": ShodanTool(api_key=shodan_api_key),
            "whois": WhoisTool(),
            "dns": DNSToolchain(),
            # Physical tools
            "wifi_pineapple": WiFiPineappleTool(host=pine_host),
            "flipper_zero": FlipperZeroTool(port=flipper_port),
            "sharktap": SharkTapTool(),
        }
        cls._apply_physical_tool_flags()
        for name, tool in cls._tools.items():
            status = "READY" if tool.is_available else "MISSING"
            logger.info(f"  [{status}] {name} ({tool.category})")
        return cls._tools

    @classmethod
    def _apply_physical_tool_flags(cls) -> None:
        enabled_all = os.getenv("PHYSICAL_TOOLS_ENABLED", "false").lower() in {"1", "true", "yes"}
        enabled_list_raw = os.getenv("PHYSICAL_TOOLS", "")
        enabled_list = {
            name.strip() for name in enabled_list_raw.split(",") if name.strip()
        }
        if enabled_all:
            return
        for name, tool in cls._tools.items():
            if tool.category in cls._physical_categories and name not in enabled_list:
                tool.is_available = False

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        return cls._tools.get(name)

    @classmethod
    def get_available(cls) -> Dict[str, BaseTool]:
        return {k: v for k, v in cls._tools.items() if v.is_available}

    @classmethod
    def get_by_category(cls, category: str) -> List[BaseTool]:
        return [t for t in cls._tools.values() if t.category == category]

    @classmethod
    def status_report(cls) -> List[Dict]:
        return [
            {"name": name, "category": tool.category, "available": tool.is_available}
            for name, tool in cls._tools.items()
        ]
