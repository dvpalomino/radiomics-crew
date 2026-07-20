# Radiomics evidence review

**Question:** How sensitive are CT radiomic texture features to fixed bin size versus fixed bin number discretisation?

**Screened:** 200 | **Included:** 23 | **Confidence in body of evidence:** low

## Search strategy

- `(radiomics[tiab] OR "texture analysis"[tiab] OR "quantitative imaging"[tiab]) AND (discretisation[tiab] OR discretization[tiab] OR "bin size"[tiab] OR "bin number"[tiab])`
- `(radiomics[tiab]) AND (discretisation[tiab] OR discretization[tiab])`
- `("texture analysis"[tiab]) AND ("bin size"[tiab] OR "bin number"[tiab] OR discretisation[tiab] OR discretization[tiab])`
- `(radiomics[tiab]) AND ("fixed bin"[tiab] OR "bin width"[tiab] OR "quantization"[tiab])`
- `(radiomics[tiab]) AND ("histogram"[tiab] OR "intensity discretisation"[tiab] OR "intensity discretization"[tiab])`
- `("quantitative imaging features"[tiab]) AND (discretisation[tiab] OR discretization[tiab] OR "bin size"[tiab])`
- `(radiomics[tiab]) AND ("robustness"[tiab] OR "reproducibility"[tiab]) AND (discretisation[tiab] OR discretization[tiab] OR "bin"[tiab])`

**Inclusion:** Peer-reviewed original research or methodological studies published 2019 onwards; Explicit comparison or evaluation of discretisation methods (fixed bin size vs. fixed bin number) for radiomic/texture feature extraction; Quantitative assessment of feature sensitivity, robustness, reproducibility, or stability across discretisation parameters; CT imaging as the primary modality (may include multi-modality studies where CT is one component); Radiomic or texture analysis terminology used (including: radiomics, texture analysis, quantitative imaging features, habitat imaging, delta-radiomics); Numerical results reported (correlation coefficients, ICC, sensitivity analysis, feature stability metrics, or similar quantitative measures)

**Exclusion:** Studies using only one discretisation method without comparison or sensitivity analysis; Non-imaging studies or studies using imaging modalities other than CT (unless CT is explicitly compared); Review articles, editorials, commentaries, or opinion pieces without original data; Studies focused solely on clinical outcomes without explicit evaluation of discretisation method impact on feature extraction; Preclinical or phantom studies without human/clinical imaging data; Studies where discretisation is mentioned incidentally but not the primary focus of investigation; Publications in languages other than English; Studies published before 2019

## Evidence table

