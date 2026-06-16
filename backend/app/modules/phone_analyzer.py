"""Telefon numarası pasif OSINT — phonenumbers + açık kaynak arama."""

import logging

from .base import BaseModule, FindingResult

logger = logging.getLogger(__name__)


class PhoneAnalyzer(BaseModule):
    @property
    def module_name(self) -> str:
        return "phone"

    async def run(self, inputs: dict) -> list[FindingResult]:
        phone = inputs.get("phone", "").strip()
        if not phone:
            return []

        findings: list[FindingResult] = []
        findings.extend(self._phonenumbers_analysis(phone))
        findings.extend(self._google_dork_hints(phone))
        return findings

    def _phonenumbers_analysis(self, phone: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        try:
            import phonenumbers
            from phonenumbers import carrier, geocoder, timezone as pn_tz

            # Türkiye numaraları için varsayılan ülke
            raw = phone.strip()
            if raw.startswith("0") and not raw.startswith("+"):
                normalized = "+90" + raw[1:]
            elif not raw.startswith("+"):
                normalized = "+" + raw
            else:
                normalized = raw

            try:
                parsed = phonenumbers.parse(normalized, None)
            except phonenumbers.NumberParseException:
                parsed = phonenumbers.parse(raw, "TR")

            if not phonenumbers.is_valid_number(parsed):
                findings.append(FindingResult(
                    module="phone", category="identity", key="validation",
                    value="Geçersiz veya tanınamayan numara formatı",
                    confidence=0.95, source="phonenumbers",
                ))
                return findings

            formatted = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            findings.append(FindingResult(
                module="phone", category="identity", key="valid_number",
                value=formatted, confidence=0.99, source="phonenumbers",
            ))

            region = (
                geocoder.description_for_number(parsed, "tr")
                or geocoder.description_for_number(parsed, "en")
            )
            if region:
                findings.append(FindingResult(
                    module="phone", category="location", key="region",
                    value=region, confidence=0.85, source="phonenumbers geocoder",
                ))

            op = (
                carrier.name_for_number(parsed, "tr")
                or carrier.name_for_number(parsed, "en")
            )
            if op:
                findings.append(FindingResult(
                    module="phone", category="network", key="carrier",
                    value=op, confidence=0.8, source="phonenumbers carrier",
                ))

            tzs = list(pn_tz.time_zones_for_number(parsed))
            if tzs:
                findings.append(FindingResult(
                    module="phone", category="timeline", key="timezone",
                    value=tzs, confidence=0.85, source="phonenumbers",
                ))

            type_map = {
                0: "Sabit hat",
                1: "Mobil",
                2: "Sabit/Mobil",
                3: "Ücretsiz hat",
                4: "Premium hat",
            }
            num_type = phonenumbers.number_type(parsed)
            findings.append(FindingResult(
                module="phone", category="identity", key="line_type",
                value=type_map.get(num_type, str(num_type)),
                confidence=0.9, source="phonenumbers",
            ))

            country = phonenumbers.region_code_for_number(parsed)
            if country:
                findings.append(FindingResult(
                    module="phone", category="location", key="country_code",
                    value=country, confidence=0.95, source="phonenumbers",
                ))

        except ImportError:
            findings.append(FindingResult(
                module="phone", category="identity", key="error",
                value="phonenumbers paketi yüklü değil",
                confidence=0.5, source="sistem",
            ))
        except Exception as e:
            logger.debug("phonenumbers error: %s", e)
        return findings

    def _google_dork_hints(self, phone: str) -> list[FindingResult]:
        """Manuel araştırma için Google dork linkleri (pasif OSINT)."""
        clean = phone.replace(" ", "").replace("-", "")
        dorks = [
            f'"{clean}"',
            f'"{clean}" site:facebook.com OR site:instagram.com',
            f'"{clean}" site:linkedin.com',
        ]
        findings = []
        for i, dork in enumerate(dorks):
            url = f"https://www.google.com/search?q={dork.replace(' ', '+')}"
            findings.append(FindingResult(
                module="phone", category="social",
                key=f"search_dork_{i}",
                value=url,
                confidence=0.5,
                source="Google dork (manuel kontrol)",
            ))
        return findings
