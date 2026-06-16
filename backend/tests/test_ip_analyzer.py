import pytest
from unittest.mock import AsyncMock, patch

from app.modules.ip_analyzer import IpAnalyzer


@pytest.fixture
def ip_analyzer():
    return IpAnalyzer()


@pytest.mark.asyncio
async def test_ip_analyzer_no_input(ip_analyzer):
    results = await ip_analyzer.run({})
    assert results == []


@pytest.mark.asyncio
async def test_ip_analyzer_with_geo(ip_analyzer):
    mock_geo = {
        "status": "success",
        "lat": 41.01,
        "lon": 28.97,
        "city": "Istanbul",
        "isp": "Turk Telekom",
        "org": "TTNet",
        "as": "AS9121 Turk Telekom",
    }

    with (
        patch(
            "app.modules.ip_analyzer.geo_lookup_free",
            new_callable=AsyncMock,
            return_value=mock_geo,
        ),
        patch(
            "app.modules.ip_analyzer.whois_lookup",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "app.modules.ip_analyzer.reverse_dns_lookup",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.modules.ip_analyzer.nmap_scan",
            new_callable=AsyncMock,
            return_value={"open_ports": [80, 443], "services": []},
        ),
    ):
        results = await ip_analyzer.run({"ip": "8.8.8.8"})

    assert any(r.key == "ip_geolocation" for r in results)
    assert any(r.key == "isp" for r in results)
    assert any(r.key == "open_ports" for r in results)
    assert all("Shodan" not in (r.source or "") for r in results)


@pytest.mark.asyncio
async def test_ip_analyzer_domain_resolution(ip_analyzer):
    with (
        patch("socket.gethostbyname", return_value="93.184.216.34"),
        patch(
            "app.modules.ip_analyzer.geo_lookup_free",
            new_callable=AsyncMock,
            return_value={},
        ),
        patch(
            "app.modules.ip_analyzer.whois_lookup",
            new_callable=AsyncMock,
            return_value={"registrar": "Example Registrar"},
        ),
        patch(
            "app.modules.ip_analyzer.reverse_dns_lookup",
            new_callable=AsyncMock,
            return_value="example.com",
        ),
        patch(
            "app.modules.ip_analyzer.nmap_scan",
            new_callable=AsyncMock,
            return_value={"open_ports": [], "services": []},
        ),
    ):
        results = await ip_analyzer.run({"ip": "example.com"})

    assert any(r.key == "resolved_ip" for r in results)
    assert any(r.key == "whois" for r in results)
