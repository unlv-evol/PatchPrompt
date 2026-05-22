# Robustness and Sensitivity Analysis Summary

This file summarizes robustness checks for the stage-based models. The checks evaluate whether the main qualitative findings remain stable after excluding the dominant repository, excluding extreme pull-request sizes, excluding the most frequent programming language, and replacing individual prompt dimensions with aggregate PQS.

## Exclusion details

| Gate   | Scenario                    |   N_before |   N_after | Exclusion_Detail                                          |
|:-------|:----------------------------|-----------:|----------:|:----------------------------------------------------------|
| Gate 0 | Main sample                 |        214 |       214 | No exclusion                                              |
| Gate 0 | Exclude dominant repository |        214 |       204 | Excluded repository: VOICEVOX/voicevox                    |
| Gate 0 | Exclude extreme PR size     |        214 |       203 | Kept PR_Size <= 95th percentile (2536.50)                 |
| Gate 0 | Exclude dominant language   |        214 |       154 | Excluded language: TypeScript                             |
| Gate 1 | Main sample                 |        139 |       139 | No exclusion                                              |
| Gate 1 | Exclude dominant repository |        139 |       133 | Excluded repository: UNLV-CS472-672/2024-S-GROUP3-Barbell |
| Gate 1 | Exclude extreme PR size     |        139 |       132 | Kept PR_Size <= 95th percentile (2750.40)                 |
| Gate 1 | Exclude dominant language   |        139 |       100 | Excluded language: TypeScript                             |
| Gate 2 | Main sample                 |         87 |        87 | No exclusion                                              |
| Gate 2 | Exclude dominant repository |         87 |        81 | Excluded repository: UNLV-CS472-672/2024-S-GROUP3-Barbell |
| Gate 2 | Exclude extreme PR size     |         87 |        82 | Kept PR_Size <= 95th percentile (4006.40)                 |
| Gate 2 | Exclude dominant language   |         87 |        57 | Excluded language: TypeScript                             |

## Qualitative stability of main findings

### Gate 0
- Main sample: Context, Specificity.
- Exclude dominant repository: Context, Specificity.
- Exclude extreme PR size: Context, Specificity.
- Exclude dominant language: Context, Specificity.

### Gate 1
- Main sample: Specificity, Verification.
- Exclude dominant repository: Specificity, Verification.
- Exclude extreme PR size: Specificity, Verification.
- Exclude dominant language: Specificity, Verification.

### Gate 2
- Main sample: Context.
- Exclude dominant repository: Context.
- Exclude extreme PR size: Context.
- Exclude dominant language: no prompt dimension reaches p < 0.05.

## Fit warnings/failures

No model fits failed.