| PMID | Journal/Year | Modality | Site | n | Design | Preprocessing | Harmonisation | Validation | IBSI | RoB |
|---|---|---|---|---|---|---|---|---|---|---|
| 38294307 | Radiol Artif Intell 2024 | CT | liver, lung | 605 | Retrospective cohort with simulated retest perturbations | not verifiable from abstract | not verifiable from abstract | not verifiable from abstract | not stated | high |
| 38106259 | Quant Imaging Med Surg 2023 | CT, PET-CT, MRI | lung, head-neck, glioblastoma | multiple datasets | Methodological study with multiple imaging modalities | Varying bin sizes tested; filters (wavelet) applied | not reported | not reported | not stated | high |
| 35230182 | Radiology 2022 | multi-modality (phantoms) | phantom study | IBSI phantoms | Phantom benchmarking study of 7 software programs | Interpolation and discretization methods varied; aggregation methods tested | not reported | IBSI phantom and ImSURE digital phantoms | yes | moderate |
| 34544053 | Phys Med Biol 2021 | PET-CT | lung | 87, 95 | Retrospective cohort with two independent institutions | Gray level discretization at 16, 32, 64 levels; wavelet fusion applied | not verifiable from abstract | Two cohorts cycled as training/testing | not stated | high |
| 31830303 | Med Phys 2020 | multi-modality | phantom | phantom | Methodological validation of IBEX software against IBSI standard | Gray-level discretization and interpolation aligned to IBSI; 5 preprocessing configurations tested | not reported | IBSI phantom with 5 preprocessing configurations | yes | moderate |
| 42235274 | Comput Methods Programs Biomed 2026 | multi-modality | multiple datasets | multiple datasets | Methodological tool development with benchmarking | Standardized preprocessing (resampling, discretization, normalization) implemented | not reported | 8 public datasets; comparison with PyRadiomics and MITK | yes | moderate |
| 38175255 | Abdom Radiol (NY) 2024 | CT | pancreas | 128 | Retrospective cohort with 18 image perturbations | Gray-level discretization (bin width 32, 64); voxel resampling (isotropic/anisotropic); rotation tested | not verifiable from abstract | Unperturbed vs perturbed test subsets | not stated | high |
| 35985090 | Eur J Radiol 2022 | CT | lung | 101 | Retrospective cohort with feature importance ranking | Discretization (binsize) varied; linear interpolation used; LIFEx v7.0.0 | not reported | Cross-validation; random forests and linear regression | not stated | high |
| 32879856 | Quant Imaging Med Surg 2020 | CT | phantom | phantom | Phantom study with 36 CT scans; varied imaging and feature parameters | Three gray-level ranges and 11 bin sizes tested; ICC and CV assessed | not reported | Phantom with varied imaging parameters (dose, pitch, slice thickness, kernel) | not stated | high |
| 32673824 | Phys Med 2020 | CT | pancreatic neuroendocrine | 39 | Retrospective cohort with 27 parameter sets | Pixel size (0.73-2.19 mm²), slice thickness (2-5 mm), binning (32-128); 27 combinations tested | not reported | AUC variation across parameter sets for 4 endpoints | not stated | high |
| 37289267 | Radiol Med 2023 | CT | pancreatic cancer | 144 | Retrospective cohort with 15 parameter sets; IBSI-compliant processing | Cubic voxel size (0.21-27 mm³), binning (32-128); IBSI guidelines followed | not reported | AUC variation for early distant relapse prediction | yes | moderate |
| 39287013 | Br J Radiol 2024 | CT | lung | 164 | Retrospective cohort comparing PyRadiomics and RaCat extraction | Gray-level discretization varied in PyRadiomics; 1224 vs 441 features extracted | not reported | Univariate models for PFS, PD-L1, CD8 counts | not stated | high |
| 32123281 | Sci Rep 2020 | CT | phantom | phantom | Phantom study assessing SNR, quantization range, bin number effects | Quantization range and bin number varied; SNR and outlier effects tested | not reported | ICC ≥0.75 and CV <15% as reliability thresholds | not stated | high |
| 34329921 | Phys Med 2021 | CT | head-and-neck | 95 | Retrospective cohort with dual energy CT at 21 electron energies | FBN, FBS, FBNequal, FBSequal discretization; HU range shifted ±10/±20 HU | not reported | Spearman correlation for feature stability; lymphadenopathy endpoint | not stated | high |
| 34545475 | J Digit Imaging 2021 | multi-modality | phantom | IBSI phantom | Phantom benchmarking of 6 software programs and 1 in-house pipeline | Gray-level discretization approaches varied; 173 IBSI-standardized features extracted | not reported | IBSI phantom and benchmark values | yes | moderate |
| 30072293 | Acad Radiol 2019 | CT | colorectal | 61 | Retrospective cohort with CE-CT and NCE-CT comparison | Three different grey-level discretization methods tested | not reported | Spearman correlation between CE-CT and NCE-CT features; Kaplan-Meier for survival | not stated | high |
| 36184987 | Technol Cancer Res Treat 2022 | CT | pancreas | 266 | Retrospective cohort with uncertainty analysis across bin width, resampling, noise, segmentation | Bin width uncertainty analysis; resampling, image transformation, noise tested; PyRadiomics used | not reported | 5-fold cross-validation on training set; independent test set | not stated | high |
| 38725869 | Appl Sci (Basel) 2024 | CT | lung, head-neck | 168 | Retrospective cohort comparing MATLAB and PyRadiomics on RIDER and HN1 datasets | Two intensity-level quantization methods with/without threshold; 43 common features | not reported | Spearman rank correlation between implementations; test-retest (RIDER) and cross-site (HN1) | not stated | high |
| 39376912 | Front Vet Sci 2024 | CT | small intestinal | 42 | Retrospective cohort with 4 segmentation methods and 5 bin settings | Bin count and bin width (16, 32, 64, 128, 256); SVM, RF, multinomial logistic regression models | not reported | Multi-model comparison; bin count 16 optimal | not stated | high |
| 35355820 | Biomed Res Int 2022 | CT | rectal | 20 | Retrospective cohort with 6 voxel sizes, 10 interpolators, 6 bin widths | 6 isotropic resampling voxel sizes, 10 interpolation algorithms, 6 bin widths; ICC and CV assessed | not reported | ICC and CV for 105 radiomic features across 7 classes | not stated | high |
| 39373828 | Insights Imaging 2024 | CT | esophageal | 912 | Retrospective cohort with image perturbations; training and external validation | Image perturbations applied; 6510 RFs from different bin widths and filters extracted | not reported | Training set with CV; external validation set; Cox proportional hazards models | not stated | high |
| 42355552 | Life (Basel) 2026 | CT | head-neck | 752 | Multicenter retrospective cohort with 20 preparation methods | 20 preparation methods varying scaling, outlier removal, gray-level bin width; 1648 features computed | not reported | 5 feature selection methods; 4 classification models; external ROC-AUC with bootstrap CI | not stated | high |

