# Code Review Policy

Gate order:
1. implement
2. lint / build / test
3. Codex review
4. approve or no blocking finding
5. then push / PR / develop integration

Severity:
- HIGH+: hold
- MEDIUM only: proceed with note
- LOW only: proceed
- final OK: no blocking finding

Verification failure policy:
- any failed guard or verify step becomes the next highest-priority task
- fix the exact failure first
- rerun the failed command, then rerun the full gate
- do not continue unrelated feature work while the failure is active unless it is explicitly blocked

Writing style:
- issue / PR / commit: Korean first
- style: concise noun/result form
- done criteria: checkable sentences
