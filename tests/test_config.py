"""Config-level tests: the prompts are the product, so they get tested like code."""

from __future__ import annotations

import re

import pytest
import yaml

from radiomics_crew.settings import settings

REVIEW = settings.config_dir / "review"
PANEL = settings.config_dir / "panel"


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", [REVIEW / "agents.yaml", PANEL / "agents.yaml"])
def test_agents_are_fully_specified(path):
    for name, spec in _load(path).items():
        assert {"role", "goal", "backstory"} <= set(spec), f"{name} is missing a field"
        assert len(spec["backstory"]) > 200, f"{name} has a thin backstory — specificity is the whole trick"


@pytest.mark.parametrize(
    "agents_path,tasks_path", [(REVIEW / "agents.yaml", REVIEW / "tasks.yaml")]
)
def test_review_tasks_reference_real_agents(agents_path, tasks_path):
    agents = set(_load(agents_path))
    tasks = _load(tasks_path)
    for name, spec in tasks.items():
        assert spec["agent"] in agents, f"task {name} points at unknown agent {spec['agent']}"
        for upstream in spec.get("context", []):
            assert upstream in tasks, f"task {name} has unknown context {upstream}"


def test_panel_tasks_have_no_agent_assigned():
    """Under Process.hierarchical the chair delegates. A hardcoded agent silently disables that."""
    for name, spec in _load(PANEL / "tasks.yaml").items():
        assert "agent" not in spec, f"panel task {name} must not pin an agent"


@pytest.mark.parametrize("path", [REVIEW / "tasks.yaml", PANEL / "tasks.yaml"])
def test_every_task_declares_expected_output(path):
    for name, spec in _load(path).items():
        assert spec.get("expected_output", "").strip(), f"{name} has no expected_output"


def test_review_placeholders_are_all_supplied():
    supplied = {"question", "scope", "min_year", "max_papers"}
    text = (REVIEW / "tasks.yaml").read_text()
    found = set(re.findall(r"\{(\w+)\}", text))
    assert found <= supplied, f"unsubstituted placeholders would reach the LLM: {found - supplied}"


def test_panel_placeholders_are_all_supplied():
    supplied = {"question", "context", "options", "tumour_site", "modality"}
    text = (PANEL / "tasks.yaml").read_text() + (PANEL / "agents.yaml").read_text()
    found = set(re.findall(r"\{(\w+)\}", text))
    assert found <= supplied, f"unsubstituted placeholders would reach the LLM: {found - supplied}"


def test_presets_are_answerable():
    from radiomics_crew.settings import ROOT

    presets = yaml.safe_load((ROOT / "examples" / "presets.yaml").read_text())
    assert presets
    for name, preset in presets.items():
        assert len(preset["options"]) >= 2, f"preset {name} gives the panel nothing to disagree about"
        assert preset["question"].strip() and preset["context"].strip()


def test_memory_is_not_hardcoded_on():
    """crewAI's default embedder is OpenAI's, so a hardcoded memory=True makes an
    OPENAI_API_KEY mandatory even for an Anthropic-only or fully local setup.
    This regressed once by being fixed on one machine and not in the repo."""
    for name in ("review_crew.py", "panel_crew.py"):
        source = (settings.config_dir.parent / "src" / "radiomics_crew" / "crews" / name).read_text()
        assert "memory=True" not in source, f"{name} hardcodes memory=True"
        assert "memory=settings.use_memory" in source, f"{name} must read memory from settings"
