import json
import subprocess
from typing import Any

from .base import BaseModule, FindingResult


class ExifAnalyzer(BaseModule):
    @property
    def module_name(self) -> str:
        return "exif"

    async def run(self, inputs: dict) -> list[FindingResult]:
        results: list[FindingResult] = []
        for image_path in inputs.get("images", []):
            results.extend(await self._analyze(image_path))
        return results

    async def _analyze(self, path: str) -> list[FindingResult]:
        findings: list[FindingResult] = []

        try:
            proc = subprocess.run(
                ["exiftool", "-json", "-n", path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            meta: dict[str, Any] = json.loads(proc.stdout)[0] if proc.stdout else {}
        except Exception:
            meta = {}

        lat = meta.get("GPSLatitude")
        lon = meta.get("GPSLongitude")
        if lat and lon:
            findings.append(
                FindingResult(
                    module="exif",
                    category="location",
                    key="gps_coordinates",
                    value={"lat": lat, "lon": lon},
                    confidence=0.98,
                    source="EXIF GPS metadata",
                    raw_data={
                        "altitude": meta.get("GPSAltitude"),
                        "speed": meta.get("GPSSpeed"),
                    },
                )
            )

        device = f"{meta.get('Make', '')} {meta.get('Model', '')}".strip()
        if device:
            findings.append(
                FindingResult(
                    module="exif",
                    category="identity",
                    key="device",
                    value=device,
                    confidence=0.99,
                    source="EXIF Make/Model",
                    raw_data={
                        "software": meta.get("Software"),
                        "firmware": meta.get("FirmwareVersion"),
                    },
                )
            )

        dt = meta.get("DateTimeOriginal") or meta.get("CreateDate")
        if dt:
            findings.append(
                FindingResult(
                    module="exif",
                    category="timeline",
                    key="capture_time",
                    value=dt,
                    confidence=0.99,
                    source="EXIF DateTimeOriginal",
                )
            )

        for field_name in ["LensModel", "FocalLength", "ExposureTime", "ISO"]:
            if meta.get(field_name):
                findings.append(
                    FindingResult(
                        module="exif",
                        category="identity",
                        key=field_name.lower(),
                        value=str(meta[field_name]),
                        confidence=0.9,
                        source="EXIF",
                    )
                )

        return findings
