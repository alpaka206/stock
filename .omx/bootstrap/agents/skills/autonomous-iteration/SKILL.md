# autonomous-iteration

name: autonomous-iteration
description: choose the next smallest verifiable task and keep moving until the exit condition is met.

## Trigger
- when unattended work must continue without waiting for the user
- when the top P0 item needs to be broken into an executable step
- when an iteration must end with implementation, verification, and state updates

## Do Not Trigger
- when the task is blocked only by missing secrets or missing external access
- when the work is purely read-only and no execution decision is needed

## Rules
- keep iterations small and leave the repo in a testable state
- update journal, state, backlog, and next-prompt files after each iteration
- do not print, commit, or push secrets
- prioritize PRIMARY_TASK and MIN_EXIT_CONDITION over convenience work
- use a short consensus loop for large or risky changes before execution