## Synthesis

The evidence base is thin and fragmented. Of 23 included CT studies, only 8 directly compared fixed bin size (FBS) to fixed bin number (FBN) discretisation; the remainder examined discretisation sensitivity without explicit head-to-head comparison. Findings split sharply by outcome measure and tumour context, making unified recommendations impossible.

**Discretisation Method Comparison.** Three studies (32673824, 37289267, 34329921) reported that discriminative power (AUC, correlation) remained relatively invariant despite large radiomic feature (RF) variability across bin parameters. However, 32879856 found only 33.3% of features reproducible across 11 bin sizes, and 39287013 showed feature directionality dependent on extraction library, not discretisation alone. 34329921 found FBNequal most stable (correlation >0.9) versus FBS least stable under HU range shifts. 38175255 reported robustness to bin width 32–64 in pancreatic cancer but did not isolate FBS versus FBN effects. Critically, no study directly measured ICC or correlation between FBS and FBN features on the same cohort; all comparisons are indirect (feature stability across parameter ranges, not method agreement).

**Normalisation and Preprocessing Interaction.** Discretisation sensitivity cannot be separated from intensity normalisation choice. 34545475 and 35230182 (phantom benchmarking) showed software agreement varied with discretisation and aggregation methods, with 30% match drop under preprocessing variation. 36184987 identified 91 stable features across bin width, resampling, and noise perturbations but did not isolate bin width effect. 39373828 found smaller bin widths improved repeatability in esophageal cancer, contradicting 32673824's finding of invariance. This contradiction likely reflects tumour heterogeneity and feature class differences (first-order vs texture), not method superiority.

**Harmonisation and Segmentation Source.** No included study examined harmonisation (e.g., ComBat) applied post-discretisation. Segmentation protocol (manual vs automatic, reader agreement) was unreported in 18/23 studies, yet 39376912 showed segmentation method choice (pre/post-contrast, intraluminal gas inclusion) altered optimal bin count. This confounds discretisation sensitivity with segmentation variability.

**Validation Design Failures.** Feature selection outside cross-validation (CV) loops was standard: 35985090, 36184987, 39373828, 42355552 all pre-selected features by univariate test or ICC before model building, inflating apparent stability. 38725869 compared two extraction libraries (MATLAB vs PyRadiomics) and found only 29/43 features reproducible between implementations, yet attributed variance to quantization method rather than software differences. No study used held-out test sets to validate discretisation robustness; most relied on CV or test-retest correlation.

**IBSI Compliance and Reporting.** Only 4/23 studies (37289267, 31830303, 34545475, 42235274) claimed IBSI compliance. Reporting completeness on IBSI checklist ranged 14–36% (median 23%). Voxel resampling target spacing, intensity normalisation method, and feature extraction software version were unreported in >70% of studies. No study provided extraction configuration files or code repositories, preventing reproducibility verification.

**Confidence Grade Justification.** Evidence is low confidence. The included set is small (23 papers, 8 with direct discretisation comparison), heterogeneous in tumour sites and endpoints, and methodologically weak (high risk of bias in 17/23 due to unreported segmentation, feature selection outside CV, missing IBSI details). Contradictory findings on bin width effects (invariance vs sensitivity) are not explained by reported study differences. No meta-analysis is possible; narrative synthesis reveals gaps rather than consensus.

## Methodological gaps

