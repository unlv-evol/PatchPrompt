# Illustrative Qualitative Evidence Dataset

This file summarizes the paper-referenced illustrative cases used in the stage-based qualitative discussion.
The companion CSV contains the full canonical dataset record for each selected case, augmented with the paper section and interpretive role.

The examples are not treated as a statistically representative sample. They are purposefully selected to illustrate mechanisms suggested by the quantitative models.

## Included Examples

Note: the current paper draft does not identify a separate case-level illustrative example for the lifecycle/Axis B discussion; therefore this artifact includes only the explicitly named cases from the Gate 0, Gate 1, and Gate 2 illustrative subsections.

### PN-19 — 4.3.1 Gate 0: Code Generation

- **Outcome class:** PN
- **Prompt scores:** C=1.0, S=1.0, V=1.0, PQS=3
- **Fraction adopted:** nan
- **Illustrative role:** Implementation-oriented prompt enabling code generation despite non-adoption
- **Interpretation:** A bounded implementation objective can elicit actionable code even when verification remains lightweight and the generated code is not ultimately adopted.
- **PR link:** https://github.com/laravel-json-api/core/pull/12
- **Conversation link:** https://chat.openai.com/share/e9555822-4ffb-4845-8e40-0bc6cbbc658d

### NE-3 — 4.3.1 Gate 0: Code Generation

- **Outcome class:** NE
- **Prompt scores:** C=1.0, S=0.0, V=0.0, PQS=1
- **Fraction adopted:** nan
- **Illustrative role:** Conceptual/naming-oriented prompt limiting code generation
- **Interpretation:** Technical domain context alone is insufficient when the prompt does not request a bounded implementation artifact.
- **PR link:** https://github.com/SalesforceCommerceCloud/pwa-kit/pull/1528
- **Conversation link:** https://chat.openai.com/share/d5a18a26-08b3-47ea-a1ac-952dee512285

### PA-22 — 4.3.2 Gate 1: Code Adoption

- **Outcome class:** PA
- **Prompt scores:** C=1.0, S=2.0, V=2.0, PQS=5
- **Fraction adopted:** 6.67
- **Illustrative role:** Explicit constraints and observable correctness supporting adoption
- **Interpretation:** High specificity and explicit verification cues make generated code easier to evaluate and trust for adoption.
- **PR link:** https://github.com/jaoafa/VCSpeaker.kt/pull/70
- **Conversation link:** https://chat.openai.com/share/be37cf76-8d76-4db7-a056-129e216f0fad

### PN-19 — 4.3.2 Gate 1: Code Adoption

- **Outcome class:** PN
- **Prompt scores:** C=1.0, S=1.0, V=1.0, PQS=3
- **Fraction adopted:** nan
- **Illustrative role:** Generated but weakly evaluable code limiting adoption
- **Interpretation:** A prompt can generate plausible code but still provide insufficient acceptance conditions for confident integration.
- **PR link:** https://github.com/laravel-json-api/core/pull/12
- **Conversation link:** https://chat.openai.com/share/e9555822-4ffb-4845-8e40-0bc6cbbc658d

### PA-78 — 4.3.3 Gate 2: Integration Depth

- **Outcome class:** PA
- **Prompt scores:** C=2.0, S=2.0, V=1.0, PQS=5
- **Fraction adopted:** 84.84
- **Illustrative role:** Strong contextual grounding enabling deep integration
- **Interpretation:** Rich surrounding implementation context aligns the generated solution with the existing codebase, supporting deeper reuse.
- **PR link:** https://github.com/VyProductions/SeniorDesign/pull/57
- **Conversation link:** https://chat.openai.com/share/968d797a-0ef8-4644-91b9-70d1a3d0c016

### PA-24 — 4.3.3 Gate 2: Integration Depth

- **Outcome class:** PA
- **Prompt scores:** C=1.0, S=2.0, V=1.0, PQS=4
- **Fraction adopted:** 7.69
- **Illustrative role:** High specificity without sufficient contextual grounding limiting integration depth
- **Interpretation:** A highly specific prompt can still produce generic output when the surrounding implementation context is weak, resulting in limited reuse.
- **PR link:** https://github.com/viets-software-club/truffle-ai-backend/pull/52
- **Conversation link:** https://chat.openai.com/share/48bd44b4-13a7-4ff8-9938-2214f0b17f6b
