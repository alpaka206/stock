# multi-agent-consensus

name: multi-agent-consensus
description: run a short planner -> critic -> architect -> executor loop before risky work.

## Trigger
- before large feature work
- before risky architectural or deployment changes
- after repeated failures when the plan needs to be recalibrated

## Do Not Trigger
- for tiny one-file fixes with an obvious next step
- when it would only duplicate a decision already recorded in state or journal

## Rules
- keep the loop short and execution-oriented
- record the conclusion, not a long transcript
- prefer the safest reversible plan when roles disagree
- move to the next verifiable action immediately after consensus
- never expose secrets in role discussion or summaries
