# Dataset Schema

## Canonical downstream dataset

`dataset/processed/final_analysis_dataset.csv` is the canonical cleaned dataset used for downstream analysis and modeling.

The file is preserved exactly as supplied for the final analysis. The pipeline does not add redundant columns to this canonical artifact.

## Canonical columns

| Column | Meaning |
|---|---|
| `Case ID` | Unique case identifier, e.g., `PA-1`. |
| `PR_Link` | GitHub pull request URL. Used to derive repository and PR number during analysis. |
| `Conversation_Link` | ChatGPT conversation URL associated with the PR. |
| `Outcome_Class` | PatchTrack outcome class: PA, PN, NE, or CL. |
| `Context` | Prompt Context score on the 0--2 rubric. |
| `Specificity` | Prompt Specificity score on the 0--2 rubric. |
| `Verification` | Prompt Verification score on the 0--2 rubric. |
| `Rationale` | Annotation rationale explaining Context, Specificity, and Verification scores. |
| `PQS ` | Prompt Quality Score. The trailing space is preserved in the canonical file. |
| `PR_Size` | Pull request size metric used as a control variable. |
| `Log_PR_Size` | Log-transformed pull request size. |
| `Has_Code` | Indicator for whether the interaction produced code. |
| `Adopt_Any` | Indicator for whether generated code was adopted. |
| `Fraction_Adopted` | Percentage/fraction of generated code retained in the final implementation. |
| `Status` | PR lifecycle status. Used to derive merge and close indicators. |
| `Exp_Author_Repo` | Contributor experience in the repository. |
| `Time_To_Event` | Time-to-resolution or censoring duration used in lifecycle analysis. |
| `PR_Language` | Main programming language associated with the pull request. |
| `Merged_By_Author` | Indicator/metadata for author merge behavior where available. |
| `Closed_By_Author` | Indicator/metadata for author close behavior where available. |
| `Closed_By_Author_new` | Revised close-by-author field where available. |

## Derived metadata

The following fields are intentionally not duplicated in the canonical dataset:

- `Repository`
- `PR_Number`
- `Merged`
- `Closed`

They are derived reproducibly in `analysis/common.py` and written to `dataset/processed/gate_model_dataset.csv`:

```text
Repository, PR_Number <- PR_Link
Merged, Closed        <- Status
PQS                   <- PQS  # normalized analysis alias only
```

This preserves fidelity with the finalized downstream analysis dataset while keeping all derived variables transparent and reproducible.

## RQ1 annotation-validation datasets

Section 4.1 uses separate validation artifacts under `annotation/validation/`.

### `human_gold_annotations.csv`

This is the stratified 30% human-consensus validation subset used as the gold standard for RQ1.

| Column | Meaning |
|---|---|
| `Case_ID` | Case identifier aligned with the canonical dataset. |
| `PR_Link` | GitHub pull request URL. |
| `Conversation_Link` | ChatGPT conversation URL. |
| `Classification` | Outcome class: PA, PN, NE, or CL. |
| `Human_Context` | Human consensus Context score. |
| `Human_Specificity` | Human consensus Specificity score. |
| `Human_Verification` | Human consensus Verification score. |
| `Human_Efficiency` | Preserved human Efficiency score, not used in downstream paper models. |
| `Human_Rationale` | Human annotation rationale. |

Expected validation subset size: 82 cases, with PA = 27, PN = 16, NE = 25, and CL = 14.

### `llm_annotations_v1_combined.csv`

This is the combined LLM-v1 annotation file across all outcome classes. RQ1 calculations use only the rows whose `Case_ID` appears in `human_gold_annotations.csv`.

| Column | Meaning |
|---|---|
| `Case_ID` | Case identifier aligned with the human gold subset and canonical dataset. |
| `PR_Link` | GitHub pull request URL. |
| `Conversation_Link` | ChatGPT conversation URL. |
| `Classification` | Outcome class: PA, PN, NE, or CL. |
| `LLM_Context` | LLM-v1 Context score. |
| `LLM_Specificity` | LLM-v1 Specificity score. |
| `LLM_Verification` | LLM-v1 Verification score. |
| `LLM_Rationale` | LLM-v1 annotation rationale. |

The aligned human--LLM validation pairs are generated at:

```text
results/rq1/rq1_human_llm_validation_pairs.csv
```
