# Tests And Docs Checklist

Use this prompt when finishing a change that should leave behind clean verification and documentation.

## Verify
- Run the smallest relevant lint, typecheck, build, test, smoke, or guard command.
- Prefer fixing the failing step before widening the verification gate.

## Docs And State
- Update only the state files and docs that materially changed.
- Remove placeholder text, mojibake, raw unicode escapes, and accidental question-mark corruption.
- Keep loop journals and verify notes readable and specific.
