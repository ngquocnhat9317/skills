# Query Perf Issue Catalog (SQL + NoSQL)

Use this file only when needed (e.g., when ranking issues, proposing fixes, or choosing the safest non-breaking optimization).

## Severity guidelines

- **High**: Causes outages/timeouts, DB CPU spikes, lock contention, unbounded scans, or fan-out that can take down the system.
- **Medium**: Clearly inefficient; noticeable latency/cost; impacts important paths but not catastrophic.
- **Low**: Inefficiency with moderate impact; safe to fix; improves cost/latency.
- **Very Low**: Micro-optimizations; marginal gain; optional.

## Common issues and safe fixes (non-breaking)

### SQL

1) **N+1 queries**
- Symptoms: Loop fetches related entities one-by-one; many small queries per request.
- Safe fixes: Batch fetch with `IN (...)`, join (when safe), dataloader pattern, prefetch associations, add caching for repeated lookups within request scope.

### ORM / Query builders (applies on top of SQL/NoSQL)

1) **ORM-driven N+1 (lazy-loading / per-row fetch)**
- Symptoms: Accessing relations in a loop triggers extra queries (e.g., missing `include/relations/preload/select_related`).
- Safe fixes: Eager load (Prisma `include/select`, TypeORM `relations`/joins, Sequelize `include`, Django `select_related/prefetch_related`, SQLAlchemy `selectinload/joinedload`, Hibernate `JOIN FETCH`/EntityGraph, GORM `Preload`), or batch fetch by IDs.

2) **Over-fetching entities**
- Symptoms: Loading full entity graphs or large columns/JSON fields by default.
- Safe fixes: Add projections (`select/attributes/only/defer`), keep DTO/output unchanged.

3) **Inefficient pagination**
- Symptoms: Offset pagination on large tables, missing index for sort key, unstable ordering.
- Safe fixes: Ensure indexed `ORDER BY`, prefer keyset pagination when possible (only if it does not change externally visible behavior).

2) **Missing/ineffective indexes**
- Symptoms: Filtering/sorting on non-indexed columns; frequent full table scans; slow `ORDER BY`.
- Safe fixes: Add index via migration; prefer composite indexes matching `(WHERE columns, ORDER BY columns)`; avoid indexes that break write performance unless justified.

3) **Over-fetching / SELECT \***
- Symptoms: Selecting large rows/JSON blobs when only a few fields are used.
- Safe fixes: Explicit projection (select only needed columns); keep response DTO unchanged.

4) **Unbounded queries**
- Symptoms: No pagination/limit; loads huge result sets; sorts without limit.
- Safe fixes: Add limit/pagination while preserving existing default behavior (e.g., keep old behavior when caller already passes limit; otherwise apply conservative cap only where safe and confirmed).

5) **Expensive COUNT(*) / DISTINCT**
- Symptoms: Frequent counts on large tables; distinct over big join results.
- Safe fixes: Use approximate counts if already acceptable; maintain counters; query rewrite; add indexes; cache counts with TTL (if semantics allow).

6) **Lock contention / long transactions**
- Symptoms: Large update/delete in single transaction; mixed reads/writes; missing WHERE key.
- Safe fixes: Chunked updates; narrower WHERE; reduce transaction scope; add indexes; use `SKIP LOCKED` patterns (only if semantics match).

### MongoDB / Document stores

1) **No index on filter / sort**
- Symptoms: Collection scan; slow sort.
- Safe fixes: Add index (migration/init script); ensure query uses index (match shape); avoid regex unanchored.

2) **Large documents fetched repeatedly**
- Symptoms: Fetching entire documents where only few fields needed.
- Safe fixes: Projection; store derived fields; avoid pulling big arrays if not used.

3) **Inefficient aggregation**
- Symptoms: `$lookup` heavy; `$unwind` explosion; pipeline not selective early.
- Safe fixes: Move `$match` earlier; add indexes; reduce `$lookup` cardinality; precompute when needed.

### DynamoDB / Key-value stores

1) **Scan instead of Query**
- Symptoms: `Scan` on large table; high RCUs.
- Safe fixes: Add/Use GSI; redesign access pattern; paginate scan with limits; cache results.

2) **Hot partition**
- Symptoms: Throttling; uneven key distribution.
- Safe fixes: Key sharding; add randomness; redesign partition key; batch reads.

## Testing guidance (UT-first)

- Prefer running the smallest unit test set covering changed repository/service.
- Add/adjust UT only when needed to lock in behavior (especially if refactoring query builder code).
- If changes add migrations/index definitions, validate they are included in the existing migration runner workflow.
