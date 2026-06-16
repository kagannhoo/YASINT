import json

from ..config import get_settings
from .base import BaseModule, FindingResult


class LLMProfiler(BaseModule):
    @property
    def module_name(self) -> str:
        return "llm"

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.anthropic_api_key

    async def run(self, inputs: dict) -> list[FindingResult]:
        all_findings = inputs.get("all_findings", [])
        if not all_findings:
            return []

        if not self._api_key:
            return self._fallback_summary(all_findings)

        findings_text = json.dumps(all_findings, ensure_ascii=False, indent=2)
        initial = inputs.get("initial_inputs", {})
        initial_text = json.dumps(initial, ensure_ascii=False) if initial else "belirtilmedi"

        prompt = f"""Sen bir OSINT analistisin. Kullanıcı sadece BİR ipucu verdi; sistem otomatik olarak zincirleme keşif yaptı.
Önce kullanıcının ne verdiğine, sonra sistemin ne bulduğuna odaklan.

KULLANICININ VERDİĞİ İPUCU:
{initial_text}

TOPLANAN TÜM BULGULAR (otomatik keşif dahil):
{findings_text}

Bu verileri analiz ederek kapsamlı bir profil raporu oluştur.
Özellikle kullanıcının BİLMEDİĞİ ama sistemin BULDUĞU bilgileri öne çıkar.

Şu başlıklar altında JSON formatında yanıt ver:
{{
  "identity_summary": "Kişi hakkında genel özet (2-3 cümle)",
  "estimated_location": "Tahmini yaşam/çalışma yeri",
  "activity_pattern": "Aktivite saatleri ve günleri analizi",
  "digital_footprint": "Dijital ayak izi özeti",
  "behavioral_insights": ["Davranışsal içgörü 1", "..."],
  "confidence_assessment": {{
    "overall": 0.0,
    "location": 0.0,
    "identity": 0.0,
    "social": 0.0
  }},
  "key_findings": ["En önemli bulgu 1", "..."],
  "recommended_next_steps": ["Daha fazla araştırma için öneri 1", "..."],
  "risk_flags": ["Dikkat çekici nokta varsa"]
}}

Sadece JSON döndür, başka bir şey yazma."""

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self._api_key)
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            profile = json.loads(text.strip())
            return [
                FindingResult(
                    module="llm",
                    category="identity",
                    key="profile_summary",
                    value=profile,
                    confidence=0.85,
                    source="Claude AI Analysis",
                    raw_data={"model": "claude-sonnet-4-20250514"},
                )
            ]
        except Exception:
            return self._fallback_summary(all_findings)

    def _fallback_summary(self, all_findings: list) -> list[FindingResult]:
        discovered = [
            f"{f.get('module', '')}: {f.get('key', '')} = {str(f.get('value', ''))[:100]}"
            for f in all_findings
            if f.get("module") not in ("llm", "enrich")
        ][:15]
        modules_seen = sorted({f.get("module", "") for f in all_findings if f.get("module")})
        high_conf = [f for f in all_findings if (f.get("confidence") or 0) >= 0.8]

        return [
            FindingResult(
                module="llm",
                category="identity",
                key="profile_summary",
                value={
                    "identity_summary": (
                        f"Toplam {len(all_findings)} bulgu, {len(modules_seen)} modülden. "
                        + (
                            "Aşağıdaki bulgular otomatik keşif ile elde edildi."
                            if discovered
                            else "Henüz yeterli bulgu yok."
                        )
                    ),
                    "key_findings": discovered or ["Henüz bulgu yok"],
                    "digital_footprint": ", ".join(discovered[:5]) if discovered else "Veri yok",
                    "confidence_assessment": {
                        "overall": min(0.3 + len(high_conf) * 0.05, 0.85),
                        "location": 0.6 if any(f.get("module") == "geo" for f in all_findings) else 0.0,
                        "identity": 0.7 if discovered else 0.0,
                        "social": 0.75
                        if any(f.get("module") in ("username", "social") for f in all_findings)
                        else 0.0,
                    },
                    "recommended_next_steps": [
                        "Yüksek güvenli bulguları manuel doğrulayın",
                        "Keşfedilen e-posta ve kullanıcı adlarıyla ikinci tur analiz çalıştırın",
                    ],
                },
                confidence=0.55,
                source="YASINT otomatik özet",
                raw_data={"modules": modules_seen},
            )
        ]
