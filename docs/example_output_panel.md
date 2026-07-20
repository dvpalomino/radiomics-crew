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


## Consensus



## Recommended protocol


## Reproducibility requirements


## Residual risks


## Revisit this decision if