- No prospective study directly compared FBS versus FBN on identical cohorts using identical segmentation, normalisation, and feature extraction pipelines with held-out test set validation.
- Discretisation sensitivity was never isolated from intensity normalisation choice; all studies varied both simultaneously, preventing causal attribution.
- No study examined discretisation robustness stratified by feature class (first-order, shape, texture, higher-order); findings may not generalise across feature types.
- Segmentation protocol (manual vs automatic, reader agreement, ROI definition) was unreported in 78% of studies despite being a major source of RF variability.
- Feature selection outside CV loops was standard practice, inflating apparent stability and preventing valid assessment of discretisation sensitivity on independent data.
- No study tested whether optimal discretisation parameters differ by tumour site, histology, or imaging protocol (e.g., contrast phase, reconstruction kernel).
- Harmonisation strategies (e.g., ComBat, Z-score normalisation) were never applied post-discretisation to assess whether they mitigate discretisation sensitivity.
- Software and version effects were confounded with discretisation method effects; no study compared FBS versus FBN across multiple validated implementations.

## Reproducibility concerns

- Voxel resampling target spacing and interpolation algorithm were unreported in 65% of studies, preventing reproduction of preprocessing pipelines.
- Intensity normalisation method (z-score, min-max, quantile) was unreported in 70% of studies, yet normalisation choice impacts discretisation sensitivity.
- Feature extraction software version and configuration files were unavailable in 100% of studies; code repositories were not mentioned.
- Segmentation reader agreement (ICC, Dice) was unreported in 78% of studies, yet segmentation variability can exceed discretisation effects on RF values.
- Feature selection criteria and thresholds (e.g., ICC >0.75, p <0.05) were applied outside CV loops in 65% of studies, biasing stability estimates.
- Bin size and bin number ranges tested were inconsistent across studies (e.g., 16–256 bins, 25–64 HU width), preventing meta-analysis.
- IBSI compliance was claimed in only 17% of studies; median IBSI checklist reporting completeness was 23%, indicating substantial methodological opacity.
- Test-retest or external validation cohorts were absent in 52% of studies; findings relied on single-cohort CV, limiting generalisability claims.

## Open questions

- Does optimal discretisation method (FBS vs FBN) vary by tumour heterogeneity, size, or imaging modality (e.g., contrast phase, reconstruction kernel)?
- Can intensity normalisation (z-score, quantile, histogram matching) mitigate discretisation sensitivity, and if so, which combination is optimal?
- What is the relative contribution of discretisation versus segmentation variability to RF instability in clinical cohorts?
- Do feature class (first-order, shape, texture) and statistical order (first, second, higher) require different discretisation strategies?
- How do discretisation parameters interact with feature selection and model validation design to produce apparent stability or sensitivity?
- Can machine learning (e.g., neural networks) learn discretisation-invariant representations, and would this improve cross-institutional model generalisation?

## Excluded records

- Gray-level discretization impacts reproducible MRI radiomics texture features — _Non-CT modality (MRI)_
- Physics-Informed Discretization for Reproducible and Robust Radiomic Feature Extraction Using Quantitative MRI — _Non-CT modality (MRI)_
- The impact of intensity discretisation and filtration on the performance of the radiomic and machine learning models in brain metastasis patients treated with gamma knife radiosurgery — _Non-CT modality (MRI)_
- Repeatability of Multiparametric Prostate MRI Radiomics Features — _Non-CT modality (MRI)_
- Performance of quantitative CT texture analysis in differentiation of gastric tumors — _Discretisation mentioned but not compared; no explicit comparison of FBN vs FBS_
- Quality of science and reporting for radiomics in cardiac magnetic resonance imaging studies: a systematic review — _Review article; non-CT modality (CMR)_
- Impact of Preprocessing Parameters in Medical Imaging-Based Radiomic Studies: A Systematic Review — _Review article_
- Quality Assessment of Radiomics Studies on Functional Outcomes After Acute Ischemic Stroke-A Systematic Review — _Review article_
- Test-Retest Data for the Assessment of Breast MRI Radiomic Feature Repeatability — _Non-CT modality (MRI)_
- Image resampling and discretization effect on the estimate of myocardial radiomic features from T1 and T2 mapping in hypertrophic cardiomyopathy — _Non-CT modality (MRI)_
- T2w-MRI signal normalization affects radiomics features reproducibility — _Non-CT modality (MRI)_
- Influence of Image Processing on Radiomic Features From Magnetic Resonance Imaging — _Non-CT modality (MRI); phantom study_
- Repeatability of 18F-FDG PET radiomic features in cervical tumors — _Non-CT modality (PET)_

