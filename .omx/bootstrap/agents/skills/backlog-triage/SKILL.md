# backlog-triage

name: backlog-triage
description: split large goals into executable P0/P1/P2 items and reorder them conservatively.

## Trigger
- when backlog priority is unclear
- when a large task must be split into smaller verifiable units
- when repeated failures require a new execution order

## Do Not Trigger
- when the next small step is already obvious
- when the only blocker is missing credentials or permissions

## Rules
- P0 must stay directly tied to MIN_EXIT_CONDITION
- prefer small, checkable items over vague objectives
- mark secret-gated work as blocked instead of forcing it
- record why priorities changed
- do not remove necessary product, QA, or deployment work just to shorten the list
