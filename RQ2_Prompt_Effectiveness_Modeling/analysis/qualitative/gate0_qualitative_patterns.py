"""Generate Gate 0 qualitative evidence tables.

Gate 0 examines whether prompt structure leads ChatGPT to produce actionable
code.  This script creates purposefully selected evidence tables contrasting
implementation-oriented prompts with conceptual-oriented prompts.  The examples
are selected to show recurring structural patterns, not statistical
representativeness.
"""
try:
    from .gate_qualitative_patterns_common import build_pattern_table, write_csv_xlsx_pdf, write_gate_readme
except ImportError:  # pragma: no cover
    from gate_qualitative_patterns_common import build_pattern_table, write_csv_xlsx_pdf, write_gate_readme

GATE = "gate0"
TITLE = "GATE 0 Qualitative Patterns"

CASES = [
    {
        "Case ID": "PA-22",
        "Structural Pattern": "Implementation-oriented",
        "Prompt Excerpt": "Kotlin の sksamuel/scrimage ライブラリで、画像上に文字列を描画し、文字列の縁取りをするコードを生成してください。文字の色は白、縁は黒で描画します。",
        "Why Representative": "Defines a bounded Kotlin image-rendering task with explicit output constraints, enabling code synthesis.",
        "Generated Actionable Code?": "Yes",
        "Notes": "Paper-referenced Gate 1 example also used to show implementation framing at Gate 0.",
    },
    {
        "Case ID": "PN-19",
        "Structural Pattern": "Implementation-oriented",
        "Prompt Excerpt": "Hello can you give me a regex to match ULID format? This one is correct? [0-7][0-9A-HJKMNP-TV-Z]{25}",
        "Why Representative": "Requests a concrete regex artifact for a ULID format, so the prompt is codable even though adoption did not occur.",
        "Generated Actionable Code?": "Yes",
        "Notes": "Paper-referenced Gate 0/Gate 1 contrasting example.",
    },
    {
        "Case ID": "PA-78",
        "Structural Pattern": "Implementation-oriented",
        "Prompt Excerpt": "I want to refactor this program, which takes in an amount of change as a user input, and then outputs how many of each bill and coin you would give back.",
        "Why Representative": "Provides program context and asks for refactoring into a better implementation structure.",
        "Generated Actionable Code?": "Yes",
        "Notes": "Paper-referenced Gate 2 example; also illustrates implementation-oriented Gate 0 framing.",
    },
    {
        "Case ID": "PA-61",
        "Structural Pattern": "Implementation-oriented",
        "Prompt Excerpt": "What is tailwindcss and can you make a simple code snippet that shows its use and what it does?",
        "Why Representative": "Requests a TailwindCSS code snippet, explicitly asking for an executable artifact.",
        "Generated Actionable Code?": "Yes",
        "Notes": "Variation: instructional/example generation request.",
    },
    {
        "Case ID": "PN-25",
        "Structural Pattern": "Implementation-oriented",
        "Prompt Excerpt": "git diff は違いがあった場合のステータスコードは何でしょうか。ありがとうございます。diffはどうでしょうか。",
        "Why Representative": "Focuses on command behavior and shell-status handling, creating a bounded workflow/script-oriented task.",
        "Generated Actionable Code?": "Yes",
        "Notes": "Variation: CLI/workflow-oriented prompt.",
    },
    {
        "Case ID": "PA-24",
        "Structural Pattern": "Implementation-oriented",
        "Prompt Excerpt": "In TypeScript: could you create an enum consisting of 5 categories, which are used to categorize software projects? Could you then initialize variables which have as a type a list of this enum.",
        "Why Representative": "Asks for a concrete TypeScript enum and variable initialization, defining a bounded coding task.",
        "Generated Actionable Code?": "Yes",
        "Notes": "Paper-referenced Gate 2 contrasting example.",
    },
    {
        "Case ID": "NE-3",
        "Structural Pattern": "Conceptual-oriented",
        "Prompt Excerpt": "How are express.js middleware functions commonly named? What might you call an express.js middleware that adds a content security policy or other security headers?",
        "Why Representative": "Asks for naming conventions and middleware names rather than executable middleware implementation.",
        "Generated Actionable Code?": "No",
        "Notes": "Paper-referenced Gate 0 conceptual example.",
    },
    {
        "Case ID": "NE-4",
        "Structural Pattern": "Conceptual-oriented",
        "Prompt Excerpt": "What is faster in PHP: serialize vs json_encode?",
        "Why Representative": "Compares PHP serialization mechanisms and performance without requesting code or a bounded implementation.",
        "Generated Actionable Code?": "No",
        "Notes": "Technical but analytical/comparative prompt.",
    },
    {
        "Case ID": "NE-11",
        "Structural Pattern": "Conceptual-oriented",
        "Prompt Excerpt": "こちらの変更に対して、『VVMファイルからVoiceModelをコンストラクトする。』という表現について、生成・解放などの用語選択に関する意見が交わされました。",
        "Why Representative": "Discusses terminology for API/model construction rather than requesting a code artifact.",
        "Generated Actionable Code?": "No",
        "Notes": "Technical terminology/workflow-oriented NE case.",
    },
    {
        "Case ID": "NE-25",
        "Structural Pattern": "Conceptual-oriented",
        "Prompt Excerpt": "If testing a code requires unit testing private methods, what does that say about the design?",
        "Why Representative": "Asks about design implications of testing private methods instead of asking for implementation code.",
        "Generated Actionable Code?": "No",
        "Notes": "Additional technically grounded conceptual NE case.",
    },
]

README = """
Gate 0 qualitative evidence table

Purpose: This table supports the Gate 0 code-generation discussion by showing
recurring prompt structures associated with actionable code generation versus
conceptual or explanatory responses.

Structural patterns:
- Implementation-oriented: the prompt defines a concrete coding objective,
  requests an executable artifact, or sufficiently bounds the implementation
  space for code synthesis.
- Conceptual-oriented: the prompt focuses on naming guidance, explanation,
  architecture, workflow reasoning, performance discussion, or API semantics
  without requesting a concrete implementation artifact.

Selection logic: examples were purposefully selected to cover PA, PN, and NE
outcomes, variation in Context/Specificity/Verification scores, and diverse
technical domains. They are intended for qualitative transparency, not statistical
representativeness.
"""


def main() -> None:
    table, full = build_pattern_table(CASES, GATE)
    write_csv_xlsx_pdf(table, full, GATE, TITLE)
    write_gate_readme(GATE, README)


if __name__ == "__main__":
    main()
