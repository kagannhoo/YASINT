from typing import Any

from .base import BaseModule, FindingResult


class FaceAnalyzer(BaseModule):
    @property
    def module_name(self) -> str:
        return "face"

    async def run(self, inputs: dict) -> list[FindingResult]:
        results: list[FindingResult] = []
        for image_path in inputs.get("images", []):
            results.extend(await self._analyze(image_path))
        return results

    async def _analyze(self, path: str) -> list[FindingResult]:
        findings: list[FindingResult] = []
        try:
            from deepface import DeepFace

            analysis: dict[str, Any] | list[dict[str, Any]] = DeepFace.analyze(
                img_path=path,
                actions=["age", "gender", "emotion", "race"],
                enforce_detection=False,
            )
            if isinstance(analysis, list):
                analysis = analysis[0]

            findings.append(
                FindingResult(
                    module="face",
                    category="identity",
                    key="estimated_age",
                    value=int(analysis.get("age", 0)),
                    confidence=0.75,
                    source="DeepFace age estimation",
                )
            )

            dominant_gender = analysis.get("dominant_gender", "")
            gender_scores = analysis.get("gender", {})
            gender_conf = (
                gender_scores.get(dominant_gender, 0) / 100
                if isinstance(gender_scores, dict)
                else 0.5
            )

            findings.append(
                FindingResult(
                    module="face",
                    category="identity",
                    key="gender",
                    value=dominant_gender,
                    confidence=gender_conf,
                    source="DeepFace gender classification",
                )
            )

            findings.append(
                FindingResult(
                    module="face",
                    category="identity",
                    key="dominant_emotion",
                    value=analysis.get("dominant_emotion"),
                    confidence=0.65,
                    source="DeepFace emotion analysis",
                )
            )

            region = analysis.get("region", {})
            findings.append(
                FindingResult(
                    module="face",
                    category="identity",
                    key="face_region",
                    value=region,
                    confidence=0.9,
                    source="DeepFace face detection",
                    raw_data={"full_analysis": analysis},
                )
            )
        except Exception:
            pass
        return findings
