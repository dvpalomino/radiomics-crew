# Methods Decision Record

**Question:** For this multicentre CT radiomics study of solid abdominal tumours, which discretisation method (FBS vs FBN) and normalisation strategy (per-case vs cohort-level z-score, and its timing relative to discretisation and external validation) should be adopted as the default preprocessing protocol?

**Context:** Evidence brief synthesised from five independent literature searches (PubMed, IBSI documentation, reporting-standard checklists) comparing four candidate configurations: (i) FBS in raw HU with no normalisation; (ii) FBN after per-case z-score normalisation; (iii) FBN after cohort-level z-score normalisation; (iv) FBS after cohort-level z-score normalisation. No study tests any of these four bundled configurations head-to-head with external validation on an outcome model in solid abdominal tumour CT. The MRI/PET literature broadly favours FBS for reproducibility, but the only CT-native discretisation-stability study (PMID 34329921, n=95, head-neck dual-energy CT under simulated HU shift) favours FBN, directly contradicting the cross-modality majority. Outcome-level evidence for FBN vs FBS is itself contradictory (PMID 38549835 favours FBN; PMID 40570507 finds no difference). No standard (IBSI, RQS, CLEAR, METRICS) specifies how cohort-level normalisation statistics should be handled at external validation (freeze-and-transport vs recompute), and this gap is confirmed by the regulatory reviewer as absent from the standards themselves, not merely under-reviewed.

## Options considered

- (i) FBS in HU, no normalisation ('HU is already calibrated')
- (ii) FBN after per-case (intra-patient) z-score normalisation
- (iii) FBN after cohort-level (inter-case) z-score normalisation
- (iv) FBS after cohort-level z-score normalisation (bins in SD units, not HU)

## Panel positions

### Consultant Radiologist
*confidence: moderate*

**Position.** Primary: Option (ii); acceptable fallback: Option (iii); rejects (i) and (iv).

**Rationale.** Absolute HU is not clinically trustworthy across vendors/protocols; relative intra-patient intensity is the stable signal, and per-case normalisation needs no infrastructure most hospital PACS environments lack.

**Evidence.** PMID 42435270, 36728452 (inter-scanner HU bias, phantom), 37413967 (multicentre abdominal CT normalisation improves feature agreement 9/93→79/93), 32704007 (z-score improves balanced accuracy), 34329921 (CT-native, favours FBN), 35523919 (slice-thickness effect on AUC).

**Concerns raised.**
- Warns Methodologist against treating a stability study as an outcome study and against citing IBSI as prescriptive; warns Engineer against prioritising code elegance (Option iv) over clinical validity.

### Radiomics Methodologist
*confidence: moderate*

**Position.** Dissents from majority: primary Option (iii), fallback (ii); rejects (i); treats (iv) as untested.

**Rationale.** Privileges the single CT-native stability finding (PMID 34329921) over the larger but off-modality MRI/PET literature, on the principle that modality-native physics evidence should outweigh cross-modality volume; treats the leakage/transport problem as a design gap to be prospectively declared, not a reason to avoid cohort statistics.

**Evidence.** PMID 34329921, 37413967, 32154773 (used to show IBSI does not mandate a discretisation choice), 42355552 (no configuration optimal across analyses, used to justify trusting modality-native evidence).

**Concerns raised.**
- Flags all four other roles as vulnerable to the 'standards-naming trap' (falsely citing IBSI/CLEAR/RQS/METRICS as mandating a choice) and pushes back on the Biostatistician's leakage framing as conflating model-tuning leakage with a preprocessing-configuration decision.

### Biostatistician
*confidence: moderate*

**Position.** Option (ii) primary, ordering (ii) > (iii) > (i) >> (iv).

**Rationale.** Leakage avoidance from per-case normalisation is mathematically certain, not probabilistic, which is the load-bearing argument; explicitly declines to treat a single n=95 stability study as decisive for a >150-patient multicentre outcome study, and flags that the only two outcome-level FBN-vs-FBS studies contradict each other in direction and are underpowered.

**Evidence.** PMID 32704007, 34329921, 37413967, 33638729/38332405 (discretisation effect exceeds segmentation-variability effect), 38549835 vs 40570507 (flagged explicitly as contradictory and underpowered).

