---
name: scan-query-perf
description: Scan and fix query-performance issues across a codebase that uses SQL and/or NoSQL (e.g., slow queries, N+1 patterns, missing indexes, over-fetching, unbounded scans, poor pagination, excessive query fan-out). Use when asked to (1) scan query hotspots and produce a prioritized issue list, (2) fix all issues or a subset by IDs or severity, or (3) scan+fix with user confirmation while keeping the input/output behavior of queries/functions unchanged.
---

# Scan Query Perf

## Goals (Scope)

- Scan everything involved in querying (SQL/NoSQL): callsites, query builders, repository/DAO/service layer, jobs/workers, batch processes, and any loops that trigger queries.
- Includes ORM/query builder stacks (Prisma/TypeORM/Sequelize/Knex, SQLAlchemy/Django ORM, Mongoose, Hibernate/JPA, GORM/Ent, …). Treat “ORM call + filter/join/eager-load” as a query to optimize just like raw SQL.
- Produce a prioritized issue list with stable IDs, root-cause analysis, a non-breaking fix recommendation, and expected impact.
- Fix issues (all / by IDs / by severity filter) and run Unit Tests (UT) whenever possible to keep behavior intact.

## Command Interface (Chat Commands)

When the user sends a message starting with `/scan-query-perf ...`, treat it as a command for this skill workflow (not a shell command).

Supported commands (exactly as typed by the user):

```
/scan-query-perf scan
/scan-query-perf scan and fix
/scan-query-perf fix
/scan-query-perf fix high|medium|low|very-low
/scan-query-perf fix QPD-XXXX,QPD-YYYY
```

Parsing rules:
- If `fix` contains `QPD-` => treat as a comma-separated list of IDs.
- If `fix` is a severity => fix **that severity and above** (e.g., `fix medium` = Medium + High).
- If `fix` has no argument => fix all issues (subject to the "Scan + Fix" default constraint below).
- For `scan and fix`: scan first, print issues, then **ask for confirmation**. If the user agrees, default to “fix all” but **only Low and above** (Low/Medium/High).

## Supported Jobs

### 1) Scan issues

Scan only. Do not change code.

### 2) Fix issues

Only run after a scan result exists (in the same thread). Supports:
- Fix `all` (default)
- Fix by `IDs`
- Fix by `severity` filter (High/Medium/Low/Very Low)

### 3) Scan + Fix

Run scan first, print issues, then **ask for user confirmation** before fixing.
- Default fix scope: `all`
- Default severity cutoff: only `Low` and above (Low/Medium/High). Skip `Very Low` unless the user explicitly requests it.

## Non-Negotiable Constraint (No Behavior Changes)

- Proposed solutions and code changes **must not change input/output** (API contract) of the query/function/logic.
- Do not change the query’s overall output (result shape + meaning). Before proposing a fix:
  - Review the baseline output (what fields/rows are returned, ordering, grouping/aggregation, null/empty behavior)
  - Understand the business purpose and identify the primary purpose of the query
  - Treat “preserve the primary purpose” and output invariants as an explicit optimization goal
- Minimize database-structure changes (schema/migrations/indexes/columns). Prefer fixes strictly within the query text and application logic whenever possible.
- If a behavior change is truly unavoidable (e.g., enforcing pagination):
  - Prefer the least-breaking approach (preserve existing defaults)
  - Make the change explicit and get user confirmation before applying
- If preserving the overall output is impossible without changing the business meaning, strongly de-prioritize that issue (lower severity/priority) and treat it as “needs-review” unless the user explicitly authorizes the change.
- If a DB-structure change is the only safe option (e.g., an index is required to avoid timeouts), treat it as a **last resort** and ask for confirmation before adding migrations/indexes/columns.
- Fixes should follow scan recommendations. If the scan is missing/misclassified, update scan findings first, then fix.

## Execution Workflow

### A) Quick Prep (Repo Discovery)

- Identify the stack: language, ORM/driver, DB (Postgres/MySQL, MongoDB, DynamoDB, Elastic, Redis, …), query ownership layers (repo/DAO/service), and how UT is run.
- Use `rg` to find entrypoints: `SELECT `, `.find(`, `.aggregate(`, `execute(`, `query(`, `scan(`, `batchGet`, etc.
- If using an ORM/query builder: search for ORM-specific patterns (e.g., Prisma `include/select`, TypeORM `relations/join`, Django `select_related/prefetch_related`, SQLAlchemy `joinedload/selectinload`, Mongoose `populate`, Hibernate `JOIN FETCH`, …). Reference `./references/orm-patterns.md`.
- (Optional) run the bundled heuristic scan helper (from this skill folder): `python3 ./scripts/scan_query_perf.py --cwd <REPO_ROOT> --json`.

