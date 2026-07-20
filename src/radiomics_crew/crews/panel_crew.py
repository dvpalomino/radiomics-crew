"""Expert panel crew — hierarchical process.

Hierarchical, not sequential, and for a specific reason: a consensus is not a pipeline. The
chair has to hold the original question while five specialists pull toward their own concerns,
send thin positions back for evidence, and decide when the disagreement is real. That is the
manager role the course describes, and it is what stops the run from degenerating into five
agents politely agreeing with whoever spoke last.
"""

from __future__ import annotations

from crewai import Crew, Process, Task

from ..parsing import shape_hint
from ..schemas import MethodsDecisionRecord
from ..settings import settings
from ..tools import EuropePMCFullTextTool, IBSIChecklistTool, PubMedFetchTool, PubMedSearchTool
from .base import build_agents, build_llm, load_yaml

OUTPUT_MODELS = {"adjudicate": MethodsDecisionRecord}


def build_panel_crew(
    question: str,
    context: str,
    options: list[str],
    tumour_site: str = "oncological",
    modality: str = "CT",
) -> Crew:
    search, fetch, full_text, ibsi = (
        PubMedSearchTool(),
        PubMedFetchTool(),
        EuropePMCFullTextTool(),
        IBSIChecklistTool(),
    )

    agents = build_agents(
        settings.config_dir / "panel" / "agents.yaml",
        tools_by_agent={
            "clinical_radiologist": [search, fetch],
            "radiomics_methodologist": [search, fetch, full_text, ibsi],
            "biostatistician": [search, fetch],
            "ml_engineer": [search, fetch, full_text],
            "regulatory_advisor": [search, fetch],
            "panel_chair": [],
        },
        allow_delegation=True,
        tumour_site=tumour_site,
        modality=modality,
    )

    chair = agents.pop("panel_chair")

    task_specs = load_yaml(str(settings.config_dir / "panel" / "tasks.yaml"))
    inputs = {
        "question": question,
        "context": context,
        "options": "; ".join(options),
    }

    tasks: dict[str, Task] = {}
    for name, spec in task_specs.items():
        description = spec["description"]
        for key, value in inputs.items():
            description = description.replace("{" + key + "}", value)
        expected = spec["expected_output"].strip()
        model = OUTPUT_MODELS.get(name)
        if model is not None:
            expected += (
                "\n\nReturn ONLY a JSON object with exactly this shape, no prose around it:\n"
                + shape_hint(model)
            )

        tasks[name] = Task(
            description=description.strip(),
            expected_output=expected,
            context=[tasks[c] for c in spec.get("context", [])],
            output_file=spec.get("output_file"),
        )  # no `agent=`: under Process.hierarchical the chair assigns the work

    settings.ensure_dirs()
    return Crew(
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.hierarchical,
        manager_agent=chair,
        manager_llm=build_llm("manager"),
        memory=settings.use_memory,
        cache=True,
        verbose=True,
    )
