---
name: diff-ut-coverage-reporter
description: Generate and update unit tests from branch diff against main, run style/type/lint checks in changed scope, compute diff line coverage for backend/article_model/frontend(main/admin), and produce an English coverage report. Also support UT-only mode (no functional code diff) where tests are added from user requirement text (Japanese/English/Vietnamese), quality checks are run, and referenced files must reach above 90 percent file coverage.
---

# Diff UT Coverage Reporter

## Overview
Use this skill to implement a strict UT workflow from git diff to final report.
Support two modes:
1. Diff mode: normal flow with diff coverage gate.
2. UT-only mode: add UT from requirement even when there is no functional code change.

## Mode Selection
Choose mode before execution.

### Diff mode
Use when there are functional code changes in `main...HEAD`.
Run full workflow including diff coverage step.

### UT-only mode
Use when user wants to add UT only and branch has no functional code change.
User provides a requirement in Japanese/English/Vietnamese.
Focus on Step 2 + Step 3 + Step 5 (without diff coverage).
Add Step 4B (file coverage > 90% for requirement-mentioned files).

## Workflow (Diff mode)
1. Detect changed files versus `main`.
2. Write or update UT by source area.
3. Run required quality checks per source.
4. Compute diff line coverage per source.
5. If coverage is below threshold, add tests and repeat.
6. Produce final English report.

## Workflow (UT-only mode)
1. Parse requirement and identify target source and target files.
2. Write/update UT strictly based on requirement.
3. Run required quality checks per source.
4. Compute per-file coverage for requirement-mentioned files and enforce >90%.
5. Produce final English report (skip diff coverage section).

## Step 1: Detect Changed Files (Diff mode)
1. Ensure local `main` exists and diff is computed against it.
2. Collect changed files:
```bash
git diff --name-only main...HEAD
```
3. Classify each changed file into one source bucket:
- `backend`
- `article_model`
- `frontend/main`
- `frontend/admin`
4. Only work on buckets that actually have changed files.

## Step 2: Write/Update UT
For each active bucket, add or update tests only where needed.

### UT requirement handling (UT-only mode)
1. Read user requirement text (JP/EN/VI).
2. Extract explicit behaviors, edge cases, and expected outcomes.
3. Map requirement points to concrete test cases.
4. Keep implementation tightly aligned with requirement; do not add unrelated scenarios.
5. If requirement mentions specific files/modules, prioritize UT for those files.

### Mandatory UT rules
1. Match existing UT style in that source:
- same mocking style
- same assertion style
- same test file location pattern
2. Follow `バックエンドテスト標準` in `.github/copilot-instructions.md`.
3. Keep tests clean and readable.
4. Avoid comments unless needed; if needed, write comments in Japanese.

### Placement rules
- Changed file in `backend` => write/update backend tests only.
- Changed file in `article_model` => write/update article_model tests only.
- Changed file in `frontend/main` => write/update frontend/main tests only.
- Changed file in `frontend/admin` => write/update frontend/admin tests only.
- UT-only mode: place tests by requirement target source/files.

## Step 3: Run Checks (Changed/Target Scope)
Run checks only for sources in scope (diff-changed sources or requirement-targeted sources), including related test files.

### backend / article_model
Run:
```bash
make format
make ruff-check
make mypy
```

### frontend/main / frontend/admin
Run:
```bash
pnpm tsc
pnpm lint
pnpm format
```

If a command supports file-scoped execution in this repository, prefer scoped execution for changed/target files.

## Step 4A: Compute Diff Coverage (Diff mode)
Compute coverage only on changed executable lines.
Do not count structural/non-executable lines (example: multiline class signature lines that do not execute).

### Coverage inputs
- backend/article_model: use `coverage.xml` (can ask user to run long tests and provide regenerated file).
- frontend: run tests and use `lcov.info`.

### Unified script (required)
Use the bundled script to keep coverage logic consistent for both formats:
- `scripts/diff_coverage.py`

Run for backend/article_model (`coverage.xml`):
```bash
python3 scripts/diff_coverage.py --base main --head HEAD --coverage-file coverage.xml
```

Run for frontend (`lcov.info`):
```bash
python3 scripts/diff_coverage.py --base main --head HEAD --coverage-file lcov.info
```

### Script logic
1. Read changed lines from `git diff --unified=0 main...HEAD`.
2. Parse coverage from `.xml` or `.info`.
3. Match changed files and changed lines to coverage entries.
4. Count only changed executable lines that are coverable.
5. Return per-source metrics:
- `coverable_changed_lines`
- `covered_changed_lines`
- `diff_coverage_percent`
- `status` (`PASS`/`FAIL`/`N/A`)

### Pass/Fail gate
- If diff coverage `< 60%`: return to Step 2 and add/update tests.
- If diff coverage `>= 60%`: pass this step.

## Step 4B: File Coverage Gate (UT-only mode)
Enforce file-level coverage for files referenced by requirement.

1. Build target file list from requirement-mentioned files/modules.
2. Read file coverage from test coverage artifact (`coverage.xml` or `lcov.info`).
3. For each target file, compute line coverage percent on coverable lines.
4. Gate:
- if every target file `> 90%`: pass.
- if any target file `< 90%`: return to Step 2 and add/update UT for that file.

Repeat Step 2 -> Step 3 -> Step 4B until all target files pass.

## Step 5: Reporting Format (English)
Produce report per active source bucket with this exact structure:

```text
Source: backend / article_model / frontend/main / frontend/admin
Diff coverage: <value or SKIPPED in UT-only mode>
Added testcases:
- <test_file_1>:
  - <ClassTest::test_method> (frontend can use test name only; keep Japanese names unchanged)
  - ...
Updated testcases:
- <test_file_2>:
  - <ClassTest::test_method>
  - ...
Coverage summary:
- ...
- ...
```

### UT-only mode report rule
- Set `Diff coverage: SKIPPED (UT-only mode)`.
- Coverage summary must report per-file coverage for requirement-mentioned files and confirm all are `> 90%`.

### Reporting requirements
1. Use English for report text.
2. Keep frontend test names as-is if they are Japanese.
3. Distinguish clearly between added and updated testcases.
4. Coverage summary must explain what behaviors/branches are now covered.

## Execution Notes
- Stay within file-change scope in Diff mode; in UT-only mode stay within requirement scope.
- Preserve existing project conventions over personal preference.
- Re-run checks after each significant UT update.
- When backend/article_model test runtime is heavy, ask user to run full tests and provide fresh `coverage.xml`, then continue coverage computation.
