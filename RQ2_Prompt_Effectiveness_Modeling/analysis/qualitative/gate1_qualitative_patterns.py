"""Generate Gate 1 qualitative evidence tables.

Gate 1 examines whether generated code is adopted.  The evidence table focuses
on evaluability, bounded implementation scope, correctness constraints, and
acceptance criteria that support or weaken developer confidence in adoption.
"""
try:
    from .gate_qualitative_patterns_common import build_pattern_table, write_csv_xlsx_pdf, write_gate_readme
except ImportError:  # pragma: no cover
    from gate_qualitative_patterns_common import build_pattern_table, write_csv_xlsx_pdf, write_gate_readme

GATE = "gate1"
TITLE = "GATE 1 Qualitative Patterns"

CASES = [
    {
        "Case ID": "PA-22",
        "Structural Pattern": "Explicitly evaluable implementation task",
        "Prompt Excerpt": "Using Kotlin with the sksamuel/scrimage library, generate code to draw text on an image with an outline. Render white text with a black border.",
        "Why Representative": "The expected visual result is observable: white text with a black outline.",
        "Generated Code?": "Yes",
        "Adopted?": "Yes",
        "Notes": "Paper-referenced adopted example.",
    },
    {
        "Case ID": "PA-23",
        "Structural Pattern": "Strong correctness constraints",
        "Prompt Excerpt": "I'd like to rewrite the following test case: describe('#1163 - https://github.com/jsdom/jsdom/issues/...') with sample DOM setup and expectations.",
        "Why Representative": "The prompt provides test-case context and expectations that support direct evaluation.",
        "Generated Code?": "Yes",
        "Adopted?": "Yes",
        "Notes": "Adopted test-related example.",
    },
    {
        "Case ID": "PA-21",
        "Structural Pattern": "Bounded implementation with concrete code context",
        "Prompt Excerpt": "'use client'; import Link from 'next/link'; ... useDeleteLeagueMutation ... export default function LeagueList(...) ...",
        "Why Representative": "Existing component/mutation code gives enough implementation context for adoption decisions.",
        "Generated Code?": "Yes",
        "Adopted?": "Yes",
        "Notes": "Adopted UI/API modification example.",
    },
    {
        "Case ID": "PA-3",
        "Structural Pattern": "Structured output expectations",
        "Prompt Excerpt": "I'm creating an open source collection of UI/UX design problem statements for freshers. Here's a category I have curated [...].",
        "Why Representative": "The prompt provides structured JSON/category examples and clear output shape expectations.",
        "Generated Code?": "Yes",
        "Adopted?": "Yes",
        "Notes": "Adopted structured-data example.",
    },
    {
        "Case ID": "PA-16",
        "Structural Pattern": "Testable implementation request",
        "Prompt Excerpt": "When using activerecord-multi-tenant library in my Rails project, filters do not work. I prepared a fix and now I want to unit test it to see that the fix is actually working.",
        "Why Representative": "The prompt asks for a unit test to validate a concrete Rails filtering fix.",
        "Generated Code?": "Yes",
        "Adopted?": "Yes",
        "Notes": "Adopted test/evaluation example.",
    },
    {
        "Case ID": "PN-19",
        "Structural Pattern": "Weakly evaluable generated solution",
        "Prompt Excerpt": "Hello can you give me a regex to match ULID format? This one is correct? [0-7][0-9A-HJKMNP-TV-Z]{25}",
        "Why Representative": "The regex task is concrete, but acceptance examples and framework-specific validation are limited.",
        "Generated Code?": "Yes",
        "Adopted?": "No",
        "Notes": "Paper-referenced generated-but-not-adopted example.",
    },
    {
        "Case ID": "PN-25",
        "Structural Pattern": "Implicit verification",
        "Prompt Excerpt": "What is the exit status code for git diff when differences are found? Thank you. Also, what about diff?",
        "Why Representative": "The prompt asks about command behavior but leaves adoption conditions implicit.",
        "Generated Code?": "Yes",
        "Adopted?": "No",
        "Notes": "Workflow/CLI-oriented PN example.",
    },
    {
        "Case ID": "PN-3",
        "Structural Pattern": "Exploratory implementation request",
        "Prompt Excerpt": "How can I log progress and handle worker output in this migration/concurrency context?",
        "Why Representative": "The prompt explores a logging approach in a concurrent environment without explicit acceptance criteria.",
        "Generated Code?": "Yes",
        "Adopted?": "No",
        "Notes": "Concurrency/logging PN example.",
    },
    {
        "Case ID": "PN-1",
        "Structural Pattern": "Underspecified acceptance criteria",
        "Prompt Excerpt": "Can you show me how to use YARP in a project to bypass CORS restrictions on an API?",
        "Why Representative": "The prompt requests a YARP/CORS setup but lacks project constraints and validation conditions.",
        "Generated Code?": "Yes",
        "Adopted?": "No",
        "Notes": "Proxy/configuration PN example.",
    },
    {
        "Case ID": "PN-2",
        "Structural Pattern": "Weak framework alignment",
        "Prompt Excerpt": "How can I configure a GitHub Action workflow for this Python project?",
        "Why Representative": "The prompt is workflow-oriented but lacks enough project-specific constraints for confident adoption.",
        "Generated Code?": "Yes",
        "Adopted?": "No",
        "Notes": "Additional PN example with weak evaluability.",
    },
]

README = """
Gate 1 qualitative evidence table

Purpose: This table supports the Gate 1 code-adoption discussion by showing
recurring prompt structures related to task boundedness, correctness
evaluability, developer confidence, and explicit versus implicit verification.

Structural patterns emphasize whether generated code is directly evaluable and
whether the prompt supplies enough constraints, expected behavior, framework
alignment, or acceptance conditions to support adoption.

Selection logic: examples were purposefully selected to include adopted PA cases
and generated-but-not-adopted PN cases across varied technical domains and score
configurations. They support transparency rather than statistical representativeness.
"""


def main() -> None:
    table, full = build_pattern_table(CASES, GATE)
    write_csv_xlsx_pdf(table, full, GATE, TITLE)
    write_gate_readme(GATE, README)


if __name__ == "__main__":
    main()
