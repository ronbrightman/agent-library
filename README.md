# agent-library

Portable [Claude Code](https://claude.com/claude-code) agents for
consumer (B2C) product work — `research`, `marketing`, `evaluation`, and
`design`. Distributed as a proper Claude Code plugin marketplace, so
getting them into any environment (a different computer, a fresh
cloud/mobile session, anywhere) is two commands instead of copying files
by hand.

## Get the agents in a new environment

Run these two commands once, in any Claude Code session:

```
claude plugin marketplace add ronbrightman/agent-library
claude plugin install product-agents@agent-library
```

That's it. The four agents (`research`, `marketing`, `evaluation`,
`design`) are now available in that environment, and stay up to date
automatically — auto-update is enabled on this marketplace, so future
improvements pushed here propagate without re-running anything.

(If you're in an interactive session rather than scripting it, the same
two things also work as slash commands: `/plugin marketplace add
ronbrightman/agent-library` then `/plugin install
product-agents@agent-library`.)

## What's in the plugin

- **`research`** — generates and researches feature ideas, grounded in
  real current B2C growth loops, retention/activation metrics, and
  monetization models. Read/web-search access only, no code-editing
  tools — it starts every run by researching current real examples,
  since this space moves fast and generic knowledge goes stale.
- **`marketing`** — generates and refines marketing/growth ideas and
  strategy (positioning, launch plans, pricing, competitive-alternative
  content), feeding the same evaluation flow as `research`'s feature
  ideas. Read/web-search access only.
- **`evaluation`** — scores and ranks ideas using the RICE framework
  (Reach × Impact × Confidence ÷ Effort), extended with explicit build
  cost, run cost, and founder-time dimensions — including a split of
  Effort itself into engineering effort (lightly weighted — delegated to
  Claude Code) vs. personal effort (fully weighted — the founder's own
  scarce time), so a ranking can distinguish "too much build" from "too
  much of my time." Read/web-search access only.
- **`design`** — turns an approved idea into a product spec plus 1-2
  visual/UX design directions, grounded in current real consumer-app
  UI/UX patterns rather than assumed taste. Read/web-search access only
  — it proposes, it doesn't build.

These four are meant to be paired with two project-specific agents,
`build` and `review`, that live in whatever repo you're actually working
in (not here) since they need to know that codebase's own structure and
conventions. See a target repo's own `AGENT_POLICY.md` for how the full
pipeline fits together end to end.

## Bundled skills

Each agent loads a small set of frozen reference skills via its own
`skills:` frontmatter — static, locally-owned copies of third-party
skills, not live plugin dependencies that could change out from under
you. They live under `plugins/product-agents/skills/`, one folder per
skill, each with its own `LICENSE`/`NOTICE.md` documenting where it came
from and under what license (all MIT or Apache-2.0, all confirmed
directly against the source repo, not assumed):

- `research` + `evaluation`: `product-manager-toolkit` (RICE, PRD,
  customer-interview templates), `competitive-teardown`,
  `product-discovery`, `product-analytics` — from
  `alirezarezvani/claude-skills`, MIT.
- `marketing`: `marketing-ideas`, `marketing-strategy-pmm`,
  `marketing-context`, `launch-strategy`, `competitor-alternatives`,
  `pricing-strategy` — a deliberately narrow subset of a much larger
  (47-skill) marketing bundle in the same repo, MIT, chosen for
  ideas/strategy rather than execution tactics.
- `design`: `frontend-design` (Anthropic's official skill, Apache 2.0),
  `ui-ux-pro-max` (`nextlevelbuilder/ui-ux-pro-max-skill`, MIT, reference
  docs only — the upstream searchable CSV database and its `search.py`
  CLI weren't copied), `web-design-guidelines` (`vercel-labs/agent-skills`
  + `vercel-labs/web-interface-guidelines`, both MIT — frozen to read a
  local guidelines copy instead of live-fetching one on every run).

Being frozen means these don't auto-update with upstream — if you want
a newer version of one, re-fetch and re-copy it deliberately.

## Repo structure (why this is a marketplace, not just a folder)

```
agent-library/
├── .claude-plugin/
│   └── marketplace.json        ← the marketplace catalog
├── plugins/
│   └── product-agents/
│       ├── .claude-plugin/
│       │   └── plugin.json     ← the plugin manifest
│       ├── agents/
│       │   ├── research.md
│       │   ├── marketing.md
│       │   ├── evaluation.md
│       │   └── design.md
│       └── skills/             ← frozen third-party reference skills (see above)
└── README.md
```

`marketplace.json` is what makes `claude plugin marketplace add
ronbrightman/agent-library` work at all — it's the catalog Claude Code
reads to know what plugins this repo offers. `plugin.json` plus the
`agents/` and `skills/` directories is what makes the actual
`product-agents` plugin installable and self-contained.

## Updating

Edit the agent `.md` files under `plugins/product-agents/agents/` (or
the skill files under `plugins/product-agents/skills/`), commit, and
push. Anywhere this marketplace is installed with auto-update on (the
default here) will pick up the change automatically on next launch — no
manual re-add or re-install needed. To force it immediately: `claude
plugin marketplace update agent-library`.
