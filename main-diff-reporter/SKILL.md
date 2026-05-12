---
name: main-diff-reporter
description: Summarize branch changes compared with `main` into a concise bilingual Japanese/English developer report focused on core business-impacting changes. Use when users ask for "main diff summary", "branch report", "PR change summary", or bilingual JA/EN change notes while ignoring minor refactors and low-impact tweaks.
---

# Main Diff Reporter

## Workflow

1. Identify target branch and ensure `main` is available locally.
2. Collect changed files and code diffs against `main`.
3. Group related changes into 2-8 major topics based on business behavior.
4. Remove low-impact changes:
- Formatting-only edits
- Rename-only edits with no behavior change
- Tiny internal cleanup that does not affect business flow
5. Produce a concise developer report in bilingual Japanese/English.

## Diff Collection

Use these commands as the default path:

```bash
git fetch origin main
git diff --name-status main...HEAD
git diff --stat main...HEAD
git diff main...HEAD
```

If user wants committed-only scope, use:

```bash
git diff main...HEAD -- .
```

## What To Keep

Keep only core changes that affect one of these:
- User-visible behavior
- Business rules and validation
- API contract, request/response shape, or side effects
- Data processing logic that changes outcomes
- Security, permission, or critical reliability behavior

## Output Rules

Follow exactly:
- Start with Japanese/English headline bullets only.
- Put file paths, symbols, and code terms in backticks.
- Keep each bullet short and concrete.
- Avoid unnecessary jargon.
- Do not use bold text.

Primary output format:

- <nội dung 1 tiếng nhật> / <nội dung 1 tiếng anh>
- <nội dung 2 tiếng nhật> / <nội dung 2 tiếng anh>
- ...

Optional detail format (only when user asks for breakdown):

- <major topic> <purpose if needed>
  - <supporting sub-change>
  - <supporting sub-change>

## Writing Style

- Target audience: developers.
- Prefer action-oriented phrasing.
- Avoid speculation; infer only from actual diff content.
- If a purpose is unclear, omit the purpose phrase.
