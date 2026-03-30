#!/usr/bin/env python3
"""
Ollama Cloud MCP Server
=======================
Ollama Cloud modellerine MCP protokolü üzerinden erişim sağlar.
API: https://ollama.com/api (Bearer token auth)

Kurulum:
  pip install mcp httpx

Çalıştırma:
  export OLLAMA_API_KEY=your_key
  python ollama_mcp.py

Claude Code config (~/.claude.json):
  {
    "mcpServers": {
      "ollama": {
        "command": "python",
        "args": ["/path/to/ollama_mcp.py"],
        "env": {"OLLAMA_API_KEY": "your_key"}
      }
    }
  }
"""

import json
import os
from enum import Enum
from typing import List, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# ─── Server Init ─────────────────────────────────────────────
mcp = FastMCP("ollama_mcp")

# ─── Constants ───────────────────────────────────────────────
OLLAMA_CLOUD_URL = "https://ollama.com/api"
OLLAMA_LOCAL_URL = "http://localhost:11434/api"

# Kullanıcının yüklü cloud modelleri
AVAILABLE_CLOUD_MODELS = [
    "qwen3.5:cloud",
    "minimax-m2.5:cloud",
    "glm-5:cloud",
    "qwen3-coder-next:cloud",
    "glm-4.7:cloud",
    "kimi-k2.5:cloud",
    "kimi-k2-thinking:cloud",
    "minimax-m2:cloud",
    "minimax-m2.1:cloud",
    "qwen3-vl:235b-cloud",
    "qwen3-next:80b-cloud",
    "mistral-large-3:675b-cloud",
    "devstral-small-2:24b-cloud",
    "nemotron-3-nano:30b-cloud",
    "gemini-3-flash-preview:cloud",
    "cogito-2.1:671b-cloud",
    "qwen3-coder:480b-cloud",
    "gemma3:27b-cloud",
    "gemini-3-pro-preview:latest",
    "deepseek-v3.2:cloud",
]

# Görev → model önerileri
TASK_MODEL_SUGGESTIONS = {
    "reasoning": "kimi-k2-thinking:cloud",
    "coding": "qwen3-coder:480b-cloud",
    "coding_fast": "devstral-small-2:24b-cloud",
    "analysis": "mistral-large-3:675b-cloud",
    "general": "gemma3:27b-cloud",
    "vision": "qwen3-vl:235b-cloud",
    "fast": "nemotron-3-nano:30b-cloud",
    "large": "cogito-2.1:671b-cloud",
}


def _get_api_key() -> str:
    """OLLAMA_API_KEY env var'dan al."""
    return os.getenv("OLLAMA_API_KEY", "")


def _build_headers(api_key: str = None) -> dict:
    """Auth header oluştur."""
    key = api_key or _get_api_key()
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _handle_error(e: Exception) -> str:
    """Tutarlı hata mesajı formatı."""
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 401:
            return "Error: API key geçersiz. OLLAMA_API_KEY kontrol edin."
        elif e.response.status_code == 429:
            return "Error: Rate limit aşıldı. Bir süre bekleyin."
        elif e.response.status_code == 404:
            return f"Error: Model bulunamadı. ollama_list_models ile mevcut modelleri kontrol edin."
        return f"Error: API hatası [{e.response.status_code}]: {e.response.text[:200]}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: İstek zaman aşımına uğradı (300s). Model çok büyük olabilir."
    elif isinstance(e, httpx.ConnectError):
        return (
            "Error: Ollama Cloud'a bağlanılamadı. İnternet bağlantısını kontrol edin."
        )
    return f"Error: {type(e).__name__}: {str(e)[:300]}"


# ─── Pydantic Input Models ────────────────────────────────────


class ChatInput(BaseModel):
    """Chat completion için input."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    model: str = Field(
        ...,
        description="Ollama model adı (örn: 'kimi-k2-thinking:cloud', 'gemma3:27b-cloud'). ollama_list_models ile mevcut modelleri görün.",
        min_length=1,
    )
    message: str = Field(
        ...,
        description="Kullanıcı mesajı / prompt",
        min_length=1,
        max_length=100000,
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Sistem promptu (opsiyonel)",
        max_length=10000,
    )
    temperature: float = Field(
        default=0.7,
        description="Yaratıcılık seviyesi (0.0=deterministik, 1.0=maksimum yaratıcılık)",
        ge=0.0,
        le=2.0,
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maksimum token sayısı (opsiyonel, model limiti kullanılır)",
        ge=1,
        le=32000,
    )


class MultiTurnChatInput(BaseModel):
    """Çok turlu konuşma için input."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    model: str = Field(..., description="Ollama model adı")
    messages: List[dict] = Field(
        ...,
        description="Mesaj listesi: [{'role': 'user'/'assistant'/'system', 'content': '...'}]",
        min_length=1,
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class GenerateInput(BaseModel):
    """Basit text generation için input."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    model: str = Field(..., description="Ollama model adı")
    prompt: str = Field(
        ..., description="Tamamlanacak metin", min_length=1, max_length=50000
    )
    system: Optional[str] = Field(default=None, description="Sistem promptu")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class TaskRouteInput(BaseModel):
    """Görev tipine göre otomatik model seçimi."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    task_type: str = Field(
        ...,
        description="Görev tipi: reasoning | coding | coding_fast | analysis | general | vision | fast | large",
    )
    message: str = Field(..., description="Görev mesajı / prompt", min_length=1)
    system_prompt: Optional[str] = Field(default=None, description="Sistem promptu")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


