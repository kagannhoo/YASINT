"""Tüm bulgulardan yapılandırılmış kimlik dosyası üretir."""

import json
import re
from typing import Any

from .base import BaseModule, FindingResult


class IdentityDossier(BaseModule):
    """Pasif OSINT sonuçlarını tek kimlik dosyasında birleştirir."""

    @property
    def module_name(self) -> str:
        return "dossier"

    async def run(self, inputs: dict) -> list[FindingResult]:
        findings = inputs.get("all_findings", [])
        if not findings:
            return []

        dossier = self._build_dossier(findings, inputs.get("initial_inputs", {}))

        return [
            FindingResult(
                module="dossier",
                category="identity",
                key="identity_dossier",
                value=dossier,
                confidence=0.9,
                source="Kimlik korelasyon motoru",
            ),
            FindingResult(
                module="dossier",
                category="identity",
                key="exposure_score",
                value=dossier["exposure_score"],
                confidence=0.85,
                source="Dijital maruziyet skoru",
                raw_data=dossier["risk_factors"],
            ),
        ]

    def _build_dossier(self, findings: list[dict], initial: dict) -> dict[str, Any]:
        emails: set[str] = set()
        usernames: set[str] = set()
        names: set[str] = set()
        phones: set[str] = set()
        locations: list[dict] = []
        social_profiles: list[dict] = []
        breaches: list[dict] = []
        registered_services: list[str] = []
        code_exposures: list[str] = []
        web_mentions: list[str] = []
        photos: list[str] = []
        ips: set[str] = set()

        if initial.get("email"):
            emails.add(initial["email"].lower())
        if initial.get("username"):
            usernames.add(initial["username"].strip().lstrip("@").lower())

        email_re = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

        for f in findings:
            module = f.get("module", "")
            key = f.get("key", "")
            value = f.get("value")
            raw = f.get("raw_data") or {}
            source = f.get("source", "")

            val = value
            if isinstance(value, str):
                try:
                    val = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass

            if key in ("email_found", "discovered_email") and isinstance(val, str):
                emails.add(val.lower())
            if key.startswith("account_") and isinstance(val, str) and val.startswith("http"):
                social_profiles.append({"platform": key.replace("account_", ""), "url": val, "source": source})
            if key == "real_name" and isinstance(val, str):
                names.add(val)
            if key == "github_name" and isinstance(val, str):
                names.add(val)
            if key in ("ip_geolocation", "gps_coordinates") and isinstance(val, dict):
                locations.append({**val, "source": source})
            if key == "breaches_found" and isinstance(raw, dict):
                breaches.extend(raw.get("breaches", []))
            if key == "registered_services" and isinstance(raw, dict):
                for svc in raw.get("services", []):
                    registered_services.append(svc.get("service", ""))
            if key in ("github_code_exposure", "public_code_mentions"):
                code_exposures.append(str(val))
            if key == "web_mention" and isinstance(val, str):
                web_mentions.append(val)
            if key == "profile_photo_url" and isinstance(val, str):
                photos.append(val)
            if key == "resolved_ip" and isinstance(val, str):
                ips.add(val)
            if key == "discovered_profile" and isinstance(val, str):
                social_profiles.append({"platform": "discovered", "url": val, "source": source})

            if isinstance(val, str):
                for e in email_re.findall(val):
                    if not e.endswith((".png", ".jpg", ".gif")):
                        emails.add(e.lower())

        risk_factors: list[str] = []
        if breaches:
            risk_factors.append(f"{len(breaches)} veri ihlalinde geçmiş")
        if code_exposures:
            risk_factors.append("Açık kaynak kodda kişisel bilgi sızıntısı")
        if len(social_profiles) > 5:
            risk_factors.append(f"{len(social_profiles)}+ sosyal medya profili açık")
        if emails:
            risk_factors.append(f"{len(emails)} e-posta adresi tespit edildi")
        if locations:
            risk_factors.append("Konum bilgisi maruz")

        exposure = min(
            0.2 * len(social_profiles)
            + 0.15 * len(emails)
            + 0.2 * len(breaches)
            + 0.1 * len(code_exposures)
            + 0.1 * len(locations)
            + 0.05 * len(web_mentions),
            1.0,
        )

        return {
            "summary": self._generate_summary(names, emails, social_profiles, breaches, initial),
            "identity": {
                "names": sorted(names),
                "emails": sorted(emails),
                "usernames": sorted(usernames),
                "phones": sorted(phones),
            },
            "digital_footprint": {
                "social_profiles": social_profiles[:30],
                "registered_services": registered_services,
                "web_mentions": web_mentions[:15],
                "code_exposures": code_exposures,
                "profile_photos": photos[:5],
            },
            "security": {
                "breaches": breaches,
                "risk_factors": risk_factors,
            },
            "network": {
                "ips": sorted(ips),
                "locations": locations,
            },
            "exposure_score": round(exposure, 2),
            "risk_factors": risk_factors,
            "stats": {
                "total_findings": len(findings),
                "social_count": len(social_profiles),
                "email_count": len(emails),
                "breach_count": len(breaches),
            },
        }

    def _generate_summary(
        self, names, emails, social_profiles, breaches, initial
    ) -> str:
        parts = []
        if names:
            parts.append(f"Tespit edilen isim(ler): {', '.join(names)}")
        if emails:
            parts.append(f"{len(emails)} e-posta adresi bulundu")
        if social_profiles:
            parts.append(f"{len(social_profiles)} sosyal medya profili aktif")
        if breaches:
            parts.append(f"{len(breaches)} veri ihlalinde kayıt var")
        if not parts:
            seed = initial.get("username") or initial.get("email") or "verilen ipucu"
            return f"'{seed}' için açık kaynak taraması tamamlandı; maruziyet sınırlı."
        return ". ".join(parts) + "."
