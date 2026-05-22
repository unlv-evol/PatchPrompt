# Full LLM Annotation Prompt

For the following developer prompt (from a ChatGPT conversation) and corresponding pull request (PR) description, evaluate the prompt using the PatchTrack-Prompt rubric for Context (C), Specificity (S), Verification (V), and Prompt Efficiency (E).

## Input Template

Developer prompt:

```text
--- developer's ChatGPT input here ---
```

PR description:

```text
--- pull request body, summary, or reviewer comment text here ---
```

## Instructions

- Focus your evaluation ONLY on the developer's ChatGPT prompt text.
- The evaluation must be based ONLY on the developer’s prompt text extracted from the PDF.
- For the developer prompt, consider all the refinements from the ChatGPT conversation.
- The provided ChatGPT share URL and GitHub PR URL must both be included in the final JSON output as metadata, under `Conversation_Link` and `PR_Link`.
- Do NOT attempt to open or analyze these URLs. They are included strictly for tracking and record-keeping.

## Context (C: 0–2)

Does the prompt provide grounding in the relevant code, file, API, framework, workflow, or execution environment?

- `2` = Explicit locus AND concrete evidence, such as file path, function/API name, code snippet, YAML fragment, error/log, or environment detail.
- `1` = Partial grounding, either locus OR evidence, but not both.
- `0` = No concrete locus or evidence; generic question.

## Specificity (S: 0–2)

Does the prompt define the intended goal, scope, and constraints? Does it guide the LLM toward a structured or bounded output?

- `2` = Explicit goal + scope + constraints, possibly including preconditions/postconditions, expected I/O examples, invariants, output format, or reasoning instructions.
- `1` = Clear goal but missing scope or constraints.
- `0` = Vague, broad, or underspecified request.

## Verification (V: 0–2)

Does the prompt define, imply, or enable correctness checking? Verification cues include expected behavior, I/O examples, type/static rules, formatting rules, invariants, or policy conditions.

- `2` = Explicit correctness condition, such as example input/output, behavioral rule, type/static constraint, doc/spec rule, or test-like expectation.
- `1` = Implicit correctness, such as alignment with existing code/docs, API stability, validity expectations, or avoiding regressions.
- `0` = No correctness cues.

Adaptive rule: If a new verification cue appears, describe it briefly, assign a provisional score, and flag it as a candidate for a new Verification family.

## Prompt Efficiency (E: 0–5)

How efficiently did the developer converge on a usable LLM response? Count only developer turns after the first substantive prompt.

- `5` = One-shot precision.
- `4` = Minor refinement.
- `3` = Moderate refinement.
- `2` = Extended refinement.
- `1` = Inefficient success.
- `0` = No convergence or abandoned conversation.

Note: For very long, exploratory conversations (>5 turns) that still produce a usable result, cap E at 3 unless the task itself is inherently exploratory.

## Output Format

Return a single JSON object:

```json
{
  "PR_Link": "--- full GitHub PR URL ---",
  "Conversation_Link": "--- ChatGPT developer prompt URL link ---",
  "Classification": "--- PA / PN / NE / CL ---",
  "Context": 0,
  "Specificity": 0,
  "Verification": 0,
  "Efficiency": 0,
  "Rationale": "Brief justification referencing ONLY the prompt text explaining each score (C, S, V, E). Do not reference PR outcome or patch content."
}
```

## Note on Downstream Analysis

Efficiency was included in the original annotation prompt but excluded from downstream modeling due to construct-validity concerns. The package preserves Efficiency where available for transparency while modeling only Context, Specificity, and Verification.
