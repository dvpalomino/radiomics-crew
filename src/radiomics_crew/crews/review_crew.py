"""Literature review crew — sequential process.

Sequential is the right shape here because the work is a genuine pipeline: you cannot screen
what you have not searched, or appraise what you have not screened. The known cost, flagged in
the course, is context fade — the original question drifts as output passes down the chain — so
every task re-injects `{question}` and declares its upstream `context` explicitly.
"""

from __future__ import annotations

from crewai import Crew, Process, Task

from ..parsing import shape_hint
from ..schemas import EvidenceTable, ReviewReport, SearchStrategy
from ..settings import settings
from ..tools import EuropePMCFullTextTool, IBSIChecklistTool, PubMedFetchTool, PubMedSearchTool
from .base import build_agents, load_yaml

# The shape each task must return. NOT passed to the provider as a JSON Schema — see
# parsing.py. The model is rendered into the prompt as text and validated after the fact.
OUTPUT_MODELS = {
    "build_search_strategy": SearchStrategy,
    "screen_records": None,
    "appraise_methods": EvidenceTable,
    "write_review": ReviewReport,
}


def build_review_crew(question: str, scope: str = "no additional constraints", min_year: int = 2018) -> Crew:
    pubmed_search = PubMedSearchTool()
    pubmed_fetch = PubMedFetchTool()
    full_text = EuropePMCFullTextTool()
    ibsi = IBSIChecklistTool()

    agents = build_agents(
        settings.config_dir / "review" / "agents.yaml",
        tools_by_agent={
            "search_strategist": [pubmed_search],
            "evidence_screener": [pubmed_search, pubmed_fetch],
            "methods_appraiser": [pubmed_fetch, full_text, ibsi],
            "scientific_writer": [],  # the writer gets no search tools on purpose: it can only
        },                            # write from the evidence table, which makes fabrication harder
    )

    task_specs = load_yaml(str(settings.config_dir / "review" / "tasks.yaml"))
    inputs = {
        "question": question,
        "scope": scope,
        "min_year": str(min_year),
        "max_papers": str(settings.max_papers),
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
            agent=agents[spec["agent"]],
            context=[tasks[c] for c in spec.get("context", [])],
            output_file=spec.get("output_file"),
        )

    settings.ensure_dirs()
    return Crew(
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.sequential,
        memory=settings.use_memory,   # see Settings.use_memory: the default embedder is OpenAI's
        cache=True,    # PubMed answers do not change between tasks in a single run
        verbose=True,
    )