# ─── Tools ───────────────────────────────────────────────────


@mcp.tool(
    name="ollama_list_models",
    annotations={
        "title": "Ollama Cloud Model Listesi",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def ollama_list_models() -> str:
    """
    Mevcut Ollama Cloud modellerini ve görev önerilerini listele.

    Returns:
        str: JSON formatında model listesi ve görev-model eşleştirmeleri.

    Kullanım:
        - Hangi modelin kullanılacağını bilmiyorsanız önce bunu çağırın.
        - ollama_chat veya ollama_generate çağrısından önce model adını doğrulayın.
    """
    try:
        # API'den canlı liste almayı dene
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{OLLAMA_CLOUD_URL}/tags",
                headers=_build_headers(),
                timeout=15.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                api_models = [m["name"] for m in data.get("models", [])]
            else:
                api_models = AVAILABLE_CLOUD_MODELS
    except Exception:
        api_models = AVAILABLE_CLOUD_MODELS

    result = {
        "cloud_models": api_models,
        "task_recommendations": TASK_MODEL_SUGGESTIONS,
        "tip": "ollama_task_route kullanarak görev tipine göre otomatik model seçimi yapabilirsiniz.",
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    name="ollama_chat",
    annotations={
        "title": "Ollama Cloud Chat",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def ollama_chat(params: ChatInput) -> str:
    """
    Ollama Cloud modeliyle tek turlu chat completion.

    Model seçim rehberi:
    - Derin düşünme/reasoning → kimi-k2-thinking:cloud
    - Büyük kod projeleri → qwen3-coder:480b-cloud
    - Hızlı kod görevleri → devstral-small-2:24b-cloud
    - Büyük analiz → mistral-large-3:675b-cloud veya cogito-2.1:671b-cloud
    - Görsel/resim → qwen3-vl:235b-cloud
    - Genel → gemma3:27b-cloud

    Args:
        params (ChatInput):
            - model: Model adı (zorunlu)
            - message: Kullanıcı mesajı (zorunlu)
            - system_prompt: Sistem promptu (opsiyonel)
            - temperature: 0.0-2.0 (varsayılan: 0.7)
            - max_tokens: Maksimum token (opsiyonel)

    Returns:
        str: JSON formatında model yanıtı.
            {
                "model": str,
                "content": str,
                "done": bool,
                "eval_count": int (token sayısı)
            }
    """
    messages = []
    if params.system_prompt:
        messages.append({"role": "system", "content": params.system_prompt})
    messages.append({"role": "user", "content": params.message})

    payload = {
        "model": params.model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": params.temperature},
    }
    if params.max_tokens:
        payload["options"]["num_predict"] = params.max_tokens

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_CLOUD_URL}/chat",
                json=payload,
                headers=_build_headers(),
                timeout=300.0,
            )
            resp.raise_for_status()
            data = resp.json()

        result = {
            "model": params.model,
            "content": data.get("message", {}).get("content", ""),
            "done": data.get("done", True),
            "eval_count": data.get("eval_count"),
            "total_duration_ms": (
                data.get("total_duration", 0) // 1_000_000
                if data.get("total_duration")
                else None
            ),
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ollama_chat_multi_turn",
    annotations={
        "title": "Ollama Cloud Çok Turlu Chat",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def ollama_chat_multi_turn(params: MultiTurnChatInput) -> str:
    """
    Ollama Cloud modeliyle çok turlu konuşma (tam mesaj geçmişi ile).

    Bir önceki konuşmayı bağlam olarak vermek istediğinizde kullanın.

    Args:
        params (MultiTurnChatInput):
            - model: Model adı
            - messages: [{"role": "user"/"assistant"/"system", "content": "..."}]
            - temperature: 0.0-2.0

    Returns:
        str: JSON formatında model yanıtı ve tam mesaj geçmişi.
    """
    payload = {
        "model": params.model,
        "messages": params.messages,
        "stream": False,
        "options": {"temperature": params.temperature},
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_CLOUD_URL}/chat",
                json=payload,
                headers=_build_headers(),
                timeout=300.0,
            )
            resp.raise_for_status()
            data = resp.json()

        assistant_msg = data.get("message", {})
        updated_history = params.messages + [assistant_msg]

        result = {
            "model": params.model,
            "content": assistant_msg.get("content", ""),
            "done": data.get("done", True),
            "eval_count": data.get("eval_count"),
            "full_history": updated_history,
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ollama_generate",
    annotations={
        "title": "Ollama Cloud Text Generation",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def ollama_generate(params: GenerateInput) -> str:
    """
    Ollama Cloud ile basit text completion (generate endpoint).
    Chat yerine doğrudan metin tamamlama için kullanın.

    Args:
        params (GenerateInput):
            - model: Model adı
            - prompt: Tamamlanacak metin
            - system: Sistem promptu (opsiyonel)
            - temperature: 0.0-2.0

    Returns:
        str: JSON formatında tamamlanmış metin.
    """
    payload = {
        "model": params.model,
        "prompt": params.prompt,
        "stream": False,
        "options": {"temperature": params.temperature},
    }
    if params.system:
        payload["system"] = params.system

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_CLOUD_URL}/generate",
                json=payload,
                headers=_build_headers(),
                timeout=300.0,
            )
            resp.raise_for_status()
            data = resp.json()

        result = {
            "model": params.model,
            "response": data.get("response", ""),
            "done": data.get("done", True),
            "eval_count": data.get("eval_count"),
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ollama_task_route",
    annotations={
        "title": "Görev Tipine Göre Otomatik Model Seçimi",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def ollama_task_route(params: TaskRouteInput) -> str:
    """
    Görev tipine göre otomatik model seçimi yaparak Ollama Cloud'a gönder.
    Hangi modeli kullanacağınızı bilmiyorsanız bu tool'u kullanın.

    Görev tipleri ve seçilen modeller:
    - reasoning   → kimi-k2-thinking:cloud  (derin düşünme, zor problemler)
    - coding      → qwen3-coder:480b-cloud  (büyük kod projeleri)
    - coding_fast → devstral-small-2:24b-cloud (hızlı kod snippets)
    - analysis    → mistral-large-3:675b-cloud (derin analiz)
    - general     → gemma3:27b-cloud (genel sorular)
    - vision      → qwen3-vl:235b-cloud (görsel içerik)
    - fast        → nemotron-3-nano:30b-cloud (hız öncelikli)
    - large       → cogito-2.1:671b-cloud (en büyük model)

    Args:
        params (TaskRouteInput):
            - task_type: reasoning|coding|coding_fast|analysis|general|vision|fast|large
            - message: Görev mesajı
            - system_prompt: Sistem promptu (opsiyonel)
            - temperature: 0.0-2.0

    Returns:
        str: JSON formatında seçilen model ve yanıt.
            {
                "selected_model": str,
                "task_type": str,
                "content": str,
                "eval_count": int
            }
    """
    model = TASK_MODEL_SUGGESTIONS.get(params.task_type, "gemma3:27b-cloud")

    messages = []
    if params.system_prompt:
        messages.append({"role": "system", "content": params.system_prompt})
    messages.append({"role": "user", "content": params.message})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": params.temperature},
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_CLOUD_URL}/chat",
                json=payload,
                headers=_build_headers(),
                timeout=300.0,
            )
            resp.raise_for_status()
            data = resp.json()

        result = {
            "selected_model": model,
            "task_type": params.task_type,
            "content": data.get("message", {}).get("content", ""),
            "done": data.get("done", True),
            "eval_count": data.get("eval_count"),
            "total_duration_ms": (
                data.get("total_duration", 0) // 1_000_000
                if data.get("total_duration")
                else None
            ),
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ollama_health_check",
    annotations={
        "title": "Ollama Cloud Bağlantı Kontrolü",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def ollama_health_check() -> str:
    """
    Ollama Cloud ve yerel Ollama bağlantı durumunu kontrol et.
    API key geçerliliğini ve erişilebilirliğini doğrular.

    Returns:
        str: JSON formatında bağlantı durumu.
            {
                "cloud": {"connected": bool, "api_key_set": bool, "model_count": int},
                "local": {"connected": bool},
                "recommendation": str
            }
    """
    cloud_status = {
        "connected": False,
        "api_key_set": bool(_get_api_key()),
        "model_count": 0,
    }
    local_status = {"connected": False}

    # Cloud check
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{OLLAMA_CLOUD_URL}/tags",
                headers=_build_headers(),
                timeout=10.0,
            )
            if resp.status_code == 200:
                cloud_status["connected"] = True
                cloud_status["model_count"] = len(resp.json().get("models", []))
    except Exception:
        pass

    # Local check
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_LOCAL_URL}/tags", timeout=5.0)
            local_status["connected"] = resp.status_code == 200
    except Exception:
        pass

    # Recommendation
    if cloud_status["connected"]:
        rec = "Cloud modellere erişim mevcut. ollama_chat veya ollama_task_route kullanın."
    elif local_status["connected"]:
        rec = "Sadece local Ollama erişilebilir. OLLAMA_API_KEY ayarlandı mı kontrol edin."
    else:
        rec = "Bağlantı yok. İnternet ve OLLAMA_API_KEY kontrol edin."

    result = {
        "cloud": cloud_status,
        "local": local_status,
        "recommendation": rec,
    }
    return json.dumps(result, indent=2, ensure_ascii=False)


# ─── Entry Point ──────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
