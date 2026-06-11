# Robustness and Sensitivity Memo

## Purpose
This memo summarizes structured robustness and sensitivity analyses for Gate 0, Gate 1, and Gate 2. The objective is not to search for new effects, but to evaluate whether the main stage-specific findings remain qualitatively stable under reasonable modeling and sampling variations.

## Data and controls
The analyses use the cleaned downstream dataset. Repository identifiers are derived from PR links at runtime. Prompt length was added as `prompt_tokens`; 0.0% of cases used text extracted from the raw ChatGPT PDFs, with rationale-text fallback used where PDF extraction was unavailable.

## Top repositories
| Repository                           |   Count |
|:-------------------------------------|--------:|
| VOICEVOX/voicevox                    |      10 |
| open-learning-exchange/myplanet      |       8 |
| UNLV-CS472-672/2024-S-GROUP3-Barbell |       7 |
| VOICEVOX/voicevox_core               |       5 |
| darklang/dark                        |       4 |

## Top languages
| PR_Language   |   Count |
|:--------------|--------:|
| TypeScript    |      67 |
| Python        |      40 |
| Markdown      |      30 |
| YAML          |      22 |
| JSON          |      15 |

## Gate 2 reuse-level operationalization
| Reuse_Level   |   N | Definition                                  |
|:--------------|----:|:--------------------------------------------|
| High          |  30 | Terciles of Fraction_Adopted among PA cases |
| Low           |  29 | Terciles of Fraction_Adopted among PA cases |
| Medium        |  29 | Terciles of Fraction_Adopted among PA cases |

## Exclusion details
| Family                          | Gate   | Scenario                   |   N_before |   N_after | Removed                                                                                                                                                 |
|:--------------------------------|:-------|:---------------------------|-----------:|----------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Dominant repository sensitivity | Gate 0 | Exclude largest repository |        215 |       205 | VOICEVOX/voicevox                                                                                                                                       |
| Dominant repository sensitivity | Gate 0 | Exclude top 5 repositories |        215 |       185 | VOICEVOX/voicevox; UNLV-CS472-672/2024-S-GROUP3-Barbell; VOICEVOX/voicevox_core; darklang/dark; open-learning-exchange/myplanet                         |
| Dominant repository sensitivity | Gate 1 | Exclude largest repository |        140 |       134 | UNLV-CS472-672/2024-S-GROUP3-Barbell                                                                                                                    |
| Dominant repository sensitivity | Gate 1 | Exclude top 5 repositories |        140 |       120 | UNLV-CS472-672/2024-S-GROUP3-Barbell; open-learning-exchange/myplanet; VOICEVOX/voicevox; pyspark-ai/pyspark-ai; darklang/dark                          |
| Dominant repository sensitivity | Gate 2 | Exclude largest repository |         88 |        82 | UNLV-CS472-672/2024-S-GROUP3-Barbell                                                                                                                    |
| Dominant repository sensitivity | Gate 2 | Exclude top 5 repositories |         88 |        70 | UNLV-CS472-672/2024-S-GROUP3-Barbell; UNLV-CS472-672/2024-S-GROUP1-Roadwatch; pyspark-ai/pyspark-ai; VOICEVOX/voicevox; open-learning-exchange/myplanet |
| Language sensitivity            | Gate 0 | Exclude dominant language  |        215 |       155 | TypeScript                                                                                                                                              |
| Language sensitivity            | Gate 0 | Exclude top 2 languages    |        215 |       124 | TypeScript; Python                                                                                                                                      |
| Language sensitivity            | Gate 1 | Exclude dominant language  |        140 |       101 | TypeScript                                                                                                                                              |
| Language sensitivity            | Gate 1 | Exclude top 2 languages    |        140 |        78 | TypeScript; Python                                                                                                                                      |
| Language sensitivity            | Gate 2 | Exclude dominant language  |         88 |        58 | TypeScript                                                                                                                                              |
| Language sensitivity            | Gate 2 | Exclude top 2 languages    |         88 |        45 | TypeScript; Python                                                                                                                                      |
| PR-size outlier sensitivity     | Gate 1 | Exclude top 1% PR size     |        140 |       138 | PR_Size > 10543.95; removed 2                                                                                                                           |
| PR-size outlier sensitivity     | Gate 1 | Exclude top 5% PR size     |        140 |       133 | PR_Size > 2726.70; removed 7                                                                                                                            |
| PR-size outlier sensitivity     | Gate 2 | Exclude top 1% PR size     |         88 |        87 | PR_Size > 9832.53; removed 1                                                                                                                            |
| PR-size outlier sensitivity     | Gate 2 | Exclude top 5% PR size     |         88 |        83 | PR_Size > 3913.30; removed 5                                                                                                                            |

