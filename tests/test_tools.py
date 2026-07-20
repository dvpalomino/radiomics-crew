"""Tests that run without network access or an API key.

The point is not coverage theatre: the IBSI checker is the one deterministic component in a
stochastic system, so it is the one component that can be pinned down by a test. If it drifts,
every downstream appraisal drifts with it, silently.
"""

from __future__ import annotations

import pytest
import yaml

from radiomics_crew.schemas import MethodsDecisionRecord, PaperCard, PanelStatement
from radiomics_crew.settings import settings
from radiomics_crew.tools import IBSIChecklistTool

WELL_REPORTED = """
    Images were acquired on a Siemens Somatom scanner at 120 kVp with a slice thickness of 1.0 mm
    in the portal venous phase after contrast administration. Two radiologists with 8 and 12 years
    of experience segmented the lesion manually in 3D Slicer; inter-observer agreement was assessed
    with the ICC. Volumes were resampled to 1x1x1 mm with a B-spline interpolator and discretised
    using a fixed bin width of 25 HU. Features were extracted with PyRadiomics version 3.0.1 in an
    IBSI-compliant configuration; the parameter file is provided as supplementary material. Batch
    effects were corrected with ComBat. Feature selection (LASSO) was performed inside the
    cross-validation loop, and the model was assessed on an external validation cohort with the AUC
    reported with a 95% CI and a calibration curve. Code is available on GitHub. The study was
    approved by the institutional review board and informed consent was waived.
"""

POORLY_REPORTED = """
    Radiomic features were extracted from the tumour region using PyRadiomics. A random forest was
    trained and achieved an AUC of 0.89, showing the excellent potential of radiomics.
"""


def test_checklist_yaml_is_wellformed():
    data = yaml.safe_load((settings.knowledge_dir / "ibsi_reporting_checklist.yaml").read_text())
    assert set(data) >= {"acquisition", "segmentation", "preprocessing", "extraction", "modelling"}
    for stage, entries in data.items():
        for entry in entries:
            assert {"id", "item", "keywords"} <= set(entry), f"malformed entry in {stage}"
            assert entry["keywords"], f"{entry['id']} has no keywords"
            assert all(kw == kw.lower() for kw in entry["keywords"]), f"{entry['id']} keywords must be lowercase"


def test_checklist_ids_are_unique():
    data = yaml.safe_load((settings.knowledge_dir / "ibsi_reporting_checklist.yaml").read_text())
    ids = [entry["id"] for entries in data.values() for entry in entries]
    assert len(ids) == len(set(ids))


def test_well_reported_methods_score_high():
    result = IBSIChecklistTool()._run(WELL_REPORTED)
    score = int(result.split("(")[1].split("%")[0])
    assert score >= 80, result


def test_poorly_reported_methods_score_low():
    result = IBSIChecklistTool()._run(POORLY_REPORTED)
    score = int(result.split("(")[1].split("%")[0])
    assert score <= 30, result
    assert "NOT REPORTED PRE-2" in result  # discretisation never mentioned


def test_checklist_rejects_stub_input():
    assert IBSIChecklistTool()._run("too short").startswith("TOOL_ERROR")


def test_checklist_rejects_unknown_stage():
    assert IBSIChecklistTool()._run(WELL_REPORTED, stages="astrology").startswith("TOOL_ERROR")


def test_stage_filter_narrows_output():
    result = IBSIChecklistTool()._run(WELL_REPORTED, stages="preprocessing")
    assert "[PREPROCESSING]" in result and "[MODELLING]" not in result


def test_papercard_defaults_to_unknown_not_to_plausible():
    """A missing field must stay missing. Silent defaults are how fabrications get published."""
    card = PaperCard(title="Some radiomics paper")
    assert card.n_patients == "not reported"
    assert card.ibsi_compliant == "not stated"  # not "no" — unstated and non-compliant differ
    assert card.modality == "unclear"


