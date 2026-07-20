"""Command line entry point.

    python -m radiomics_crew review --question "..." --min-year 2019
    python -m radiomics_crew panel  --preset fbn_vs_fbs_ct
    python -m radiomics_crew panel  --question "..." --option A --option B --context "..."
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from .crews import build_panel_crew, build_review_crew
from .parsing import parse_as
from .render import record_to_markdown, review_to_markdown
import json_repair

from .schemas import (
    EvidenceTable,
    MethodsDecisionRecord,
    PanelStatement,
    ReviewReport,
    SearchStrategy,
)
from .settings import ROOT, settings

PRESETS_PATH = ROOT / "examples" / "presets.yaml"


def _load_preset(name: str) -> dict:
    presets = yaml.safe_load(PRESETS_PATH.read_text(encoding="utf-8"))
    if name not in presets:
        sys.exit(f"Unknown preset '{name}'. Available: {', '.join(presets)}")
    return presets[name]


def _write(stem: str, payload, markdown: str) -> None:
    settings.ensure_dirs()
    json_path = settings.output_dir / f"{stem}.json"
    md_path = settings.output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(payload.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    print(f"\nWrote {json_path}\nWrote {md_path}")


def run_review(args: argparse.Namespace) -> None:
    crew = build_review_crew(question=args.question, scope=args.scope, min_year=args.min_year)
    result = crew.kickoff()

    # The deliverable is assembled from three tasks, not one: the strategy (task 0) so the
    # search is re-runnable, the appraised table (task 2), and the narrative (task 3).
    strategy = parse_as(SearchStrategy, result.tasks_output[0].raw)
    table = parse_as(EvidenceTable, result.tasks_output[2].raw)
    report = parse_as(ReviewReport, result.raw)

    _write("review_report", report, review_to_markdown(report, table, strategy))
    (settings.output_dir / "evidence_table.json").write_text(
        json.dumps(table.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nUsage: {result.token_usage}")


def run_panel(args: argparse.Namespace) -> None:
    if args.preset:
        preset = _load_preset(args.preset)
        question, context, options = preset["question"], preset["context"], preset["options"]
        tumour_site, modality = preset.get("tumour_site", "oncological"), preset.get("modality", "CT")
    else:
        if not args.question or not args.option:
            sys.exit("Without --preset you must pass --question and at least two --option values.")
        question, context, options = args.question, args.context, args.option
        tumour_site, modality = args.tumour_site, args.modality

    crew = build_panel_crew(
        question=question, context=context, options=options, tumour_site=tumour_site, modality=modality
    )
    result = crew.kickoff()
    record = parse_as(MethodsDecisionRecord, result.raw)

    # The chair is told to leave panel_statements empty so it spends its output budget on the
    # decision (disagreements, consensus, protocol) rather than re-transcribing the five positions.
    # Recover them here from the collect_positions task, mirroring how the review recombines its
    # evidence table. Best-effort: if the shape differs, the record still stands on its synthesis.
    if not record.panel_statements and len(result.tasks_output) > 1:
        from .parsing import extract_json
        import json

        try:
            raw = extract_json(result.tasks_output[1].raw)
            data = json.loads(json_repair.repair_json(raw))
            items = data.get("statements", data) if isinstance(data, dict) else data
            record.panel_statements = [PanelStatement.model_validate(s) for s in items]
        except Exception:
            pass  # best-effort: the record still stands on its synthesis

    _write("methods_decision_record", record, record_to_markdown(record))
    print(f"\nUsage: {result.token_usage}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="radiomics_crew", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="Run the literature review crew")
    review.add_argument("--question", required=True)
    review.add_argument("--scope", default="no additional constraints")
    review.add_argument("--min-year", type=int, default=2018)
    review.set_defaults(func=run_review)

    panel = sub.add_parser("panel", help="Run the expert methodology panel")
    panel.add_argument("--preset", help=f"Name from {PRESETS_PATH.name}")
    panel.add_argument("--question")
    panel.add_argument("--context", default="")
    panel.add_argument("--option", action="append", help="Repeatable; one per option on the table")
    panel.add_argument("--tumour-site", default="oncological")
    panel.add_argument("--modality", default="CT")
    panel.set_defaults(func=run_panel)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
