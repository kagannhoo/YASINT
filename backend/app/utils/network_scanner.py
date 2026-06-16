import asyncio
import json
import re
import socket
from typing import Any

from ..config import get_settings


COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 8080, 8443]


async def reverse_dns_lookup(ip: str) -> str | None:
    try:
        loop = asyncio.get_event_loop()
        hostname, _, _ = await loop.run_in_executor(
            None, socket.gethostbyaddr, ip
        )
        return hostname
    except (socket.herror, socket.gaierror, OSError):
        return None


async def whois_lookup(target: str) -> dict[str, Any]:
    try:
        import whois

        loop = asyncio.get_event_loop()
        w = await loop.run_in_executor(None, whois.whois, target)
        if w is None:
            return {}

        result: dict[str, Any] = {}
        for field in [
            "domain_name",
            "registrar",
            "creation_date",
            "expiration_date",
            "name_servers",
            "org",
            "country",
            "emails",
        ]:
            val = getattr(w, field, None)
            if val is not None:
                if hasattr(val, "isoformat"):
                    val = val.isoformat()
                elif isinstance(val, list):
                    val = [str(v) for v in val[:5]]
                else:
                    val = str(val)
                result[field] = val
        return result
    except Exception:
        return {}


async def nmap_scan(target: str) -> dict[str, Any]:
    settings = get_settings()
    nmap_bin = settings.nmap_path

    try:
        proc = await asyncio.create_subprocess_exec(
            nmap_bin,
            "-Pn",
            "-sT",
            "-T4",
            "--top-ports",
            str(settings.nmap_top_ports),
            "-oX",
            "-",
            target,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
        xml_output = stdout.decode(errors="ignore")
        return _parse_nmap_xml(xml_output)
    except FileNotFoundError:
        return await _socket_port_scan(target)
    except Exception:
        return await _socket_port_scan(target)


def _parse_nmap_xml(xml_output: str) -> dict[str, Any]:
    import xml.etree.ElementTree as ET

    result: dict[str, Any] = {"open_ports": [], "services": []}
    if not xml_output.strip():
        return result

    try:
        root = ET.fromstring(xml_output)
        for host in root.findall("host"):
            for port in host.findall(".//port"):
                state = port.find("state")
                if state is not None and state.get("state") == "open":
                    port_id = int(port.get("portid", 0))
                    service = port.find("service")
                    svc_name = service.get("name", "unknown") if service is not None else "unknown"
                    result["open_ports"].append(port_id)
                    result["services"].append(
                        {"port": port_id, "service": svc_name, "protocol": port.get("protocol", "tcp")}
                    )
    except ET.ParseError:
        pass

    return result


async def _socket_port_scan(target: str) -> dict[str, Any]:
    """Nmap yoksa yaygın portlarda hızlı TCP bağlantı taraması."""
    open_ports: list[int] = []
    services: list[dict[str, Any]] = []

    async def check_port(port: int) -> None:
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(target, port),
                timeout=2.0,
            )
            writer.close()
            await writer.wait_closed()
            open_ports.append(port)
            services.append({"port": port, "service": "unknown", "protocol": "tcp"})
        except (OSError, asyncio.TimeoutError):
            pass

    await asyncio.gather(*[check_port(p) for p in COMMON_PORTS])
    open_ports.sort()
    return {"open_ports": open_ports, "services": services}


async def geo_lookup_free(ip: str) -> dict[str, Any]:
    """ip-api.com — ücretsiz, API anahtarı gerektirmez."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={
                    "fields": "status,message,country,countryCode,regionName,city,"
                    "lat,lon,timezone,isp,org,as,reverse,query"
                },
            )
            data = r.json()
            if data.get("status") == "success":
                return data
    except Exception:
        pass
    return {}


def is_valid_ip(value: str) -> bool:
    try:
        socket.inet_aton(value)
        return True
    except OSError:
        return False


def is_domain(value: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$", value))
