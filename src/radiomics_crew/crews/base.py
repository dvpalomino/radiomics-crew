"""Shared construction logic: YAML -> Agent objects.

Agents and tasks live in YAML rather than in Python so that changing a backstory is a
config change, not a code change. Prompt engineering is the actual work here; it should be
reviewable in a diff without reading around it.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from crewai import LLM, Agent

from ..settings import settings


@lru_cache(maxsize=16)
def load_yaml(path: str) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_llm(key: str = "worker") -> LLM:
    """One place to swap models. Workers run cheap; the manager runs on the strong model.

    The course's point that different agents can use different LLMs is not a cost trick —
    the chair has to hold the goal across a long hierarchical run, which is exactly where
    a weaker model drifts.
    """
    model = settings.manager_model if key == "manager" else settings.model

    # Some newer models (the reasoning-tier ones typically used for the manager) reject the
    # `temperature` parameter outright — the API returns "temperature is deprecated for this
    # model". Rather than hardcode a model list that goes stale, only send temperature when it
    # is configured, and let it be turned off per-run for models that refuse it.
    kwargs: dict[str, object] = {"max_tokens": settings.max_output_tokens}
    if settings.temperature is not None:
        kwargs["temperature"] = settings.temperature

    # The writer's report is long by design and was hitting the default output ceiling mid-JSON.
    return LLM(model=model, **kwargs)


def build_agents(
    config_path: Path,
    tools_by_agent: dict[str, list] | None = None,
    allow_delegation: bool = False,
    **template_vars: str,
) -> dict[str, Agent]:
    """Instantiate every agent declared in a YAML file.

    ``template_vars`` are substituted into role/goal/backstory so a single panel config can
    be pointed at pancreas-PET or rectum-MRI without duplicating the file.
    """
    raw = load_yaml(str(config_path))
    tools_by_agent = tools_by_agent or {}
    agents: dict[str, Agent] = {}

    for name, spec in raw.items():
        fields = {}
        for field_name in ("role", "goal", "backstory"):
            text = spec[field_name].strip()
            for key, value in template_vars.items():
                text = text.replace("{" + key + "}", str(value))
            fields[field_name] = text

        agents[name] = Agent(
            **fields,
            tools=tools_by_agent.get(name, []),
            llm=build_llm(spec.get("llm_key", "worker")),
            allow_delegation=allow_delegation,
            verbose=True,
            max_iter=12,  # guardrail: bounded reasoning, no infinite tool loops
            max_rpm=20,  # guardrail: stay inside provider and NCBI rate limits
        )
    return agents
