"""Render the JSON artifacts into Markdown a human will actually read.

The pydantic object is what you diff and test against; the Markdown is what you paste
into a protocol document or a lab meeting.
"""

from __future__ import annotations

from .schemas import EvidenceTable, MethodsDecisionRecord, ReviewReport, SearchStrategy


def review_to_markdown(report: ReviewReport, table: EvidenceTable, strategy: SearchStrategy) -> str:
    lines = [
        "# Radiomics evidence review\n",
        f"**Question:** {report.question}\n",
        f"**Screened:** {report.n_screened} | **Included:** {report.n_included} "
        f"| **Confidence in body of evidence:** {report.confidence_in_body_of_evidence}\n",
        "## Search strategy\n",
    ]
    for query in strategy.queries:
        lines.append(f"- `{query}`")
    lines.append("\n**Inclusion:** " + "; ".join(strategy.inclusion_criteria))
    lines.append("\n**Exclusion:** " + "; ".join(strategy.exclusion_criteria))

    lines.append("\n## Evidence table\n")
    lines.append(
        "| PMID | Journal/Year | Modality | Site | n | Design "
        "| Preprocessing | Harmonisation | Validation | IBSI | RoB |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for paper in table.included:
        lines.append(
            f"| {paper.pmid} | {paper.journal_year} | {paper.modality} | {paper.tumour_site} "
            f"| {paper.n_patients} | {paper.design} | {paper.preprocessing} | {paper.harmonisation} "
            f"| {paper.validation} | {paper.ibsi_compliant} | {paper.risk_of_bias} |"
        )

    lines.append("\n## Synthesis\n")
    lines.append(report.synthesis)
    for title, items in (
        ("Methodological gaps", report.methodological_gaps),
        ("Reproducibility concerns", report.reproducibility_concerns),
        ("Open questions", report.open_questions),
    ):
        lines.append(f"\n## {title}\n")
        lines.extend(f"- {item}" for item in items)

    lines.append("\n## Excluded records\n")
    for row in table.excluded:
        lines.append(f"- {row.title} — _{row.reason}_")

    lines.append("\n## References\n")
    lines.extend(f"{i}. {ref}" for i, ref in enumerate(report.references, 1))
    return "\n".join(lines)


def record_to_markdown(record: MethodsDecisionRecord) -> str:
    lines = [
        "# Methods Decision Record\n",
        f"**Question:** {record.question}\n",
        f"**Context:** {record.context}\n",
        "## Options considered\n",
        *[f"- {option}" for option in record.options_considered],
        "\n## Panel positions\n",
    ]
    for statement in record.panel_statements:
        lines.append(f"### {statement.role}  \n*confidence: {statement.confidence}*\n")
        lines.append(f"**Position.** {statement.position}\n")
        lines.append(f"**Rationale.** {statement.rationale}\n")
        if statement.evidence:
            lines.append("**Evidence.** " + "; ".join(statement.evidence) + "\n")
        if statement.concerns_about_other_roles:
            lines.append("**Concerns raised.**")
            lines.extend(f"- {concern}" for concern in statement.concerns_about_other_roles)
            lines.append("")

    lines.append("## Points of disagreement\n")
    lines.extend(f"- {point}" for point in record.points_of_disagreement)
    lines.append(f"\n## Consensus\n\n{record.consensus}\n")
    lines.append("## Recommended protocol\n")
    lines.extend(f"{i}. {step}" for i, step in enumerate(record.recommended_protocol, 1))
    for title, items in (
        ("Reproducibility requirements", record.reproducibility_requirements),
        ("Residual risks", record.residual_risks),
        ("Revisit this decision if", record.revisit_if),
    ):
        lines.append(f"\n## {title}\n")
        lines.extend(f"- {item}" for item in items)
    return "\n".join(lines)
