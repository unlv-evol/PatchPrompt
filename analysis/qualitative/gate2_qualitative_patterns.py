"""Generate Gate 2 qualitative evidence tables.

Gate 2 examines integration depth among adopted PA cases.  The evidence table
focuses on contextual grounding, alignment with existing implementation
structures, project-specific integration constraints, and downstream adaptation
requirements.
"""
try:
    from .gate_qualitative_patterns_common import build_pattern_table, write_csv_xlsx_pdf, write_gate_readme
except ImportError:  # pragma: no cover
    from gate_qualitative_patterns_common import build_pattern_table, write_csv_xlsx_pdf, write_gate_readme

GATE = "gate2"
TITLE = "GATE 2 Qualitative Patterns"

CASES = [
    {
        "Case ID": "PA-78",
        "Structural Pattern": "Strong contextual grounding enabling deep reuse",
        "Prompt Excerpt": "I want to refactor this program, which takes in an amount of change as a user input, and then outputs how many of each bill and coin you would give back.",
        "Why Representative": "Provides program context and a refactoring target, allowing generated code to align with existing implementation.",
        "Integration Depth Category": "High",
        "Notes": "Paper-referenced high-reuse example.",
    },
    {
        "Case ID": "PA-23",
        "Structural Pattern": "Rich project artifacts supporting direct integration",
        "Prompt Excerpt": "I'd like to rewrite the following test case: describe('#1163 - https://github.com/jsdom/jsdom/issues/...') with sample DOM setup and expectations.",
        "Why Representative": "Includes test-case structure and expected behavior, supporting direct integration of generated changes.",
        "Integration Depth Category": "High",
        "Notes": "Recommended high-depth example from Gate 2 instructions.",
    },
    {
        "Case ID": "PA-21",
        "Structural Pattern": "Rich project artifacts supporting direct integration",
        "Prompt Excerpt": "'use client'; import Link from 'next/link'; ... useDeleteLeagueMutation ... export default function LeagueList(...) ...",
        "Why Representative": "Includes surrounding component and mutation code that anchors the generated output in existing project structure.",
        "Integration Depth Category": "High",
        "Notes": "Recommended high-depth example from Gate 2 instructions.",
    },
    {
        "Case ID": "PA-84",
        "Structural Pattern": "Strong contextual grounding enabling deep reuse",
        "Prompt Excerpt": "C++/CGIString prompt with code snippets and function context for direct implementation.",
        "Why Representative": "Includes C++ code and function context, supporting near-direct reuse.",
        "Integration Depth Category": "High",
        "Notes": "Additional high-reuse PA example.",
    },
    {
        "Case ID": "PA-61",
        "Structural Pattern": "Contextual grounding with adaptation requirements",
        "Prompt Excerpt": "What is tailwindcss and can you make a simple code snippet that shows its use and what it does?",
        "Why Representative": "Includes Tailwind/React framing and code context, but still requires adaptation to fit project conventions.",
        "Integration Depth Category": "Medium",
        "Notes": "Recommended moderate example.",
    },
    {
        "Case ID": "PA-16",
        "Structural Pattern": "Project-constrained integration",
        "Prompt Excerpt": "When using activerecord-multi-tenant library in my Rails project, filters do not work. I prepared a fix and now I want to unit test it to see that the fix is actually working.",
        "Why Representative": "Rails/library-specific testing context supports reuse but requires framework-specific adaptation.",
        "Integration Depth Category": "Medium",
        "Notes": "Recommended moderate example.",
    },
    {
        "Case ID": "PA-3",
        "Structural Pattern": "Contextual grounding with adaptation requirements",
        "Prompt Excerpt": "I'm creating an open source collection of UI/UX design problem statements for freshers. Here's a category I have curated [...].",
        "Why Representative": "Structured JSON/category examples support reuse, but integration still requires adaptation to project content.",
        "Integration Depth Category": "Medium",
        "Notes": "Recommended moderate example.",
    },
    {
        "Case ID": "PA-24",
        "Structural Pattern": "High specificity but shallow integration",
        "Prompt Excerpt": "In TypeScript: could you create an enum consisting of 5 categories, which are used to categorize software projects? Could you then initialize variables which have as a type a list of this enum.",
        "Why Representative": "The TypeScript enum task is specific but weakly grounded in surrounding implementation context.",
        "Integration Depth Category": "Low",
        "Notes": "Paper-referenced low-reuse example.",
    },
    {
        "Case ID": "PA-22",
        "Structural Pattern": "Generic implementation with limited contextual alignment",
        "Prompt Excerpt": "Kotlin の sksamuel/scrimage ライブラリで、画像上に文字列を描画し、文字列の縁取りをするコードを生成してください。文字の色は白、縁は黒で描画します。",
        "Why Representative": "The image-rendering task is specific and evaluable but lacks surrounding project code.",
        "Integration Depth Category": "Low",
        "Notes": "Recommended low-reuse example.",
    },
    {
        "Case ID": "PA-34",
        "Structural Pattern": "High specificity but shallow integration",
        "Prompt Excerpt": "TypeScript implementation request that defines a specific bounded task but gives limited surrounding project context.",
        "Why Representative": "Specific TypeScript task with limited surrounding code context, resulting in shallow reuse.",
        "Integration Depth Category": "Low",
        "Notes": "Additional low-reuse PA case.",
    },
]

README = """
Gate 2 qualitative evidence table

Purpose: This table supports the Gate 2 integration-depth discussion by showing
recurring contextual-alignment patterns among PA cases. Gate 2 focuses on the
extent to which adopted LLM-generated code is reused in the final implementation.

Structural patterns emphasize contextual grounding, surrounding implementation
artifacts, project-specific constraints, adaptation requirements, and reuse depth.

Selection logic: examples were purposefully selected to span high, medium, and
low integration-depth cases while varying Context scores, technical domains, and
adaptation requirements. They support qualitative transparency rather than
statistical representativeness.
"""


def main() -> None:
    table, full = build_pattern_table(CASES, GATE)
    write_csv_xlsx_pdf(table, full, GATE, TITLE)
    write_gate_readme(GATE, README)


if __name__ == "__main__":
    main()