### B) Scan Issues (Output Must Follow the Format)

Scan must return a list of issues. Each issue includes:
- `id`: `QPD-...` (stable within the thread; if using the script, keep the script ID)
- `severity`: High | Medium | Low | Very Low
- `location`: file + function/method + (if possible) approximate line/logic block
- `analysis`: why it is slow/expensive (hypothesized root cause + evidence from code)
- `solution`: a non-breaking fix recommendation (lowest-risk first)
- `output_invariants`: what must stay the same about the query output (shape + meaning)
- `estimated_gain`: expected improvement + assumptions (e.g., “reduce N queries to 1”)
- `impact`: files to touch + risk + how to test/verify

Reference when needed: `./references/issue-catalog.md`.

### C) Fix Issues (Only After Scan)

Before changing code:
- Confirm fix scope: `all` / `IDs` / `severity` filter.
- Enforce “no input/output change” and “minimal DB-structure change”. Prefer query/logic-only optimizations: projection/select fields, batching, request-scope caching, bounded scans, preserve pagination defaults, eliminate N+1, remove queries from loops, reuse prepared statements, add sane timeouts.
- Explicitly document output invariants and the primary purpose for each touched query, and ensure the fix preserves both.
- Only propose/add indexes/migrations/columns after the query/logic-only path is exhausted and the user confirms.

After changing code:
- Run the most relevant UT first; then run the full UT suite if reasonable.
- If UT fails: iterate until passing, or revert the failing portion and report clearly.

### D) Scan + Fix (Must Ask For Confirmation)

Required flow:
1) Scan and print the issue list.
2) Ask: “Do you want me to fix now? Fix all or by IDs/severity?”
3) If user agrees: only fix `Low` and above unless `Very Low` is explicitly requested.

## Unit Tests (UT) Execution

### UT steps (try to run for real)

Do these steps to reduce the chance that UT cannot be executed:

1) Detect the test runner and package manager:
- Node.js: `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`
- Python: `pyproject.toml`, `poetry.lock`, `requirements.txt`, `uv.lock`
- Go: `go.mod`
- Java/Kotlin: `pom.xml`, `build.gradle`, `settings.gradle`
- Ruby: `Gemfile`, `Gemfile.lock`
- PHP: `composer.json`, `composer.lock`
- .NET: `*.sln`, `*.csproj`

2) Install dependencies using the lockfile-driven command (prefer deterministic installs):
- Node: `npm ci` | `pnpm install --frozen-lockfile` | `yarn install --frozen-lockfile`
- Python: `uv sync` | `poetry install` | `pip install -r requirements.txt`
- Go: `go mod download`
- Java/Kotlin: `mvn -q test -DskipTests` (download deps) or `./gradlew testClasses`
- Ruby: `bundle install`
- PHP: `composer install`
- .NET: `dotnet restore`

3) Run the smallest relevant UT set first (then expand):
- Node: `npm test -- <pattern>` / `pnpm test -- <pattern>` / `yarn test <pattern>`
- Python: `pytest -k <pattern>` / `python -m unittest <module>`
- Go: `go test ./... -run <TestName>`
- Java/Kotlin: `mvn test -Dtest=<TestClass>` / `./gradlew test --tests <pattern>`
- Ruby: `bundle exec rspec <spec>`
- PHP: `vendor/bin/phpunit --filter <pattern>`
- .NET: `dotnet test --filter <pattern>`

4) If UT still cannot run, collect the minimal diagnostics in the output:
- The exact command you attempted
- The first error line + stack summary
- Detected toolchain files (`.nvmrc`, `.tool-versions`, lockfiles) and expected runtime versions if present

### If UT cannot be executed here (Assumed UT)

If environment constraints prevent running UT, do **not** claim “tests passed”. Instead, provide an “Assumed UT / Safety Check” that compares before vs after for the touched query/function/logic:

