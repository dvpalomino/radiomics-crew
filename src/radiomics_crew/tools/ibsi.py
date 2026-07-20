"""IBSI / reporting-completeness checker.

Deliberately dumb by design: keyword matching over a Methods section, no LLM in the
loop. It answers one narrow question — *did the authors state this?* — and never
'did they do it correctly?'. Keeping the check deterministic means two runs of the
crew on the same paper produce the same checklist, so any disagreement between runs
comes from the agents' reasoning and not from the evidence underneath it.
"""

from __future__ import annotations

from functools import lru_cache

import yaml
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..settings import settings

CHECKLIST_PATH = settings.knowledge_dir / "ibsi_reporting_checklist.yaml"


@lru_cache(maxsize=1)
def _load_checklist() -> dict[str, list[dict]]:
    with CHECKLIST_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class IBSIChecklistInput(BaseModel):
    methods_text: str = Field(description="Raw Methods section text (or full abstract as a fallback)")
    stages: str = Field(
        default="all",
        description="Comma-separated stages to check, or 'all'. Options: acquisition, segmentation, "
        "preprocessing, extraction, harmonisation, modelling, reproducibility",
    )


class IBSIChecklistTool(BaseTool):
    name: str = "ibsi_reporting_checklist"
    description: str = (
        "Audit a Methods section against a condensed IBSI/METRICS-style reporting checklist. "
        "Returns REPORTED / NOT REPORTED per item plus a completeness score. "
        "It checks whether a choice was *stated*, never whether it was correct — do not overclaim from it."
    )
    args_schema: type[BaseModel] = IBSIChecklistInput

    def _run(self, methods_text: str, stages: str = "all") -> str:
        if not methods_text or len(methods_text) < 50:
            return "TOOL_ERROR: methods_text is too short to audit. Fetch the full text first."

        checklist = _load_checklist()
        wanted = (
            list(checklist)
            if stages.strip().lower() == "all"
            else [s.strip().lower() for s in stages.split(",") if s.strip().lower() in checklist]
        )
        if not wanted:
            return f"TOOL_ERROR: unknown stage(s) '{stages}'. Valid: {', '.join(checklist)}"

        haystack = methods_text.lower()
        lines: list[str] = []
        hits = total = 0
        missing: list[str] = []

        for stage in wanted:
            lines.append(f"\n[{stage.upper()}]")
            for entry in checklist[stage]:
                matched = [kw for kw in entry["keywords"] if kw in haystack]
                total += 1
                if matched:
                    hits += 1
                    lines.append(
                        f"  REPORTED     {entry['id']} — {entry['item']}  (matched: {', '.join(matched[:3])})"
                    )
                else:
                    missing.append(f"{entry['id']}: {entry['item']}")
                    lines.append(f"  NOT REPORTED {entry['id']} — {entry['item']}")

        score = 100 * hits / total if total else 0
        header = (
            f"Reporting completeness: {hits}/{total} items ({score:.0f}%)\n"
            f"Caveat: keyword-based. A REPORTED item means the wording is present, "
            f"not that the choice was sound."
        )
        tail = (
            "\n\nMost consequential gaps:\n" + "\n".join(f"  - {m}" for m in missing[:8]) if missing else ""
        )
        return header + "\n".join(lines) + tail
