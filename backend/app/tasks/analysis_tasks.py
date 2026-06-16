import asyncio

from .celery_app import celery_app
from ..modules.breach_checker import BreachChecker
from ..modules.domain_intel import DomainIntel
from ..modules.dork_searcher import DorkSearcher
from ..modules.email_hunter import EmailHunter
from ..modules.email_registration import EmailRegistrationChecker
from ..modules.enrichment import EnrichmentModule
from ..modules.exif_analyzer import ExifAnalyzer
from ..modules.face_analyzer import FaceAnalyzer
from ..modules.geo_estimator import GeoEstimator
from ..modules.identity_dossier import IdentityDossier
from ..modules.ip_analyzer import IpAnalyzer
from ..modules.llm_profiler import LLMProfiler
from ..modules.paste_searcher import PasteSearcher
from ..modules.phone_analyzer import PhoneAnalyzer
from ..modules.reverse_image import ReverseImageSearch
from ..modules.social_scraper import SocialScraper
from ..modules.username_hunter import UsernameHunter
from ..utils.enrichment import extract_seeds, has_new_seeds, merge_into_inputs
from ..utils.file_handler import delete_uploads_older_than
from ..utils.ws_broadcast import (
    broadcast_update,
    calculate_confidence,
    mark_analysis_status,
    save_findings,
)

MAX_ROUNDS = 3


def _has_email(inputs: dict) -> bool:
    return bool(inputs.get("email") or inputs.get("discovered_emails"))


def _has_identity_seed(inputs: dict) -> bool:
    return bool(
        inputs.get("username")
        or inputs.get("email")
        or inputs.get("discovered_emails")
        or inputs.get("images")
    )


def _build_modules(inputs: dict, round_num: int = 0) -> list:
    modules = []

    if inputs.get("images"):
        modules.extend([
            ExifAnalyzer(),
            FaceAnalyzer(),
            GeoEstimator(),
            ReverseImageSearch(),
        ])

    if inputs.get("username"):
        modules.append(UsernameHunter())
        modules.append(SocialScraper())

    if inputs.get("ip"):
        modules.append(IpAnalyzer())

    if inputs.get("phone"):
        modules.append(PhoneAnalyzer())

    if _has_email(inputs):
        modules.append(EmailHunter())
        modules.append(BreachChecker())
        modules.append(EmailRegistrationChecker())
        modules.append(DomainIntel())

    if inputs.get("url") or inputs.get("profile_urls"):
        if not any(isinstance(m, SocialScraper) for m in modules):
            modules.append(SocialScraper())

    # Derin OSINT — 2. turdan itibaren veya e-posta/kullanıcı adı varsa
    if round_num >= 1 or inputs.get("username") or _has_email(inputs):
        modules.append(PasteSearcher())
        modules.append(DorkSearcher())

    return _dedupe_modules(modules)


def _dedupe_modules(modules: list) -> list:
    seen: set[str] = set()
    unique = []
    for m in modules:
        if m.module_name not in seen:
            seen.add(m.module_name)
            unique.append(m)
    return unique


async def _run_module(module, inputs: dict):
    return await module.run(inputs)


async def _run_round(
    analysis_id: str,
    inputs: dict,
    round_num: int,
    all_findings: list[dict],
) -> list[dict]:
    modules = _build_modules(inputs, round_num)
    round_inputs = {**inputs, "all_findings": all_findings}
    all_round_findings: list[dict] = []

    if not modules:
        return all_round_findings

    tasks = []
    for module in modules:
        broadcast_update(analysis_id, module.module_name, [], status="running")
        tasks.append((module, _run_module(module, round_inputs)))

    results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

    for (module, _), result in zip(tasks, results):
        if isinstance(result, Exception):
            broadcast_update(
                analysis_id,
                module.module_name,
                [],
                error=str(result),
                status="failed",
            )
            continue

        findings = result
        finding_dicts = [f.__dict__ for f in findings]
        all_round_findings.extend(finding_dicts)
        save_findings(analysis_id, findings)
        broadcast_update(analysis_id, module.module_name, findings)

    return all_round_findings


@celery_app.task(bind=True)
def run_analysis(self, analysis_id: str, inputs: dict):
    """
    Çok turlu pasif OSINT pipeline:
    Tur 1 → kullanıcı ipucu
    Tur 2 → keşfedilen e-posta/URL/kullanıcı adı
    Tur 3 → derin tarama (paste, dork, breach, domain)
  Final → kimlik dosyası + AI özet
    """
    mark_analysis_status(analysis_id, "running")
    initial_inputs = dict(inputs)
    all_findings: list[dict] = []
    current_inputs = dict(inputs)

    async def run_all():
        nonlocal all_findings, current_inputs

        for round_num in range(MAX_ROUNDS):
            if round_num == 1:
                seeds = extract_seeds(all_findings, current_inputs)
                enriched = merge_into_inputs(current_inputs, seeds)
                if not has_new_seeds(current_inputs, enriched):
                    continue
                broadcast_update(analysis_id, "enrich", [], status="running")
                current_inputs = enriched

            round_findings = await _run_round(
                analysis_id, current_inputs, round_num, all_findings
            )
            all_findings.extend(round_findings)

        # Keşif özeti
        enricher = EnrichmentModule()
        try:
            enrich_findings = await enricher.run({
                **current_inputs,
                "all_findings": all_findings,
                "initial_inputs": initial_inputs,
            })
            enrich_dicts = [f.__dict__ for f in enrich_findings]
            all_findings.extend(enrich_dicts)
            save_findings(analysis_id, enrich_findings)
            broadcast_update(analysis_id, "enrich", enrich_findings)
        except Exception as e:
            broadcast_update(analysis_id, "enrich", [], error=str(e), status="failed")

        # Kimlik dosyası
        broadcast_update(analysis_id, "dossier", [], status="running")
        try:
            dossier = IdentityDossier()
            dossier_findings = await dossier.run({
                **current_inputs,
                "all_findings": all_findings,
                "initial_inputs": initial_inputs,
            })
            dossier_dicts = [f.__dict__ for f in dossier_findings]
            all_findings.extend(dossier_dicts)
            save_findings(analysis_id, dossier_findings)
            broadcast_update(analysis_id, "dossier", dossier_findings)
        except Exception as e:
            broadcast_update(analysis_id, "dossier", [], error=str(e), status="failed")

        # AI profil
        broadcast_update(analysis_id, "llm", [], status="running")
        try:
            profile = await LLMProfiler().run({
                **current_inputs,
                "all_findings": all_findings,
                "initial_inputs": initial_inputs,
            })
            profile_dicts = [f.__dict__ for f in profile]
            all_findings.extend(profile_dicts)
            save_findings(analysis_id, profile)
            broadcast_update(analysis_id, "llm", profile)
        except Exception as e:
            broadcast_update(analysis_id, "llm", [], error=str(e), status="failed")

        confidence = calculate_confidence(all_findings)
        mark_analysis_status(analysis_id, "completed", confidence)
        broadcast_update(analysis_id, "system", [], status="completed")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_all())
    except Exception as e:
        mark_analysis_status(analysis_id, "failed")
        broadcast_update(analysis_id, "system", [], error=str(e), status="failed")
    finally:
        loop.close()

    return {"analysis_id": analysis_id, "findings_count": len(all_findings)}


@celery_app.task
def cleanup_old_uploads():
    deleted = delete_uploads_older_than(hours=24)
    return {"deleted_directories": deleted}
