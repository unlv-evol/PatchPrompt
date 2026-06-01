# Prompt-PatchTrack Human Annotation Codebook

This codebook was used during the prompt-quality annotation phase of the PatchPrompt study.

---

# Context (Scale 0–2)

Measures how grounded the prompt is in concrete technical context.

| Score | Definition | Examples | Decision Rules |
|---------|------------|------------|------------|
| **2 – High Context** | Prompt gives explicit location or technical evidence | File path, function name, stack trace, error message, code snippet, config file, workflow, API version, runtime details | - If any explicit technical artifact is present, score = 2<br>- If the prompt is semi-grounded but nonspecific, score = 1<br>- If completely generic, score = 0 |
| **1 – Medium Context** | Some grounding, but not specific enough | Mentions technology or broad API ("React component", "Kubernetes job") but without file/function/code | |
| **0 – No Context** | No technical anchors | "How do I fix this?", "What's wrong here?", general conceptual questions | |

---

# Specificity (Scale 0–2)

Measures whether the developer defines goal, scope, constraints, or instructions.

| Score | Definition | Examples | Decision Rules |
|---------|------------|------------|------------|
| **2 – High Specificity** | Prompt defines goal + scope and/or constraints | "Optimize this function to run in O(n)." "Return JSON in this format…" | - If the prompt describes both what and how/under what constraints, score = 2<br>- If the goal is clear, but details missing, score = 1<br>- If unclear or general, score = 0 |
| **1 – Medium Specificity** | Clear goal, but missing scope or constraints | "Fix this error" with a provided code snippet | |
| **0 – Low Specificity** | Vague or lacks problem definition | "Improve this", "Make this better", "Any suggestions?" | |

---

# Verification (Scale 0–2)

Measures whether the prompt provides rules or conditions for correctness.

| Score | Definition | Examples | Decision Rules |
|---------|------------|------------|------------|
| **2 – Explicit Verification** | Prompt defines correctness criteria or expected behavior | I/O examples, invariants, "should return X if Y", error conditions | - If correctness is stated clearly, score = 2<br>- If correctness is only implied, score = 1<br>- If no correctness cues, score = 0 |
| **1 – Implicit Verification** | Correctness is implied | "Make this valid YAML", "Ensure backward compatibility" | |
| **0 – No Verification** | No correctness conditions | "Rewrite this code", "Explain this" | |

---

# Prompt Efficiency (Scale 0–5)

Counts the number of developer turns needed to get a usable result.

| Score | Definition | Special Rules |
|---------|------------|------------|
| **5** | One-shot usable answer | For conversations > 5 turns but naturally exploratory, cap at E = 3 |
| **4** | One follow-up clarification | |
| **3** | 3–4 turns, focused refinements | |
| **2** | 5–6 turns | |
| **1** | 7–9 turns OR scattered attempts | |
| **0** | No convergence | |

---

# Relationship to the Study

This rubric was used during human annotation of the validation subset and served as the basis for:

- Context (C) scoring
- Specificity (S) scoring
- Verification (V) scoring
- Prompt Efficiency (E) scoring

The resulting annotations were used to evaluate agreement between human annotators and LLM-assisted annotations during the RQ1 prompt-evaluation validation phase.