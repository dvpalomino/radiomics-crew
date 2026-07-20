# RadiomicsCrew

**Multi-agent systems for radiomics methodology — literature review that reads the Methods, and an expert panel that is allowed to disagree.**

[![tests](https://github.com/USER/radiomics-crew/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/radiomics-crew/actions)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

Built with [crewAI](https://github.com/crewAIInc/crewAI), applying the design principles from
DeepLearning.AI's *Multi AI Agent Systems with crewAI* (João Moura) to a domain where a
plausible-sounding wrong answer is expensive: quantitative medical imaging.

---

## Why this exists

Two tasks in radiomics research eat weeks and are structurally a good fit for a crew of agents:

1. **Reading the literature properly.** A radiomics paper's conclusion is rarely the interesting
   part. What matters is buried in the Methods: was discretisation FBS or FBN, was feature selection
   inside or outside the cross-validation loop, was there an external cohort, which PyRadiomics
   version. Screening on abstracts misses all of it — and abstracts are where a single LLM stops.

2. **Deciding methodology.** Choices like *fixed bin size vs fixed bin number*, *per-case vs
   cohort-level normalisation*, or *ComBat vs image-level harmonisation* are not settled. They get
   resolved in meetings where a radiologist, a methodologist, a biostatistician, an engineer and a
   regulatory person want genuinely different things — and the useful output of that meeting is not
   agreement, it is a written record of where the disagreement is.

Each maps to a different crewAI process, and the mapping is the point of this repo.

| | `review` crew | `panel` crew |
|---|---|---|
| **Process** | `Process.sequential` | `Process.hierarchical` |
| **Why** | It is a real pipeline: you cannot screen what you have not searched | A consensus is not a pipeline; someone must hold the goal and push back |
| **Agents** | Search Strategist → Evidence Screener → Methods Appraiser → Scientific Writer | Radiologist, Methodologist, Biostatistician, ML Engineer, Regulatory Advisor + Chair |
| **Delegation** | off | on — the chair returns thin positions for evidence |
| **Output** | `ReviewReport` (JSON + Markdown, with an evidence table) | `MethodsDecisionRecord` (ADR-style, dissent preserved) |

---

## What it produces

`review` → an evidence table where every row was verified against the **full text**, not the abstract,
plus a synthesis organised by *methodological choice* rather than paper by paper, and an explicit list
of what nobody has tested.

`panel` → a Methods Decision Record: options considered, one position per role with its evidence,
**points of disagreement kept in the record**, an ordered executable protocol, reproducibility
requirements, residual risks, and the conditions under which the decision should be revisited.

> A protocol is "FBS, bin width 25 HU, on images resampled to 1×1×1 mm with a B-spline interpolator".
> "Choose an appropriate discretisation" is not a protocol. The schemas enforce the difference.

---

## Install

```bash
git clone https://github.com/USER/radiomics-crew.git
cd radiomics-crew
python -m venv .venv && source .venv/bin/activate    # Windows: py -3.12 -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env      # add your key; .env is gitignored
pytest -q                 # verifies the install without spending a token
```

**Python 3.10–3.13.** crewAI caps at `<3.14`; 3.12 is the safest bet on Windows, where wheels for
the compiled dependencies land latest.

Any LiteLLM-supported provider works. Workers and the panel chair are routed separately —
`RC_MODEL` for the four workers, `RC_MANAGER_MODEL` for the chair, because a weaker model drifts
off the goal over a long hierarchical run. A local Ollama model works for both if you want a zero-cost run.

## Run

```bash
# Literature review
python -m radiomics_crew review \
  --question "Does ComBat harmonisation improve external validation of CT radiomic models in multicentre cohorts?" \
  --min-year 2019

# Expert panel, from a preset
python -m radiomics_crew panel --preset fbn_vs_fbs_ct

# Expert panel, your own question
python -m radiomics_crew panel \
  --question "Are DL-generated masks acceptable as the ROI source for a radiomic signature?" \
  --context "nnU-Net mean Dice 0.87, 10% of cases below 0.6" \
  --option "fully automatic" --option "automatic + review of every case" \
  --option "review triggered by a quality score" \
  --tumour-site pancreatic --modality CT
```

Artifacts land in `outputs/` as both JSON (diffable, testable) and Markdown (readable).
Presets live in [`examples/presets.yaml`](examples/presets.yaml); more review questions —
including [the ones this crew handles badly](examples/questions.md) — are in `examples/`.

---

## Design notes

The course's six components, and what each one is actually doing here:

**Role-playing.** Specificity is the whole trick. Not "you are a biostatistician" but *"you have
killed more radiomic signatures than you have published, and you consider that a successful career.
You count events, not patients."* Roles live in [`config/*/agents.yaml`](config/) so that prompt
changes are reviewable in a diff — the prompts are the product, and they are tested like code.

**Tools.** Four custom ones: `pubmed_search` and `pubmed_fetch_abstracts` (NCBI E-utilities),
`europepmc_full_text` (open-access Methods sections), and `ibsi_reporting_checklist`. All of them
cache, retry with backoff, throttle to stay inside NCBI's rate limit, and return errors as text the
agent can reason about rather than raising and killing the run.

**Focus.** The Scientific Writer has **no search tools** — deliberately. It can only write from the
evidence table it is handed. Removing the ability to fabricate beats instructing against it.

**Guardrails.** Every task output is validated against a pydantic model, so a task cannot succeed
by returning confident prose. `max_iter=12` and `max_rpm=20` bound the reasoning loops.
`PaperCard.n_patients` defaults to the literal string `"not reported"`, never to a plausible number,
and `ibsi_compliant="not stated"` is kept distinct from `"no"` — a distinction that gets lost
constantly in real reviews.

Two failure modes get *repaired* rather than rejected, because they are properties of the medium
rather than prompt bugs: a long JSON object written token by token eventually drops a comma
(`json_repair` fixes the punctuation), and models write `"HIGH — because the full text was
unavailable"` where an enum was asked for (coercing validators recover the first word). Neither
tolerance extends to invented fields or missing required ones — and the coercion refuses to guess:
if the first word is not a valid level, it raises. The line is between recovering an intent the
model clearly had and fabricating one it did not.

Validation happens in [`parsing.py`](src/radiomics_crew/parsing.py), *not* via crewAI's
`output_pydantic`. That option serialises the model into a JSON Schema and hands it to the provider
to enforce — and Anthropic rejects nested ones outright (`Schema is too complex`), with no
documented limit to design against. So the schema never leaves the process: the task prompt carries
a rendered example of the shape, generated from the model itself so it cannot drift, and the output
is parsed and validated on the way back. Same guardrail, one step later, portable across providers.

**Cache, and memory off by default.** `cache=True` stops four agents from re-fetching the same
PMID. crewAI's memory is disabled unless you set `RC_MEMORY=true`: it requires an embedder and
defaults to OpenAI's, which would make an `OPENAI_API_KEY` mandatory even on an Anthropic-only or
fully local setup. Little is lost — every task declares its upstream `context` explicitly, which is
what actually carries the chain.

**Cooperation.** Sequential where the work is a pipeline, hierarchical where it is a negotiation.

### The IBSI checker is deliberately dumb

`ibsi_reporting_checklist` is keyword matching over a Methods section — no LLM in the loop. It answers
exactly one question: *did the authors state this?* Never *did they do it correctly?*

That is on purpose. It is the only deterministic component in a stochastic system, so two runs over
the same paper produce an identical checklist, and any disagreement between runs comes from the
agents' reasoning rather than from the evidence underneath it. The checklist is a condensed
IBSI-1/IBSI-2 + METRICS-style reporting audit, versioned in
[`knowledge/ibsi_reporting_checklist.yaml`](knowledge/ibsi_reporting_checklist.yaml) and pinned by tests.

### Honest limitations

- **Screening is not systematic-review-grade.** No dual independent screening, no PRISMA flow, no
  formal risk-of-bias instrument. This is a fast, auditable first pass — it points a human at the
  right twenty papers. It does not replace them.
- **Full-text appraisal only reaches open access.** Paywalled papers come back
  `NOT_OPEN_ACCESS`; the crew marks the fields unverifiable and raises risk-of-bias rather than
  guessing. Roughly half the relevant literature is behind that wall, and the evidence table
  is biased by exactly that much.
- **The panel simulates expertise; it does not have any.** A Methods Decision Record is a structured
  starting point for a real meeting, and an argument map. It is not a clinical or regulatory opinion,
  and nothing here is a medical device.
- **PubMed indexing lags.** Very recent work is under-retrieved, silently.
- **Cost.** A `panel` run with a hierarchical chair is not cheap. Check `token_usage`, printed after
  every run.

---

## Tests

```bash
pytest -q          # 24 tests, no network, no API key
ruff check src tests
```

The suite pins the deterministic parts: the checklist's behaviour on well- and poorly-reported
Methods, that a missing `PaperCard` field stays missing, that panel tasks never hardcode an agent
(which would silently disable the chair's delegation), and that no unsubstituted `{placeholder}`
can reach an LLM.

Three of them are regression tests for bugs that actually shipped, and they are the ones worth
reading: `memory` must never be hardcoded on, `output_pydantic` must never reappear, and the
parser must survive a model that wraps its JSON in chatty prose. Each of those cost a failed run
to find, which is the argument for the tests existing at all.

## Layout

```
config/          agents.yaml + tasks.yaml per crew — the prompts, versioned and tested
knowledge/       the IBSI/METRICS reporting checklist
src/radiomics_crew/
  crews/         sequential review crew, hierarchical panel crew
  tools/         PubMed, Europe PMC, IBSI checker, shared cached HTTP layer
  schemas.py     pydantic contracts for every task output
  render.py      JSON -> Markdown
examples/        presets and example questions (including the bad ones)
```

## Credits

Agent design patterns from [*Multi AI Agent Systems with crewAI*](https://www.deeplearning.ai/courses/multi-ai-agent-systems-with-crewai)
(DeepLearning.AI / crewAI, João Moura). The domain layer — the checklist, the schemas, the panel
roles, the failure modes worth guarding against — is mine.

MIT licensed. Not a medical device. Not clinical advice.
