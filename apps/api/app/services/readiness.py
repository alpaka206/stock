from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal

from app.config import Settings
from app.services.clients.alpha_vantage import AlphaVantageClient
from app.services.clients.open_dart import OpenDartClient
from app.services.clients.summary_router import ResearchSummaryClient
from app.services.errors import ExternalServiceError, ProviderConfigurationError
from app.services.prompt_loader import PromptLoader
from app.services.providers.factory import create_provider

ProbeMode = Literal["config", "remote"]


async def build_readiness_report(
    *,
    settings: Settings,
    prompt_loader: PromptLoader,
    probe: ProbeMode = "config",
) -> tuple[bool, dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append(_check_prompt_contracts(prompt_loader))
    checks.append(_check_provider_factory(settings))

    if settings.default_provider == "mock":
        ready = all(check["ok"] for check in checks)
        return ready, _build_report(settings=settings, probe=probe, checks=checks, ready=ready)

    checks.extend(_build_real_provider_checks(settings))

    if probe == "remote":
        checks.extend(await _run_remote_provider_probes(settings))

    ready = all(check["ok"] for check in checks if check.get("required", True))
    return ready, _build_report(settings=settings, probe=probe, checks=checks, ready=ready)


def _check_prompt_contracts(prompt_loader: PromptLoader) -> dict[str, Any]:
    try:
        page_keys = list(PromptLoader.PAGE_DIR_MAP.keys())
        for page_key in page_keys:
            prompt_loader.load_page(page_key)
        return {
            "name": "prompt-contracts",
            "ok": True,
            "detail": f"Loaded {len(page_keys)} prompt/contract bundles.",
            "required": True,
        }
    except FileNotFoundError as exc:
        return {
            "name": "prompt-contracts",
            "ok": False,
            "detail": f"Missing required prompt or contract file: {exc}",
            "required": True,
        }
    except Exception as exc:  # pragma: no cover
        return {
            "name": "prompt-contracts",
            "ok": False,
            "detail": f"Prompt/contract loading failed: {exc}",
            "required": True,
        }


def _check_provider_factory(settings: Settings) -> dict[str, Any]:
    try:
        provider = create_provider(settings.default_provider, settings)
        return {
            "name": "provider-factory",
            "ok": True,
            "detail": f"Created provider instance: {provider.__class__.__name__}.",
            "required": True,
        }
    except Exception as exc:  # pragma: no cover
        return {
            "name": "provider-factory",
            "ok": False,
            "detail": f"Provider creation failed: {exc}",
            "required": True,
        }


def _build_real_provider_checks(settings: Settings) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = [
        {
            "name": "env::ALPHA_VANTAGE_API_KEY",
            "ok": bool(settings.alpha_vantage_api_key),
            "detail": (
                "ALPHA_VANTAGE_API_KEY is configured."
                if settings.alpha_vantage_api_key
                else "ALPHA_VANTAGE_API_KEY is missing."
            ),
            "required": True,
        },
        {
            "name": "env::OPENDART_API_KEY",
            "ok": bool(settings.opendart_api_key),
            "detail": (
                "OPENDART_API_KEY is configured."
                if settings.opendart_api_key
                else "OPENDART_API_KEY is missing, so domestic disclosure coverage may be reduced."
            ),
            "required": False,
        },
    ]
    checks.extend(_build_llm_checks(settings))
    return checks


def _build_llm_checks(settings: Settings) -> list[dict[str, Any]]:
    if settings.llm_provider == "none":
        return [
            {
                "name": "llm-provider",
                "ok": True,
                "detail": "RESEARCH_LLM_PROVIDER=none, deterministic summaries only.",
                "required": False,
            }
        ]

    if settings.llm_provider == "openai":
        return [
            {
                "name": "env::OPENAI_API_KEY",
                "ok": bool(settings.openai_api_key),
                "detail": (
                    "OPENAI_API_KEY is configured."
                    if settings.openai_api_key
                    else "OPENAI_API_KEY is missing."
                ),
                "required": True,
            }
        ]

    if settings.llm_provider == "gemini":
        return [
            {
                "name": "env::GEMINI_API_KEY",
                "ok": bool(settings.gemini_api_key),
                "detail": (
                    "GEMINI_API_KEY is configured."
                    if settings.gemini_api_key
                    else "GEMINI_API_KEY is missing."
                ),
                "required": True,
            }
        ]

    configured = []
    if settings.openai_api_key:
        configured.append("openai")
    if settings.gemini_api_key:
        configured.append("gemini")
    if configured:
        detail = f"auto mode can use: {', '.join(configured)}."
    else:
        detail = "auto mode has no AI provider key, deterministic fallback only."
    return [
        {
            "name": "llm-provider",
            "ok": True,
            "detail": detail,
            "required": False,
        }
    ]


async def _run_remote_provider_probes(settings: Settings) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    alpha_client = AlphaVantageClient(
        api_key=settings.alpha_vantage_api_key,
        base_url=settings.alpha_vantage_base_url,
        timeout_seconds=settings.request_timeout_seconds,
        cache_ttl_seconds=settings.provider_cache_ttl_seconds,
    )
    checks.append(
        await _run_probe(
            name="provider::alpha-vantage",
            detail="Probe TIME_SERIES_DAILY MSFT with 2 candles.",
            probe=lambda: alpha_client.get_daily_series("MSFT", limit=2),
            required=True,
        )
    )

    if settings.opendart_api_key:
        open_dart_client = OpenDartClient(
            api_key=settings.opendart_api_key,
            base_url=settings.opendart_base_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        checks.append(
            await _run_probe(
                name="provider::opendart",
                detail="Probe one recent disclosure.",
                probe=lambda: open_dart_client.get_recent_disclosures(days=1, page_count=1),
                required=False,
            )
        )
    else:
        checks.append(
            {
                "name": "provider::opendart",
                "ok": True,
                "detail": "Skipped remote OpenDART probe because OPENDART_API_KEY is missing.",
                "required": False,
            }
        )

    llm_client = ResearchSummaryClient(
        llm_provider=settings.llm_provider,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
        gemini_api_key=settings.gemini_api_key,
        gemini_model=settings.gemini_model,
        gemini_base_url=settings.gemini_base_url,
        timeout_seconds=settings.request_timeout_seconds,
    )
    if llm_client.has_configured_provider() and settings.llm_provider != "none":
        checks.append(
            await _run_probe(
                name="provider::llm",
                detail="Probe configured LLM provider.",
                probe=llm_client.probe_health,
                required=False,
            )
        )
    else:
        checks.append(
            {
                "name": "provider::llm",
                "ok": True,
                "detail": "Skipped remote LLM probe because only deterministic fallback is available.",
                "required": False,
            }
        )

    return checks


async def _run_probe(
    *,
    name: str,
    detail: str,
    probe: Callable[[], Awaitable[Any]],
    required: bool,
) -> dict[str, Any]:
    try:
        result = await probe()
        result_size = len(result) if hasattr(result, "__len__") else 1
        return {
            "name": name,
            "ok": True,
            "detail": f"{detail} result_count={result_size}",
            "required": required,
        }
    except (ProviderConfigurationError, ExternalServiceError) as exc:
        return {
            "name": name,
            "ok": False,
            "detail": str(exc),
            "required": required,
        }
    except Exception as exc:  # pragma: no cover
        return {
            "name": name,
            "ok": False,
            "detail": f"{detail} failed with exception: {exc}",
            "required": required,
        }


def _build_report(
    *,
    settings: Settings,
    probe: ProbeMode,
    checks: list[dict[str, Any]],
    ready: bool,
) -> dict[str, Any]:
    return {
        "status": "ready" if ready else "not_ready",
        "providerMode": settings.default_provider,
        "llmProvider": settings.llm_provider,
        "probe": probe,
        "checks": checks,
    }

