"""Typed outputs. Agents are fuzzy; the artifacts they hand back should not be.

Design note on the sentinel strings below. The obvious way to model "the authors did not
report this" is `str | None`. It reads better in Python, but every optional field expands to
an `anyOf` branch in the JSON Schema, and once those sit inside a nested array of 20-field
objects the schema exceeds what the Anthropic API accepts ("Schema is too complex").

So optional fields carry an explicit "not reported" default instead of None. This is not
only a workaround: it makes the missing-data contract legible to the model, which now has to
write the words "not reported" rather than silently omitting a key. The rule the crew exists
to enforce — a missing field is data, never a plausible guess — survives intact.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

_MODALITIES = {"CT", "MRI", "PET", "PET/CT", "PET/MR", "US", "multimodal", "unclear"}


def _as_modality(value):
    """Real papers span modalities ("CT, MRI, PET/CT"). Forcing one value made the model choose
    between lying and failing. Accept a free string, but normalise the clean single-value case so
    the common path stays tidy."""
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    if not isinstance(value, str):
        return "unclear"
    cleaned = value.strip()
    return cleaned if cleaned else "unclear"


Confidence = Literal["low", "moderate", "high"]
Reported = Literal["yes", "no", "not stated"]

NR = "not reported"


def _as_str(value):
    """PMIDs and cohort sizes are numbers; a model writing them unquoted is correct, not wrong.

    These fields are typed as strings because they also have to hold "not reported" and things
    like "605 (2436 lesions)". Coerce the clean scalar case instead of rejecting the whole run.
    """
    if value is None:
        return NR
    if isinstance(value, (int, float)):
        return str(value)
    return value


def _as_list(value):
    """A model asked for a list will hand back a paragraph often enough to matter."""
    if isinstance(value, str):
        return [value] if value.strip() else []
    return value


def _as_confidence(value):
    """Coerce 'HIGH — because the full text was unavailable' to 'high'.

    The model is answering the question correctly and formatting it wrong. Recovering the intent
    beats discarding a run that cost real money — but only where the intent is unambiguous: the
    first word must actually be one of the allowed levels, otherwise this raises like anything else.
    """
    if not isinstance(value, str) or not value.strip():
        return "moderate"
    head = value.strip().lower().split()[0].strip(":-—,.")
    # "moderate" is the honest default for an unreadable confidence: it neither inflates nor
    # dismisses. Only a clear first-word level overrides it.
    return head if head in {"low", "moderate", "high"} else "moderate"


def _as_reported(value):
    """Map anything the model writes for ibsi_compliant onto yes / no / not stated.

    The safe default is "not stated": the whole point of this field is that an unverified claim
    must not read as a verified one. So only an explicit affirmative becomes "yes", only an
    explicit negative becomes "no", and everything else — "stated", "unknown", "n/a", a stray
    "not verifiable from abstract" — collapses to "not stated" rather than failing the run.
    """
    if value is None:
        return "not stated"
    if not isinstance(value, str):
        return value
    lowered = value.strip().lower()
    if lowered in {"yes", "true", "compliant", "ibsi-compliant", "ibsi compliant"}:
        return "yes"
    if lowered in {"no", "false", "non-compliant", "not compliant"}:
        return "no"
    return "not stated"


class SearchStrategy(BaseModel):
    """A search strategy that a human could re-run and reproduce."""

    question: str
    population: str
    index_test: str
    comparator: str
    outcome: str
    queries: list[str] = Field(description="Literal boolean queries actually executed, PubMed syntax")
    inclusion_criteria: list[str]
    exclusion_criteria: list[str]


class PaperCard(BaseModel):
    """One paper, reduced to the fields that decide whether it is usable.

    Every text field defaults to "not reported". Write that string when the source does not
    say; do not infer it from context.
    """

    pmid: str = NR
    title: str
    journal_year: str = Field(default=NR, description="e.g. 'Eur Radiol 2021'")
    modality: str = Field(
        default="unclear",
        description="One of CT/MRI/PET/PET-CT/US/multimodal, or a comma-list if the study spans several",
    )
    tumour_site: str = NR
    n_patients: str = Field(default=NR, description="Cohort size as stated, or 'not reported'")
    design: str = Field(default=NR, description="e.g. 'retrospective single-centre'")
    segmentation: str = Field(default=NR, description="Manual/semi-auto/DL; readers; agreement")
    preprocessing: str = Field(
        default=NR, description="Resampling, discretisation (FBN/FBS + value), normalisation"
    )
    harmonisation: str = Field(default=NR, description="ComBat, image-level, or 'none'")
    validation: str = Field(default=NR, description="Internal CV / hold-out / external cohort")
    main_result: str = NR
    ibsi_compliant: Reported = Field(default="not stated", description="'not stated' != 'no'")
    limitations: list[str] = Field(default_factory=list, description="Short bullets, one clause each")
    risk_of_bias: Confidence = Field(default="moderate", description="Level of concern, not level of quality")

    _coerce_strs = field_validator(
        "pmid",
        "n_patients",
        "title",
        "journal_year",
        "tumour_site",
        "design",
        "segmentation",
        "preprocessing",
        "harmonisation",
        "validation",
        "main_result",
        mode="before",
    )(_as_str)
    _coerce_modality = field_validator("modality", mode="before")(_as_modality)
    _coerce_limitations = field_validator("limitations", mode="before")(_as_list)
    _coerce_rob = field_validator("risk_of_bias", mode="before")(_as_confidence)
    _coerce_ibsi = field_validator("ibsi_compliant", mode="before")(_as_reported)


class ExcludedRecord(BaseModel):
    title: str
    reason: str = Field(description="Specific: 'review article', 'n<20', 'no features extracted'")


class EvidenceTable(BaseModel):
    included: list[PaperCard]
    excluded: list[ExcludedRecord] = Field(default_factory=list, description="Screening must be auditable")


class ReviewReport(BaseModel):
    """The deliverable of the ``review`` crew — the narrative half.

    Deliberately does NOT carry the evidence table. The appraiser already produced it as a
    typed artifact; making the writer restate it would double the token cost and push the
    JSON Schema past what the API accepts. The CLI recombines the two on the way out.
    """

    question: str
    n_screened: int
    n_included: int
    synthesis: str = Field(
        description="Narrative synthesis grouped by methodological choice, not paper by paper"
    )
    methodological_gaps: list[str] = Field(default_factory=list)
    reproducibility_concerns: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence_in_body_of_evidence: Confidence = "low"
    references: list[str] = Field(default_factory=list, description="Vancouver style, one per included paper")

    _coerce_lists = field_validator(
        "methodological_gaps", "reproducibility_concerns", "open_questions", "references", mode="before"
    )(_as_list)
    _coerce_confidence = field_validator("confidence_in_body_of_evidence", mode="before")(_as_confidence)


class PanelStatement(BaseModel):
    """One expert's position. Dissent is a feature, not noise to be averaged away."""

    role: str
    position: str = ""
    rationale: str = ""
    evidence: list[str] = Field(
        default_factory=list, description="PMIDs, or the literal string 'expert opinion, no citation'"
    )
    concerns_about_other_roles: list[str] = Field(default_factory=list)
    confidence: Confidence = "moderate"

    _coerce_evidence = field_validator("evidence", "concerns_about_other_roles", mode="before")(_as_list)
    _coerce_confidence = field_validator("confidence", mode="before")(_as_confidence)


class PanelStatements(BaseModel):
    """Wrapper for the collect_positions output — the five role statements before adjudication.

    Kept separate from MethodsDecisionRecord so the chair can leave the record's panel_statements
    empty (saving its output budget for the decision) and the CLI recombines the two afterwards.
    """

    statements: list[PanelStatement] = Field(default_factory=list)


class MethodsDecisionRecord(BaseModel):
    """ADR-style record for a methodological decision. The deliverable of ``panel``."""

    question: str
    context: str = ""
    options_considered: list[str] = Field(default_factory=list)
    panel_statements: list[PanelStatement] = Field(default_factory=list)
    points_of_disagreement: list[str] = Field(
        default_factory=list,
        description="Must be non-empty if the panel disagreed; do not manufacture false consensus",
    )
    consensus: str = ""
    recommended_protocol: list[str] = Field(
        default_factory=list, description="Ordered, executable steps — not principles"
    )
    reproducibility_requirements: list[str] = Field(
        default_factory=list, description="IBSI / CLAIM / TRIPOD+AI reporting items"
    )
    residual_risks: list[str] = Field(default_factory=list)
    revisit_if: list[str] = Field(
        default_factory=list, description="Conditions that would invalidate this decision"
    )
