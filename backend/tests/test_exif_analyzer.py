import pytest
from unittest.mock import patch, MagicMock

from app.modules.base import FindingResult
from app.modules.exif_analyzer import ExifAnalyzer


@pytest.fixture
def exif_analyzer():
    return ExifAnalyzer()


@pytest.mark.asyncio
async def test_exif_analyzer_no_images(exif_analyzer):
    results = await exif_analyzer.run({})
    assert results == []


@pytest.mark.asyncio
async def test_exif_analyzer_with_gps(exif_analyzer):
    mock_meta = {
        "GPSLatitude": 41.0082,
        "GPSLongitude": 28.9784,
        "Make": "Apple",
        "Model": "iPhone 14",
        "DateTimeOriginal": "2024:01:15 14:30:00",
    }
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout='[{"GPSLatitude": 41.0082, "GPSLongitude": 28.9784, "Make": "Apple", "Model": "iPhone 14", "DateTimeOriginal": "2024:01:15 14:30:00"}]',
            returncode=0,
        )
        results = await exif_analyzer.run({"images": ["/fake/path.jpg"]})

    assert len(results) >= 2
    gps = next((r for r in results if r.key == "gps_coordinates"), None)
    assert gps is not None
    assert gps.category == "location"
    assert gps.confidence == 0.98


@pytest.mark.asyncio
async def test_exif_analyzer_device_info(exif_analyzer):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout='[{"Make": "Canon", "Model": "EOS R5"}]',
            returncode=0,
        )
        results = await exif_analyzer.run({"images": ["/fake/path.jpg"]})

    device = next((r for r in results if r.key == "device"), None)
    assert device is not None
    assert "Canon" in device.value


def test_finding_result_dataclass():
    f = FindingResult(
        module="exif",
        category="location",
        key="test",
        value="val",
        confidence=0.9,
        source="test",
    )
    assert f.module == "exif"
    assert f.raw_data is None
