# Example questions for the `review` crew

Copy one, or write your own. The crew rewards a question narrow enough to have an answer.

```bash
python -m radiomics_crew review \
  --question "Does ComBat harmonisation improve external validation performance of CT radiomic models in multicentre pancreatic cancer cohorts?" \
  --min-year 2019
```

```bash
python -m radiomics_crew review \
  --question "How sensitive are CT radiomic texture features to the choice of fixed bin size versus fixed bin number discretisation?" \
  --scope "restrict to studies that report a stability analysis (ICC or CCC)" \
  --min-year 2018
```

```bash
python -m radiomics_crew review \
  --question "Do radiomic models predicting pathological complete response after neoadjuvant chemoradiotherapy in rectal cancer validate externally?" \
  --scope "external validation cohort required; exclude single-centre-only studies" \
  --min-year 2020
```

```bash
python -m radiomics_crew review \
  --question "What segmentation quality metrics beyond Dice have been proposed to represent radiologist correction workload?" \
  --min-year 2019
```

## Questions this crew will handle badly

Worth knowing where the tool ends:

- **"What is radiomics?"** — too broad; the screener will include everything and the synthesis will be a textbook chapter.
- **"Is my model good?"** — no literature answers this. This is a panel question at best, and probably a biostatistician question.
- **Anything from the last three months** — PubMed indexing lags, and the crew will silently under-retrieve rather than warn you.