def test_schemas_stay_within_provider_complexity_limits():
    """Anthropic rejects deeply nested tool schemas with 'Schema is too complex'.

    This is the test that was missing when it bit us: the models validated fine in Python
    while the JSON Schema they serialise to was rejected by the API. Guard the artifact the
    provider actually sees, not the class.
    """
    import json

    from radiomics_crew.schemas import EvidenceTable, ReviewReport, SearchStrategy

    for model in (ReviewReport, SearchStrategy, MethodsDecisionRecord, EvidenceTable):
        schema = json.dumps(model.model_json_schema())
        assert len(schema) < 3000, f"{model.__name__} schema is {len(schema)} chars — flatten it"

    # The writer's output must stay flat: no nested model definitions at all.
    assert "$defs" not in json.dumps(ReviewReport.model_json_schema())


def test_decision_record_requires_a_protocol():
    with pytest.raises(Exception):
        MethodsDecisionRecord(
            question="q", context="c", options_considered=["a", "b"],
            panel_statements=[PanelStatement(role="r", position="p", rationale="why")],
            points_of_disagreement=["d"], consensus="c",
            # recommended_protocol omitted on purpose
            reproducibility_requirements=["x"], residual_risks=["y"], revisit_if=["z"],
        )


def test_no_pydantic_schema_reaches_the_provider():
    """The 'Schema is too complex' failure came from output_pydantic serialising a model into
    a JSON Schema the API refused. Validation now happens in parsing.py instead. If someone
    reintroduces output_pydantic, it breaks on Anthropic only at runtime — so catch it here."""
    from radiomics_crew.settings import ROOT

    for name in ("review_crew.py", "panel_crew.py"):
        source = (ROOT / "src" / "radiomics_crew" / "crews" / name).read_text()
        assert "output_pydantic" not in source, f"{name} sends a schema to the provider"


def test_parse_as_survives_fenced_and_chatty_output():
    from radiomics_crew.parsing import parse_as
    from radiomics_crew.schemas import PaperCard

    chatty = 'Sure! Here is the card:\n```json\n{"title": "A paper", "pmid": "123"}\n```\nHope that helps!'
    card = parse_as(PaperCard, chatty)
    assert card.title == "A paper" and card.pmid == "123"
    assert card.n_patients == "not reported"  # the missing-is-data contract still holds


def test_parse_as_refuses_junk_loudly():
    """json_repair will turn prose into an empty string rather than admit defeat, so the repair
    step must never be the last line of defence — pydantic still has to reject it."""
    from radiomics_crew.parsing import parse_as
    from radiomics_crew.schemas import PaperCard

    with pytest.raises(ValueError, match="did not match|not recoverable"):
        parse_as(PaperCard, "I could not complete this task.")


def test_shape_hint_carries_field_descriptions_into_the_prompt():
    from radiomics_crew.parsing import shape_hint
    from radiomics_crew.schemas import PaperCard

    hint = shape_hint(PaperCard)
    assert '"ibsi_compliant"' in hint
    assert "not stated" in hint  # the description is the instruction; it must survive


def test_shape_hint_lists_literal_options():
    """A Literal rendered as '<one of>' tells the model nothing and it invents a value that
    then fails validation. The allowed values must reach the prompt."""
    from radiomics_crew.parsing import shape_hint
    from radiomics_crew.schemas import EvidenceTable, PaperCard, ReviewReport

    hint = shape_hint(PaperCard)
    assert '"yes" | "no" | "not stated"' in hint       # ibsi_compliant stays a strict enum
    assert '"low" | "moderate" | "high"' in hint        # risk_of_bias too
    assert "[str, ...]" in hint  # lists render their element type

    assert '"low" | "moderate" | "high"' in shape_hint(ReviewReport)
    assert "one of" not in shape_hint(EvidenceTable)  # the old placeholder must be gone


