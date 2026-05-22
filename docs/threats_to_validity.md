# Threats to Validity and Trustworthiness

This document summarizes validity considerations for the replication package and aligns them with the paper’s threats-to-validity discussion.

## Construct Validity

The study operationalizes prompt quality using three primary dimensions:

- Context
- Specificity
- Verification

Prompt Efficiency was initially considered during annotation design but was excluded from downstream modeling because the shared ChatGPT conversations do not reliably capture the full prompting history. Developers may have shared only selected or final interactions, making turn-count-based efficiency an unreliable measure of actual effort.

The replication package preserves this decision by keeping Efficiency in the annotation artifacts where available, while excluding it from the downstream modeling scripts.

## Annotation Construct Validity

Human and LLM annotations are compared using ordinal agreement metrics. The package includes the human gold-standard subset, LLM V1 annotations, agreement scripts, and the derived class-aware annotation policy.

Verification is treated cautiously because correctness-related signals are often implicit, distributed across the prompt, or dependent on developer intent. This is why the package reproduces the paper’s selective automation policy rather than applying a uniform automation rule.

## Internal Validity

The study is observational. Regression models identify associations between prompt structure and PR outcomes; they do not establish causal effects.

Potential confounders include:

- repository norms,
- reviewer expectations,
- developer experience,
- PR size and complexity,
- task type,
- project maturity,
- unobserved social or organizational factors.

The package mitigates these concerns by including control variables where available, stage-specific modeling, diagnostics, and robustness checks.

## External Validity

The dataset is drawn from real-world GitHub pull requests involving developer-shared ChatGPT conversations. Findings may not generalize to:

- private repositories,
- organizations with different review practices,
- newer LLM systems,
- interactions that were never publicly shared,
- developer workflows outside pull-request-based collaboration.

The package includes raw artifacts and processed datasets to support future external replication on additional corpora.

## Conclusion Validity

Statistical conclusions may be affected by sample size, class imbalance, skewed PR-size distributions, and modeling assumptions.

The package addresses this through:

- log transformations for skewed variables where appropriate,
- model diagnostics,
- separation checks for logistic models,
- proportional-hazards diagnostics for lifecycle models,
- sensitivity analyses,
- repository-aware robustness checks where applicable.

## Transferability

The package separates raw, intermediate, and processed data so that future researchers can adapt the workflow to other datasets.

The most transferable components are:

- the prompt-quality rubric,
- the annotation reliability workflow,
- the gate-based modeling structure,
- output validation scripts,
- notebook walkthroughs.

## Dependability

Dependability is supported through:

- versioned scripts,
- deterministic run configuration,
- package manifests,
- expected-output validation,
- generated run metadata,
- documented reproduction steps.

These artifacts make it easier to determine whether future results differ because of data changes, software changes, or methodological changes.

## Confirmability

Confirmability is supported by preserving:

- raw PatchTrack artifacts,
- raw ChatGPT PDFs,
- human annotation data,
- LLM annotation data,
- scoring rationale fields where available,
- scripts used to regenerate results,
- generated output manifests.

The package is intended to make the analysis auditable rather than relying only on prose descriptions in the paper.

## Limitations of the Replication Package

The default pipeline begins from the cleaned downstream dataset rather than fully re-mining GitHub and ChatGPT artifacts. This reflects the current artifact scope: reproducing the paper’s analyses from the validated study data. Raw files are included for traceability and future extension, but full mining automation may require additional project-specific tools or credentials.
