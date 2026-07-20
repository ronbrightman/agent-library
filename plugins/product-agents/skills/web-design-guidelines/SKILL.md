---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Read the frozen guidelines in `reference/web-interface-guidelines.md`
   (see the note below on why this is a local copy, not a live fetch).
2. Read the specified files (or prompt the user for files/pattern).
3. Check against all rules in the guidelines doc.
4. Output findings in the terse `file:line` format.

## Guidelines source (frozen, not live)

The upstream version of this skill fetches fresh guidelines on every run
from `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`.
This copy was deliberately frozen instead — read
`reference/web-interface-guidelines.md` in this same skill folder rather
than fetching it live. If the upstream guidelines have moved on
meaningfully since 2026-07-20 and it matters for a specific review, say
so rather than silently re-fetching.

## Usage

When a user provides a file or pattern argument:
1. Read `reference/web-interface-guidelines.md` in this skill folder.
2. Read the specified files.
3. Apply all rules from the guidelines doc.
4. Output findings using the format specified in that doc.

If no files specified, ask the user which files to review.
