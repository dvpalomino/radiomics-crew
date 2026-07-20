# Architecture

## review — sequential

```
question
   │
   ▼
[Search Strategist]      pubmed_search
   │  SearchStrategy (PICOS + literal boolean queries)
   ▼
[Evidence Screener]      pubmed_search, pubmed_fetch_abstracts
   │  EvidenceTable (abstract level; every exclusion carries a reason)
   ▼
[Methods Appraiser]      pubmed_fetch, europepmc_full_text, ibsi_reporting_checklist
   │  EvidenceTable (full-text verified; risk_of_bias per paper)
   ▼
[Scientific Writer]      no tools — can only write from the evidence table
   │
   ▼
ReviewReport ──> outputs/review_report.{json,md}
```

Sequential's known weakness is context fade: the original question dilutes as output passes down the
chain. Mitigated by re-injecting `{question}` into every task description, declaring upstream
`context` explicitly rather than relying on adjacency. (crewAI's own memory is off by default —
see the README — so the explicit `context` chain is what carries state, not a vector store.)

## panel — hierarchical

```
                        ┌──────────────────┐
   question ──────────► │   Panel Chair    │ ◄── holds the goal, delegates,
   context              │  (manager_agent) │     sends thin positions back
   options              └────────┬─────────┘
                                 │
        ┌───────────┬────────────┼────────────┬──────────────┐
        ▼           ▼            ▼            ▼              ▼
   Radiologist  Methodologist  Biostat.   ML Engineer   Regulatory
        │           │            │            │              │
        └───────────┴────────────┴────────────┴──────────────┘
                                 │
                                 ▼
              MethodsDecisionRecord ──> outputs/methods_decision_record.{json,md}
```

Three stages: `gather_evidence` (establish what the literature says before anyone has a position),
`collect_positions` (one statement per role, no convergence permitted yet), `adjudicate` (confront,
decide, and record the dissent).

The tasks carry no `agent:` field — under `Process.hierarchical` the chair assigns them. Pinning an
agent there silently disables the delegation that is the entire reason for choosing this process.

## Why the writer has no tools

The most common failure of an LLM-written review is a citation that does not exist. Instructing the
model not to fabricate is weaker than removing the capability: with no search tool, the Scientific
Writer's only source of PMIDs is the evidence table upstream. It can still misread that table — but
it cannot invent a paper.

## Cost profile

Workers run on `RC_MODEL` (cheap, high call volume). The chair runs on `RC_MANAGER_MODEL`. This is
not only about cost: the chair must hold the original question across a long hierarchical run with
five delegates, which is precisely where a small model drifts and starts agreeing with whoever spoke
last.


## Why validation lives in parsing.py

crewAI's `output_pydantic` serialises the model to a JSON Schema and makes the provider enforce it.
Convenient, and it works on OpenAI. Anthropic rejects nested schemas with `Schema is too complex`,
and the limit is not published as a number, so flattening field counts until it passes is guesswork
that breaks again on the next model.

So the schema stays in-process. `parsing.shape_hint(model)` renders the expected JSON as plain text
into the task prompt — generated from the pydantic model, so prompt and type cannot drift apart —
and `parsing.parse_as(model, raw)` validates the result, tolerating the fences and preamble that
models like to wrap JSON in. The guardrail fires one step later, under our control, and behaves the
same on any provider.