**Concerns raised.**
- Directly names the Methodologist's reliance on 34329921 as a category error (stability endpoint mistaken for outcome endpoint in a small single-institution sample); flags the Radiologist for citing 37413967 as timing-specific when the paper does not report which normalisation timing was used.

### Medical Imaging AI Engineer
*confidence: moderate*

**Position.** Option (ii) primary; conditional escalation to (iii) only if internal validation shows a stated AUC advantage AND a fully specified freeze/transport protocol is built and audited first.

**Rationale.** Determinism and absence of hidden pipeline state are the primary decision criteria, not a proxy for expected AUC; states that 'freeze-and-transport' as currently proposed is not a real specification (no field-standard for statistic versioning, drift-checking, or new-site onboarding) and estimates it as a concrete, costed engineering liability.

**Evidence.** PMID 34329921 (explicitly flagged as single-study, CT-native but contradicting the majority), 37413967, 36728452, 42435270, 33706419/38454921/31544368 (slice thickness as dominant confound).

**Concerns raised.**
- Challenges the Methodologist to specify decimal precision, recompute-vs-freeze decision rules, and governance for a third site joining later, arguing that without these, 'freeze-and-transport' is aspirational rather than implementable.

### Regulatory and Reproducibility Advisor
*confidence: moderate*

**Position.** Option (ii) primary, with a defined conditional pathway to (iii) only under a pre-registered internal validation trigger and an audited implementation spec.

**Rationale.** Applies a three-part test (full specification/auditability, no undocumented cross-site dependency, honest representation of what standards require) and finds only Option (ii) currently passes cleanly; explicitly states IBSI/RQS/CLEAR/METRICS assess reporting, not correctness, and flags this as the likeliest error to appear in the eventual Methods section.

**Evidence.** PMID 34329921, 37413967, 36728452, 42435270, 32154773, 42355552, used specifically to test standards-compliance and auditability rather than clinical or statistical performance.

**Concerns raised.**
- Names the Methodologist's 'prospective registration' of freeze-and-transport as procedurally reassuring but informationally empty absent a real implementation spec; endorses the Engineer's and Biostatistician's skepticism as substantively correct.

## Points of disagreement

- **The core split is (ii) vs (iii): per-case vs cohort-level z-score.** Four roles (Radiologist, Biostatistician, Engineer, Regulatory) default to per-case (ii); the Methodologist dissents to cohort-level (iii). The disagreement is real, not vocabulary — it turns on the leakage/transport problem, not on the discretisation method, since all four of these positions already agree on FBN.
- **How much weight the single CT-native study (PMID 34329921) should carry.** The Methodologist treats it as decisive on the principle that modality-native physics evidence outweighs the larger off-modality MRI/PET literature. The Biostatistician names this a category error — a stability endpoint (n=95, single-institution, head-neck DECT) used as if it were outcome-level evidence for a >150-patient multicentre abdominal study. This is the sharpest substantive clash in the panel.
- **Whether the leakage argument applies at all.** The Biostatistician holds that per-case normalisation removes an information-leakage pathway with mathematical certainty. The Methodologist counters that this conflates model-tuning leakage with a preprocessing-configuration decision, and that a prospectively declared cohort-statistic protocol is legitimate. This is not resolved by the evidence — it is a genuine framing disagreement.
- **Whether 'freeze-and-transport' is implementable or aspirational.** The Methodologist proposes prospective registration of the cohort-statistic handling as sufficient. The Engineer and Regulatory reviewer agree with each other that, absent a real specification (decimal precision, recompute-vs-freeze rules, drift-checking, new-site onboarding governance), prospective registration is "procedurally reassuring but informationally empty." This is a disagreement about what counts as a specification, not about the science.
- **The standards-naming trap.** The Methodologist flags all other roles as vulnerable to citing IBSI/CLEAR/RQS/METRICS as if they mandate a discretisation or normalisation choice. The Regulatory reviewer concurs that these standards assess reporting completeness, not methodological correctness — and identifies this as the single most likely error to appear in the eventual Methods section. This is a point of agreement about a shared risk, surfaced through disagreement.
- **Option (i) FBS-no-normalisation is rejected by consensus, but for non-identical reasons** — the Radiologist on grounds of cross-vendor HU untrustworthiness, the Biostatistician and Engineer on reproducibility-stability grounds. Option (iv) is rejected or treated as untested by all five.

## Consensus