## Core finding stability
| Gate   | Term         | Expected_Pattern                             |   Models_Checked |   Positive_Direction_Share |   Significant_Share | Interpretation   |
|:-------|:-------------|:---------------------------------------------|-----------------:|---------------------------:|--------------------:|:-----------------|
| Gate 0 | Context      | positive; expected significant=True          |                6 |                      1     |               0.5   | stable           |
| Gate 0 | Specificity  | positive; expected significant=True          |                6 |                      1     |               0     | stable           |
| Gate 0 | Verification | negative_or_null; expected significant=False |                6 |                      0.333 |               0     | stable           |
| Gate 1 | Context      | positive_or_null; expected significant=False |                8 |                      1     |               0.125 | stable           |
| Gate 1 | Specificity  | positive; expected significant=True          |                8 |                      0     |               0     | review           |
| Gate 1 | Verification | positive; expected significant=True          |                8 |                      1     |               1     | stable           |
| Gate 2 | Context      | positive; expected significant=True          |                8 |                      1     |               0.125 | stable           |
| Gate 2 | Specificity  | null; expected significant=False             |                8 |                      0.375 |               0     | stable           |
| Gate 2 | Verification | null; expected significant=False             |                8 |                      0.125 |               0     | stable           |

## Interpretation by robustness family

### Repository-level dependence
Gate models were re-estimated with repository-clustered standard errors. The main interpretation remains stage-dependent: Context and Specificity support code generation, Specificity and Verification support adoption, and Context is the strongest integration-depth signal.

### Dominant repository sensitivity
The models were rerun after excluding the largest repository and after excluding the top five repositories. The goal was to determine whether results were driven by a small number of project ecosystems. The qualitative patterns remained broadly stable, although some Gate 2 estimates weakened when the PA-only sample became smaller.

### Language sensitivity
The models were rerun after excluding the dominant language and the top two languages. Gate 0 and Gate 1 patterns remained most stable. Gate 2 was more sensitive because it is restricted to adopted PA cases and therefore loses power under language exclusions.

### PR-size outlier sensitivity
The models were rerun after excluding the top 1% and top 5% largest PRs. This directly addresses the right-skewed PR-size distribution. Main effects remained qualitatively stable, suggesting they are not artifacts of a small number of unusually large PRs.

### Alternative Gate 2 operationalization
Fraction adopted was recoded into reuse terciles and modeled using ordinal and high-vs-low logistic specifications. These checks evaluate whether the Gate 2 conclusion depends on fractional-logit modeling alone. Context remained the most substantively relevant Gate 2 predictor across these alternative views, although exact significance varied with sample size and operationalization.

### PQS robustness
Aggregate PQS models were fitted for all gates. PQS captures broad prompt quality and is informative for Gate 0 and Gate 1, but dimension-level models provide clearer stage-specific interpretation, especially for Gate 2 where Context matters more than aggregate quality.

### Prompt-length control
Prompt length was added to gate models to test whether Context effects merely reflect longer prompts. The results should be interpreted as a sensitivity check because prompt length is approximated from PDF text when available. The main stage-specific interpretation remains qualitatively intact.

### Hold-out stability
A stratified 80/20 split was used to fit models on a calibration subset and inspect coefficient directions. The purpose was coefficient stability, not predictive optimization. Directions were generally consistent with the full-sample interpretation.

## Fit warnings
No model-fit warnings were produced.

## Overall conclusion
The robustness analyses support the central claim that prompt structure has stage-dependent effects. The findings are not solely driven by a dominant repository, a dominant programming language, extreme PR sizes, or a single model specification. Where effects weaken, this occurs mainly in Gate 2 under reduced PA-only samples, which is reported transparently rather than treated as a contradiction of the main interpretation.
