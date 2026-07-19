# agent-library

Portable [Claude Code](https://claude.com/claude-code) agents for
consumer (B2C) product work — `research`, `evaluation`, and `design`.
Distributed as a proper Claude Code plugin marketplace, so getting them
into any environment (a different computer, a fresh cloud/mobile
session, anywhere) is two commands instead of copying files by hand.

## Get the agents in a new environment

Run these two commands once, in any Claude Code session:

```
claude plugin marketplace add ronbrightman/agent-library
claude plugin install product-agents@agent-library
```

That's it. The three agents (`research`, `evaluation`, `design`) are now
available in that environment, and stay up to date automatically —
auto-update is enabled on this marketplace, so future improvements
pushed here propagate without re-running anything.

(If you're in an interactive session rather than scripting it, the same
two things also work as slash commands: `/plugin marketplace add
ronbrightman/agent-library` then `/plugin install
product-agents@agent-library`.)

## What's in the plugin

- **`research`** — generates and researches feature/marketing ideas,
  grounded in real current B2C growth loops, retention/activation
  metrics, and monetization models. Read/web-search access only, no
  code-editing tools — it starts every run by researching current real
  examples, since this space moves fast and generic knowledge goes
  stale.
- **`evaluation`** — scores and ranks ideas using the RICE framework
  (Reach × Impact × Confidence ÷ Effort), extended with explicit build
  cost, run cost, and founder-time dimensions. Read/web-search access
  only.
- **`design`** — turns an approved idea into a product spec plus 1-2
  visual/UX design directions, grounded in current real consumer-app
  UI/UX patterns rather than assumed taste. Read/web-search access only
  — it proposes, it doesn't build.

These three are meant to be paired with two project-specific agents,
`build` and `review`, that live in whatever repo you're actually working
in (not here) since they need to know that codebase's own structure and
conventions. See a target repo's own `AGENT_POLICY.md` for how the full
five-agent pipeline fits together end to end.

## Repo structure (why this is a marketplace, not just a folder)

```
agent-library/
├── .claude-plugin/
│   └── marketplace.json        ← the marketplace catalog
├── plugins/
│   └── product-agents/
│       ├── .claude-plugin/
│       │   └── plugin.json     ← the plugin manifest
│       └── agents/
│           ├── research.md
│           ├── evaluation.md
│           └── design.md
└── README.md
```

`marketplace.json` is what makes `claude plugin marketplace add
ronbrightman/agent-library` work at all — it's the catalog Claude Code
reads to know what plugins this repo offers. `plugin.json` plus the
`agents/` directory is what makes the actual `product-agents` plugin
installable and gives Claude Code the three agent definitions.

## Updating

Edit the agent `.md` files under `plugins/product-agents/agents/`,
commit, and push. Anywhere this marketplace is installed with
auto-update on (the default here) will pick up the change automatically
on next launch — no manual re-add or re-install needed. To force it
immediately: `claude plugin marketplace update agent-library`.