Four of five roles converge on **Option (ii): FBN after per-case z-score normalisation** as the default preprocessing protocol, with the Methodologist dissenting toward cohort-level normalisation (iii). The consensus is genuine but bounded: it holds on the discretisation method (FBN over FBS for this multi-vendor, HU-drift-prone setting) and on per-case normalisation as the safe default, and it explicitly does *not* claim (ii) is the performance optimum — only that it is the most defensible and lowest-liability choice given that no study tests these configurations at outcome-model level with external validation. The panel agrees that the choice between (ii) and (iii) should not be settled by assertion but by a pre-registered internal-validation trigger: (iii) is adopted only if it shows a stated AUC advantage *and* a fully specified, audited freeze-and-transport implementation exists first.

## Recommended protocol

1. Discretise with **fixed bin number (FBN)**, not fixed bin size, given the multi-vendor cohort and documented cross-scanner HU drift; fix the bin count in advance (e.g. 64) and report it.
2. Apply **per-case (intra-patient) z-score normalisation before discretisation** as the default; compute the statistic within each patient's ROI, so no cross-case or cross-site information enters the transform.
3. Resample to isotropic voxels with a stated interpolator before discretisation, and report the target spacing; treat slice thickness (1.0–3.0 mm here) as a dominant confound and record it per case.
4. **Do not** adopt cohort-level normalisation (iii) as the default. Reserve it for a conditional pathway only.
5. Define the conditional escalation to (iii) as a **pre-registered internal-validation trigger**: adopt (iii) only if it shows a specified AUC advantage over (ii) on internal validation AND a complete freeze-and-transport specification has been built and audited first.
6. If (iii) is ever adopted, the freeze-and-transport spec must state: decimal precision of the frozen statistics, the recompute-vs-freeze decision rule at each new site, drift-checking procedure, and governance for onboarding a site that joins after the statistics are locked.
7. In the Methods section, state explicitly that IBSI/RQS/CLEAR/METRICS were used for reporting completeness only, and that they do not mandate the discretisation or normalisation choice — pre-empting the standards-naming trap.
8. Declare the preprocessing configuration as locked before external validation on the fourth centre, and report it as a fixed part of the pipeline, not a tunable hyperparameter.

## Reproducibility requirements

- Report the discretisation method and exact bin count, the normalisation method and its timing relative to discretisation, and the resampling spacing and interpolator.
- State per-case vs cohort-level normalisation explicitly, and if cohort-level is ever used, document the freeze-vs-recompute handling at external validation — the gap no standard currently specifies.
- Record slice thickness per case and report its distribution, given its role as a dominant confound.
- Cite IBSI/reporting standards for what they actually cover (reporting completeness), not as justification for the methodological choice.
- Re-verify every PMID against PubMed directly before manuscript submission, particularly any high-identifier records flagged as unverified in the evidence brief.

## Residual risks

- The entire decision rests on feature-reproducibility evidence, not outcome-model evidence: no study compares these configurations on AUC/calibration with external validation in abdominal CT, so the default is a liability-minimising choice, not a demonstrated optimum.
- The one CT-native study (PMID 34329921) contradicts the cross-modality majority and points toward FBN; the panel adopts FBN partly on its strength while simultaneously flagging it as too small and off-anatomy to be decisive — an acknowledged tension.
- The two outcome-level FBN-vs-FBS studies contradict each other in direction and are underpowered, so the FBN preference could reverse with better-powered evidence.
- Per-case normalisation trades the leakage risk of cohort statistics for a possible loss of a genuinely informative cohort-level signal, which cannot be quantified from current evidence.

## Revisit this decision if

- A study compares these configurations at outcome-model level (AUC, calibration, external transportability) in multi-vendor abdominal CT — that evidence would supersede the current reproducibility-only basis.
- Internal validation shows a specified AUC advantage for cohort-level normalisation (iii) AND an audited freeze-and-transport specification exists — the pre-registered trigger for escalating from (ii) to (iii).
- A standard (IBSI, CLEAR, RQS, METRICS or successor) begins to specify how cohort-level normalisation statistics must be handled at external validation, closing the gap the panel identified.
- A better-powered outcome study resolves the current FBN-vs-FBS contradiction in either direction.
- A third or later site joins the study after statistics are locked, forcing the freeze-vs-recompute governance question the Engineer raised.
