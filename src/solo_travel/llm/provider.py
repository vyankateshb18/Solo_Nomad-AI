"""LLM Provider factory ensuring zero top-level side effects and local-first execution."""
from typing import Optional
from crewai import LLM
from solo_travel.config import LLMProviderType, Settings, get_settings


def get_llm(
    provider: Optional[LLMProviderType] = None,
    model_name: Optional[str] = None,
    settings: Optional[Settings] = None
) -> LLM:
    """
    Factory function to initialize a CrewAI LLM instance on-demand.
    Does NOT execute network requests during module import.
    """
    cfg = settings or get_settings()
    selected_provider = provider or cfg.DEFAULT_PROVIDER
    selected_model = model_name or cfg.DEFAULT_MODEL

    if selected_provider == LLMProviderType.OLLAMA:
        # Local Ollama - works completely offline without cloud API keys
        return LLM(
            model=f"ollama/{selected_model}",
            base_url=cfg.OLLAMA_BASE_URL,
            temperature=cfg.LLM_TEMPERATURE,
            timeout=cfg.LLM_TIMEOUT,
        )

    elif selected_provider == LLMProviderType.GROQ:
        if not cfg.GROQ_API_KEY:
            raise ValueError(
                "Groq provider selected but GROQ_API_KEY is not configured in environment or .env."
            )
        return LLM(
            model=f"groq/{selected_model}",
            api_key=cfg.GROQ_API_KEY,
            temperature=cfg.LLM_TEMPERATURE,
            timeout=cfg.LLM_TIMEOUT,
        )

    elif selected_provider == LLMProviderType.GEMINI:
        if not cfg.GEMINI_API_KEY:
            raise ValueError(
                "Gemini provider selected but GEMINI_API_KEY is not configured in environment or .env."
            )
        return LLM(
            model=f"gemini/{selected_model}",
            api_key=cfg.GEMINI_API_KEY,
            temperature=cfg.LLM_TEMPERATURE,
            timeout=cfg.LLM_TIMEOUT,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {selected_provider}")
