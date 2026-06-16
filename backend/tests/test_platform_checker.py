import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.utils.platform_checker import scan_username


@pytest.mark.asyncio
async def test_scan_username_returns_list():
    with patch("app.utils.platform_checker.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        async def fake_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 404
            resp.text = "not found"
            if "api.github.com" in url:
                resp.status_code = 200
                resp.text = '{"login": "testuser", "html_url": "https://github.com/testuser"}'
                resp.json = lambda: {"login": "testuser", "html_url": "https://github.com/testuser"}
            return resp

        mock_client.get = fake_get
        results = await scan_username("testuser")
        assert isinstance(results, list)
