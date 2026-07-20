"""Runtime settings, loaded from environment (.env) with sane defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Central configuration object. Never hardcode keys in code."""

    model: str = field(default_factory=lambda: os.getenv("RC_MODEL", "gpt-4o-mini"))
    manager_model: str = field(
        default_factory=lambda: os.getenv("RC_MANAGER_MODEL", os.getenv("RC_MODEL", "gpt-4o"))
    )
    temperature: float = field(default_factory=lambda: float(os.getenv("RC_TEMPERATURE", "0.2")))
    max_papers: int = field(default_factory=lambda: int(os.getenv("RC_MAX_PAPERS", "25")))

    # Off by default. crewAI's memory needs an embedder, and its default embedder is OpenAI's —
    # so leaving this on silently makes an OPENAI_API_KEY mandatory even for an Anthropic-only
    # or fully local setup. Little is lost: `cache=True` still prevents refetching, and every
    # task declares its upstream `context` explicitly, which is what actually carries the chain.
    use_memory: bool = field(default_factory=lambda: os.getenv("RC_MEMORY", "false").lower() == "true")

    # The writer emits a long structured report as one JSON object; the default provider ceiling
    # truncates it mid-object. 8192 fits the full report with headroom.
    max_output_tokens: int = field(default_factory=lambda: int(os.getenv("RC_MAX_OUTPUT_TOKENS", "8192")))

    # NCBI E-utilities is happier (and faster) with an identified caller.
    ncbi_email: str | None = field(default_factory=lambda: os.getenv("NCBI_EMAIL"))
    ncbi_api_key: str | None = field(default_factory=lambda: os.getenv("NCBI_API_KEY"))

    config_dir: Path = field(default_factory=lambda: ROOT / "config")
    knowledge_dir: Path = field(default_factory=lambda: ROOT / "knowledge")
    output_dir: Path = field(default_factory=lambda: ROOT / "outputs")

    def ensure_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
