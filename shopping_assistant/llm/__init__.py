"""
LLM client singleton — carrega configuração do agent_configs.yaml e inicializa
o modelo Ollama (ou qualquer provider compatível com a interface ChatOllama).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from langchain_ollama import ChatOllama


_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agent_configs.yaml"


def _load_config() -> dict:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def get_llm() -> Optional[ChatOllama]:
    """Retorna o cliente LLM configurado ou None se Ollama estiver indisponível."""
    config = _load_config()
    llm_cfg = config.get("llm", {})

    base_url = os.getenv("OLLAMA_BASE_URL", llm_cfg.get("base_url", "http://localhost:11434"))
    model = os.getenv("OLLAMA_MODEL", llm_cfg.get("model", "llama2:7b"))
    temperature = float(llm_cfg.get("temperature", 0.1))

    try:
        llm = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=temperature,
        )
        # Teste rápido de conectividade (sem gerar tokens)
        llm.invoke("ping")
        print(f"[LLMClient] Ollama conectado: model={model} base_url={base_url}")
        return llm
    except Exception as e:
        print(f"[LLMClient] AVISO: Ollama indisponível ({e}). Agentes usarão lógica determinística.")
        return None
