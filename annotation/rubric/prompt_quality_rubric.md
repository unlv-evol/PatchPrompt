# Prompt Quality Rubric

Each developer prompt is scored on three dimensions from 0 to 2.

## Context

- 0: little or no grounding in code, files, framework, workflow, or environment.
- 1: partial grounding but missing concrete locus or evidence.
- 2: explicit locus plus concrete evidence such as files, APIs, constraints, or error traces.

## Specificity

- 0: broad or open-ended request.
- 1: partially constrained request with some expected behavior.
- 2: precise task boundaries, output format, and implementation constraints.

## Verification

- 0: no test, oracle, expected behavior, or validation instruction.
- 1: informal expected behavior or manual check.
- 2: explicit tests, acceptance criteria, or executable validation path.

`PQS = Context + Specificity + Verification`.
