"""
AI Router — Tekil LLM Çağrı Yöneticisi (Strictly Sequential)
======================================================
AGENTS.md kuralı: "ASLA asyncio.gather() ile paralel LLM çağrısı yapma" ve "Tüm ajanlar SIRALI çalışır".
- Bu router sistemi sadece BİR çağrının yapılmasına izin verir.
- Model, görev tipine göre seçilir (get_model_for_task).
"""

import asyncio
import logging
import os
import time
from typing import Protocol


class AsyncCallFn(Protocol):
    """Protocol for async callback functions passed to AIRouter.route()."""

    async def __call__(self, *, api_key: str, model: str) -> object:
            ...


logger = logging.getLogger("cyber-agent.ai_router")

# ─────────────────────────────────────────────
# MODEL KATEGORİLERİ — görev → model grubu
# ─────────────────────────────────────────────

DEFAULT_MODEL = "gemma3:27b-cloud"

ALL_TASK_MODELS: dict[str, str] = {
    "vuln_analysis": "kimi-k2-thinking:cloud",
    "attack_path": "kimi-k2-thinking:cloud",
    "credential_check": "cogito-2.1:671b-cloud",
    "exposure_map": "mistral-large-3:675b-cloud",
    "mitigation": "mistral-large-3:675b-cloud",
    "report": "qwen3-coder:480b-cloud",
    "asset_correlation": "qwen3-coder-next:cloud",
    "risk_priority": "glm-4.7:cloud",
    "detection_gap": "deepseek-v3.2:cloud",
    "wireless_scan": DEFAULT_MODEL,
    "physical_recon": DEFAULT_MODEL,
    "network_scan": "devstral-small-2:24b-cloud",
    "passive_monitor": "nemotron-3-nano:30b-cloud",
}


def get_model_for_task(task_type: str) -> str:
    """Görev tipi → tek model. Bilinmiyorsa varsayılan."""
    model = ALL_TASK_MODELS.get(task_type, DEFAULT_MODEL)
    logger.debug(f"[Router] '{task_type}' → '{model}'")
    return model


class AIRouter:
    """
    Görev → model eşleştirici + Strict Sequential Call Enforcer.
    """

    def __init__(self) -> None:
        self._lock: asyncio.Lock = asyncio.Lock()  # Asla paralel çağrı yapılamaması için sıkı kilit
        self._api_key: str = os.getenv("OLLAMA_API_KEY", "").strip()

    async def route(
        self,
        task_type: str,
        call_fn: "AsyncCallFn",
        wait_time: float = 120.0,
    ) -> object:
        _ = wait_time  # unused parameter
        model = get_model_for_task(task_type)
        logger.info(f"[Router] Sıraya alındı: task='{task_type}', model='{model}'")

        # AGENTS.md rule: STRICTLY SEQUENTIAL
        async with self._lock:
            logger.info(f"[Router] Çalıştırılıyor: task='{task_type}', model='{model}'")
            start = time.monotonic()
            try:
                # Gerçekleştirilen çağrı
                result: object = await call_fn(api_key=self._api_key, model=model)
                return result
            except Exception as e:
                logger.error(f"[Router] Çağrı hatası: {e}")
                raise
            finally:
                elapsed = int((time.monotonic() - start) * 1000)
                logger.info(f"[Router] Tamamlandı: task='{task_type}', ms={elapsed}")


_router: AIRouter | None = None


def get_router() -> AIRouter:
    global _router
    if _router is None:
        _router = AIRouter()
    return _router