- Contract lock: exported function signatures, DTO/response shape, and error behavior remain unchanged.
- Query semantics lock: same filters, ordering, joins/includes, pagination defaults, and null/empty behaviors.
- Data access lock: only add safe optimizations (projection, batching, eager-load, indexes); avoid changing meaning.
- Migration/index lock: only additive (new indexes), no destructive schema changes unless confirmed.
- Provide concrete “user-run” commands to verify in their environment (install deps + UT command).

## Logging & Issue State (Required)

Always persist scan and fix activity into a log file so the skill can:
- Avoid re-reporting already-fixed issues as “new”
- Track which issues are open vs fixed vs blocked
- Provide an audit trail (commands run, tests run, touched files)

### Default log location

Store logs alongside this skill (not inside the target repo), namespaced per repo root:
- Directory: `<SKILL_ROOT>/logs/<repo_key>/`
- Log file: `<SKILL_ROOT>/logs/<repo_key>/qpd-log.jsonl`

`repo_key` is a stable hash of `<REPO_ROOT>` to avoid collisions between different repos.

### Log format (JSONL events)

Append one JSON object per line. Supported event types:
- `scan`: includes a minimal list of scanned issues `{id,severity,location}`
- `fix`: includes results per issue `{id,status,note}` where `status` is one of `fixed|blocked|skipped|needs-review|open`

### How to write and read the log

Use the bundled helper script:
Run these commands from this skill directory (where this `SKILL.md` lives), or use an absolute path to `scripts/qpd_log.py`.

1) Initialize log:
- `python3 scripts/qpd_log.py init --repo <REPO_ROOT>`

2) After scan (recommended: also save a human-readable report file):
- Save report: `<SKILL_ROOT>/logs/<repo_key>/scan-<timestamp>.md`
- Append status: `python3 scripts/qpd_log.py append-scan --repo <REPO_ROOT> --issues-json <issues.json> --command "<scan command(s)>"`

3) After fix:
- Append results: `python3 scripts/qpd_log.py append-fix --repo <REPO_ROOT> --result QPD-XXXX:fixed --result QPD-YYYY:blocked:needs-migration --tests "<exact UT commands + outcome>" --touched-file path/to/file.ts`

4) Before reporting “what’s left”, compute current state from log:
- `python3 scripts/qpd_log.py status --repo <REPO_ROOT>`

### Status rules (skill behavior)

- On every `scan`, mark listed IDs as `open`. If an ID was previously `fixed` and appears again, treat it as a regression and mark it `open` with note `regressed`.
- On `fix`, update only the listed IDs to the provided `status`.
- Never claim an issue is fixed unless a `fix` event marks it `fixed`.

## Output Format

### Scan output (readable + actionable)

Make scan output easy to skim. Use this structure:

1) **Summary**
- Findings count by severity
- Top hotspots (modules/services/jobs)
- Top 3 “quick wins” (Low/Medium, low risk)

2) **Issue table** (markdown table)
- Columns: `ID | Severity | Area | Location | Root cause | Effort | Confidence`

3) **Issue details** (one block per issue, consistent fields)
- `Location`
- `Problem`
- `Evidence` (what in code indicates the issue; small snippet only if critical)
- `Non-breaking fix`
- `Why safe` (explicitly state what contract/behavior is preserved)
- `Estimated gain` (with assumptions)
- `Test plan` (UT commands; include targeted + full suite)

Example issue detail block:

```
ID: QPD-0007
Severity: Medium
Location: path/to/file.ts :: functionName (line ~123)
Problem: ...
Evidence: ...
Non-breaking fix: ...
Why safe: ...
Estimated gain: ~30–60% (assumption: ...)
Test plan: ...
```

### Fix output (not “too brief”)

When reporting fixes, include:
- `What changed` (files + high-level change list)
- `Why it helps` (tie back to root cause)
- `Why it’s non-breaking` (explicit contract lock)
- `Risk / rollback` (how to revert safely)
- `Tests` with one of:
  - `Tests: passed` + exact commands you ran, or
  - `Tests: not run` + reason + exact commands for the user to run, plus “Assumed UT / Safety Check”

## Notes

- If the system has DB migrations/index definitions (SQL migrations, Mongo index creation scripts, Terraform/CloudFormation, etc.), prefer proposing/fixing in the canonical place rather than runtime shortcuts.
- If UT cannot be executed in the current environment, state it clearly and provide exact commands for the user to verify.
