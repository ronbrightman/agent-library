Frozen copy combining two Vercel sources, both MIT:
1. `vercel-labs/agent-skills` (skills/web-design-guidelines/SKILL.md) —
   license confirmed via that repo's README "## License / MIT" section
   (no separate root LICENSE file exists in that repo).
2. `vercel-labs/web-interface-guidelines` (command.md) — the actual
   rule content the skill fetches live upstream; license confirmed via
   its own root LICENSE file (MIT, copyright Vercel Labs 2025), copied
   here as LICENSE-web-interface-guidelines.

**Deliberate edit:** the upstream SKILL.md live-fetches command.md on
every run via WebFetch, which defeats the point of freezing a copy. This
version reads the local `reference/web-interface-guidelines.md` file
instead (a byte-exact copy of command.md as of 2026-07-20). Re-run the
original fetch step manually later if you want to pick up upstream
changes.
