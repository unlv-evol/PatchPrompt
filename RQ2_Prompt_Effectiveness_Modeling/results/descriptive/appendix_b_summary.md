# Appendix B Descriptive Analysis Summary

This file summarizes the extended descriptive outputs generated from the canonical
`Dataset_Construction/processed_data/final_analysis_dataset.csv` file. These outputs complement the
compact descriptive tables shown in the paper and provide additional distributional
evidence for the modeling decisions used downstream.

## Pull Request Size

Pull request size is strongly right-skewed. The mean PR size is 1802.77, while
the median is 214.0, with a maximum of 182390.0. This substantial
mean--median discrepancy and the presence of upper-tail outliers motivate the use
of log-transformed PR-size controls and robustness checks that remove extreme PR-size
observations.

## Contributor Experience

Contributor experience is also right-skewed. The mean is 58.69, the median
is 10.0, and the maximum is 788.0. This indicates that a small
number of highly experienced contributors contribute disproportionately large values,
which motivates careful interpretation of experience-related controls.

## Repository and Language Concentration

The most frequent repository is `VOICEVOX/voicevox` with 10
observations. The most frequent programming language is `TypeScript`
with 66 observations. These concentrations motivate the
robustness checks that exclude the dominant repository and dominant language.

## Generated Artifacts

The extended descriptive analysis produces CSV summaries, LaTeX-ready tables, and
figures under `results/descriptive/`, `results/descriptive/appendix_b_tables/`, and
`results/descriptive/appendix_b_figures/`.

## Interpretation

Pull request size and contributor experience exhibit strong right-skew, with
substantial mean--median discrepancies and several extreme outliers. These patterns
support the paper's use of log-transformed controls and robust/sensitivity modeling
procedures.