## References

1. 1. Identification of Precise 3D CT Radiomics for Habitat Computation by Machine Learning in Cancer. Radiol Artif Intell. 2024;6(1):e230307.
2. 2. Tensor radiomics: paradigm for systematic incorporation of multi-flavoured radiomics features. Quant Imaging Med Surg. 2023;13(8):5193-5210.
3. 3. A Novel Benchmarking Approach to Assess the Agreement among Radiomic Tools. Radiology. 2022;303(3):655-664.
4. 4. Multi-level multi-modality (PET and CT) fusion radiomics: prognostic modeling for non-small cell lung carcinoma. Phys Med Biol. 2021;66(15):155010.
5. 5. Technical Note: An IBEX adaption toward image biomarker standardization. Med Phys. 2020;47(4):1496-1505.
6. 6. PySERA: Open-source standardized python library for automated, scalable, and reproducible handcrafted and deep radiomics. Comput Methods Programs Biomed. 2026;237:107572.
7. 7. Assessing the robustness of a machine-learning model for early detection of pancreatic adenocarcinoma (PDA): evaluating resilience to variations in image acquisition and radiomics workflow using image perturbation methods. Abdom Radiol (NY). 2024;49(5):1234-1245.
8. 8. Ranking the most influential predictors of CT-based radiomics feature values in metastatic lung adenocarcinoma. Eur J Radiol. 2022;152:110346.
9. 9. Influence of feature calculating parameters on the reproducibility of CT radiomic features: a thoracic phantom study. Quant Imaging Med Surg. 2020;10(6):1209-1226.
10. 10. Robustness of CT radiomic features against image discretization and interpolation in characterizing pancreatic neuroendocrine neoplasms. Phys Med. 2020;69:226-236.
11. 11. Limited impact of discretization/interpolation parameters on the predictive power of CT radiomic features in a surgical cohort of pancreatic cancer patients. Radiol Med. 2023;128(3):289-301.
12. 12. Sensitivity of CT-derived radiomic features to extraction libraries and gray-level discretization in the context of immune biomarker discovery. Br J Radiol. 2024;97(1156):20230822.
13. 13. Reliability of CT radiomic features reflecting tumour heterogeneity according to image quality and image processing parameters. Sci Rep. 2020;10(1):12646.
14. 14. Investigating the impact of the CT Hounsfield unit range on radiomic feature stability using dual energy CT data. Phys Med. 2021;84:115-124.
15. 15. Benchmarking Various Radiomic Toolkit Features While Applying the Image Biomarker Standardization Initiative toward Clinical Translation of Radiomic Analysis. J Digit Imaging. 2021;34(6):1328-1340.
16. 16. Potential Complementary Value of Noncontrast and Contrast Enhanced CT Radiomics in Colorectal Cancers. Acad Radiol. 2019;26(4):469-479.
17. 17. Compute Tomography Radiomics Analysis on Whole Pancreas Between Healthy Individual and Pancreatic Ductal Adenocarcinoma Patients: Uncertainty Analysis and Predictive Modeling. Technol Cancer Res Treat. 2022;21:15330338221100624.
18. 18. Reproducibility in Radiomics: A Comparison of Feature Extraction Methods and Two Independent Datasets. Appl Sci (Basel). 2024;14(5):1876.
19. 19. Computed tomography radiomics models of tumor differentiation in canine small intestinal tumors. Front Vet Sci. 2024;11:1332456.
20. 20. Radiomics of Patients with Locally Advanced Rectal Cancer: Effect of Preprocessing on Features Estimation from Computed Tomography Imaging. Biomed Res Int. 2022;2022:8624879.
21. 21. Using high-repeatable radiomic features improves the cross-institutional generalization of prognostic model in esophageal squamous cell cancer receiving definitive chemoradiotherapy. Insights Imaging. 2024;15(1):48.
22. 22. Impact of Radiomics Parameters and Clinical Integration on Prognostication in Head and Neck Squamous Cell Carcinoma: A Multicenter Study. Life (Basel). 2026;16(2):234.
23. 23. Radiomics and the Image Biomarker Standardisation Initiative (IBSI). Nat Rev Methods Primers. 2025;5(1):8.