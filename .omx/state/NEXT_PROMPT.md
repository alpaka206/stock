# Next Prompt

Next iteration order:
1. Read `AGENTS.md`, `TASK.md`, `STATE.md`, `BACKLOG.md`, `DISCORD_STATUS.md`, and `VERIFY_LAST_FAILURE.md`.
2. If `VERIFY_LAST_FAILURE.md` is not `clear`, make failure remediation the top priority.
3. Before risky work, run a short `planner -> critic -> architect -> executor` consensus loop.
4. Treat `.env.discord` as read-only secret input; check existence and key presence only.
5. Pick the smallest executable P0 item.
6. Update journal, state, backlog, and Discord status.