def test_parse_as_repairs_llm_json_syntax():
    """A 15k-char JSON written token-by-token drops a comma eventually. That is a property of
    the medium, not a prompt bug — repair it rather than losing a paid run."""
    from radiomics_crew.parsing import parse_as
    from radiomics_crew.schemas import EvidenceTable

    broken = '{"included": [{"title": "A", "pmid": "1",}, {"title": "B" "pmid": "2"}]}'
    table = parse_as(EvidenceTable, broken)
    assert [p.title for p in table.included] == ["A", "B"]


def test_papercard_coerces_the_mistakes_models_actually_make():
    """Reproduces a real failed run: a paragraph where a list was asked for, and an enum value
    with an explanation welded onto it."""
    from radiomics_crew.parsing import parse_as
    from radiomics_crew.schemas import PaperCard

    card = parse_as(PaperCard, """{
        "pmid": "38294307", "title": "Precise 3D CT Radiomics",
        "limitations": "NOT_OPEN_ACCESS: full text unavailable. Completeness 23%.",
        "risk_of_bias": "HIGH — Absence of full-text verification prevents assessment.",
        "ibsi_compliant": "not stated"
    }""")
    assert card.risk_of_bias == "high"
    assert card.limitations == ["NOT_OPEN_ACCESS: full text unavailable. Completeness 23%."]


def test_enums_default_instead_of_crashing_on_garbage():
    """A model that writes 'stated' for ibsi_compliant or a sentence for risk_of_bias must not
    kill a paid run. The enums coerce to a safe default — 'not stated' and 'moderate', the values
    that neither inflate nor dismiss — rather than raising. This was a real failure: 'stated'
    fell through a startswith() gap and crashed the whole review at the last step."""
    from radiomics_crew.parsing import parse_as
    from radiomics_crew.schemas import PaperCard

    card = parse_as(PaperCard, '{"title": "X", "ibsi_compliant": "stated", "risk_of_bias": "probably fine"}')
    assert card.ibsi_compliant == "not stated"  # unverified must never read as verified
    assert card.risk_of_bias == "moderate"

    # explicit values still pass through exactly
    clean = parse_as(PaperCard, '{"title": "Y", "ibsi_compliant": "yes", "risk_of_bias": "high"}')
    assert clean.ibsi_compliant == "yes" and clean.risk_of_bias == "high"



def test_papercard_accepts_numeric_pmid_and_multivalue_modality():
    """The second real failed run: the model wrote PMIDs and cohort sizes as JSON numbers, and
    gave modality as 'CT, MRI, PET/CT' for studies that genuinely span several. Both are the
    model being right and the schema being too rigid — coerce, don't reject."""
    from radiomics_crew.parsing import parse_as
    from radiomics_crew.schemas import EvidenceTable

    table = parse_as(EvidenceTable, """{"included": [
        {"pmid": 30845221, "title": "A", "modality": "MRI", "n_patients": 104},
        {"pmid": 39123396, "title": "B", "modality": "CT, MRI, CBCT, PET/CT", "n_patients": "not reported"}
    ]}""")
    assert table.included[0].pmid == "30845221"      # coerced int -> str
    assert table.included[0].n_patients == "104"
    assert table.included[1].modality == "CT, MRI, CBCT, PET/CT"  # multi-value survives


def test_truncated_report_is_recovered_not_lost():
    """A writer that runs into the output-token ceiling mid-JSON produced a report cut off at
    'Test-retest interval not specified in' — a real failure. The synthesis and everything up to
    the cut must survive; the missing closing fields default rather than discarding a paid run."""
    from radiomics_crew.parsing import parse_as
    from radiomics_crew.schemas import ReviewReport

    truncated = (
        '{"question": "q", "n_screened": 87, "n_included": 25, "synthesis": "long analysis",'
        ' "methodological_gaps": ["only 3 CT studies"], "reproducibility_concerns": ["no code released",'
        ' "Test-retest interval not specified in'
    )
    report = parse_as(ReviewReport, truncated)
    assert report.synthesis == "long analysis"
    assert report.methodological_gaps == ["only 3 CT studies"]
    assert report.confidence_in_body_of_evidence == "low"  # safe default, not a crash
    assert report.references == []
