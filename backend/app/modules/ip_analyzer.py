import asyncio

from .base import BaseModule, FindingResult
from ..config import get_settings
from ..utils.network_scanner import (
    geo_lookup_free,
    is_domain,
    is_valid_ip,
    nmap_scan,
    reverse_dns_lookup,
    whois_lookup,
)


async def _empty_scan() -> dict:
    return {"open_ports": [], "services": []}


class IpAnalyzer(BaseModule):
    """IP/domain analizi — tamamen açık kaynak ve ücretsiz araçlar."""

    @property
    def module_name(self) -> str:
        return "ip"

    async def run(self, inputs: dict) -> list[FindingResult]:
        target = inputs.get("ip", "").strip()
        if not target:
            return []

        resolve_target = target
        if is_domain(target) and not is_valid_ip(target):
            try:
                import socket

                resolve_target = socket.gethostbyname(target)
            except socket.gaierror:
                resolve_target = target

        findings: list[FindingResult] = []

        settings = get_settings()

        geo_task = geo_lookup_free(resolve_target)
        whois_task = whois_lookup(target)
        dns_task = reverse_dns_lookup(resolve_target)
        scan_task = (
            nmap_scan(resolve_target)
            if settings.port_scan_enabled
            else _empty_scan()
        )

        geo, whois_data, hostname, scan = await asyncio.gather(
            geo_task, whois_task, dns_task, scan_task
        )

        if is_domain(target) and resolve_target != target:
            findings.append(
                FindingResult(
                    module="ip",
                    category="network",
                    key="resolved_ip",
                    value=resolve_target,
                    confidence=0.95,
                    source="DNS resolution",
                    raw_data={"domain": target},
                )
            )

        if geo:
            if geo.get("lat") and geo.get("lon"):
                findings.append(
                    FindingResult(
                        module="ip",
                        category="location",
                        key="ip_geolocation",
                        value={"lat": geo["lat"], "lon": geo["lon"]},
                        confidence=0.75,
                        source="ip-api.com (ücretsiz)",
                        raw_data={
                            "city": geo.get("city"),
                            "region": geo.get("regionName"),
                            "country": geo.get("country"),
                            "timezone": geo.get("timezone"),
                        },
                    )
                )
            if geo.get("isp"):
                findings.append(
                    FindingResult(
                        module="ip",
                        category="network",
                        key="isp",
                        value=geo.get("isp"),
                        confidence=0.90,
                        source="ip-api.com",
                    )
                )
            if geo.get("org"):
                findings.append(
                    FindingResult(
                        module="ip",
                        category="network",
                        key="organization",
                        value=geo.get("org"),
                        confidence=0.85,
                        source="ip-api.com",
                    )
                )
            if geo.get("as"):
                findings.append(
                    FindingResult(
                        module="ip",
                        category="network",
                        key="asn",
                        value=geo.get("as"),
                        confidence=0.90,
                        source="ip-api.com",
                    )
                )

        if hostname:
            findings.append(
                FindingResult(
                    module="ip",
                    category="network",
                    key="reverse_dns",
                    value=hostname,
                    confidence=0.85,
                    source="Reverse DNS (socket)",
                )
            )

        if whois_data:
            findings.append(
                FindingResult(
                    module="ip",
                    category="network",
                    key="whois",
                    value=whois_data,
                    confidence=0.80,
                    source="python-whois (açık kaynak)",
                    raw_data=whois_data,
                )
            )

        open_ports = scan.get("open_ports", [])
        if open_ports:
            findings.append(
                FindingResult(
                    module="ip",
                    category="network",
                    key="open_ports",
                    value=open_ports,
                    confidence=0.90,
                    source="Nmap (açık kaynak)",
                    raw_data={"services": scan.get("services", [])},
                )
            )

        return findings
