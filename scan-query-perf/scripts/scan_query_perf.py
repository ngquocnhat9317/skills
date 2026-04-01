#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class Finding:
    id: str
    kind: str
    pattern: str
    file: str
    line: int
    excerpt: str


def _stable_id(file: str, line: int, kind: str, pattern: str, excerpt: str) -> str:
    raw = f"{file}:{line}:{kind}:{pattern}:{excerpt}".encode("utf-8", errors="replace")
    digest = hashlib.sha1(raw).hexdigest()[:8].upper()
    return f"QPD-{digest}"


def _run_rg(pattern: str, globs: List[str], cwd: str) -> List[Finding]:
    if shutil.which("rg") is None:
        return []

    cmd = ["rg", "-n", "--hidden", "--no-heading", "--color", "never", pattern]
    for g in globs:
        cmd.extend(["-g", g])

    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or f"rg failed for pattern: {pattern}")

    findings: List[Finding] = []
    for line in proc.stdout.splitlines():
        # Format: path:line:content (rg can include ':' in path on Windows; ok for our environment)
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        path, line_no_s, content = parts
        try:
            line_no = int(line_no_s)
        except ValueError:
            continue
        excerpt = content.strip()
        fid = _stable_id(path, line_no, "candidate", pattern, excerpt)
        findings.append(
            Finding(
                id=fid,
                kind="candidate",
                pattern=pattern,
                file=path,
                line=line_no,
                excerpt=excerpt[:240],
            )
        )
    return findings


def _dedupe(findings: Iterable[Finding]) -> List[Finding]:
    seen = set()
    out: List[Finding] = []
    for f in findings:
        key = (f.id, f.file, f.line, f.pattern)
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Heuristic scan for SQL/NoSQL query callsites and obvious hotspots."
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Repo root (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON to stdout (default: pretty text).",
    )
    parser.add_argument(
        "--out",
        help="Also write the output to this file path (directories are created).",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=800,
        help="Max findings to output (default: 800).",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Scan all files (default: scan common code/query file types only).",
    )
    args = parser.parse_args(argv)

    cwd = os.path.abspath(args.cwd)

    exclude_globs = [
        "!**/node_modules/**",
        "!**/dist/**",
        "!**/build/**",
        "!**/.git/**",
        "!**/.next/**",
        "!**/coverage/**",
        "!**/vendor/**",
    ]

    include_globs = []
    if not args.all_files:
        include_globs = [
            "**/*.ts",
            "**/*.tsx",
            "**/*.js",
            "**/*.jsx",
            "**/*.mjs",
            "**/*.cjs",
            "**/*.py",
            "**/*.go",
            "**/*.java",
            "**/*.kt",
            "**/*.rb",
            "**/*.php",
            "**/*.cs",
            "**/*.sql",
            "**/*.prisma",
            "**/*.graphql",
            "**/*.gql",
            "**/*.yml",
            "**/*.yaml",
            "**/*.json",
        ]

    patterns = [
        # SQL-ish (try to avoid HTTP method false positives like 'DELETE')
        # Heuristic: require quotes/backticks to reduce matches like "import { Select } from ..."
        r"(?i)(\"|'|`)\s*select\s+.+\s+from\s+\w+",
        r"(?i)(\"|'|`)\s*update\s+\w+\s+set\s+",
        r"(?i)(\"|'|`)\s*insert\s+into\s+\w+",
        r"(?i)(\"|'|`)\s*delete\s+from\s+\w+",
        r"(?i)(\"|'|`)\s*explain\s+",
        r"(?i)(\"|'|`)\s*where\s+.*\bin\s*\(",
        # Generic "execute/query" callsites
        r"\.execute\(|\.query\(|\.raw\(",
        # ORMs / query builders (common)
        r"\bprisma\.\w+\.findMany\(|\bprisma\.\w+\.findFirst\(",
        r"\bprisma\.\w+\.findUnique\(",
        r"\bknex\(|\.select\(|\.where\(|\.orderBy\(",
        r"\bsequelize\b|\bTypeORM\b",
        r"\bcreateQueryBuilder\(",
        r"\bModel\.findAll\(|\bModel\.findOne\(",
        # Mongo-ish / Mongoose
        r"\.find\(|\.findOne\(|\.aggregate\(|\.updateOne\(|\.updateMany\(",
        r"\.populate\(",
        # Mongo-ish
        r"\$lookup\b|\$unwind\b|\$match\b",
        # MongoDB drivers/ODMs (multi-language heuristics)
        r"\bMongoClient\b|\bMongoTemplate\b|\bReactiveMongoTemplate\b",
        r"\bMongoRepository\b|\bAsyncIOMotorClient\b",
        r"\bcollection\.find\(|\bcollection\.aggregate\(",
        r"\bcollection\.update_one\(|\bcollection\.update_many\(",
        r"\bDocument\.objects\(|\bMongoEngine\b",
        # Python ORMs
        r"\bsession\.query\(|\bselect\(",
        r"\bjoinedload\(|\bselectinload\(|\bsubqueryload\(",
        r"\.objects\.filter\(|\.objects\.get\(",
        r"\.select_related\(|\.prefetch_related\(",
        # Dynamo-ish
        r"\bBatchGetItem\b|\bQueryCommand\b|\bScanCommand\b|\bscan\(",
        r"\bDynamoDBDocumentClient\b|\bDocumentClient\b",
        r"\b(Get|Put|Update|Delete|Query|Scan|BatchGet|BatchWrite)Command\(",
        r"\bdocClient\.send\(",
        r"\.transactGet\(|\.transactWrite\(",
        r"\bdynamoose\.model\(|\bDynamoose\b",
        r"\bModel\.query\(|\bModel\.scan\(|\bModel\.batchGet\(",
        r"\bPynamoDB\b|\bModel\.batch_get\(|\bModel\.batch_write\(",
        r"\bboto3\.client\(\s*['\"]dynamodb['\"]\s*\)",
        r"\bboto3\.resource\(\s*['\"]dynamodb['\"]\s*\)",
        r"\bDynamoDBMapper\b|\bDynamoDbEnhancedClient\b",
        r"\bElectroDB\b|\bnew\s+Entity\(",
        # Java/Kotlin ORMs
        r"\bcreateQuery\(|\bCriteriaBuilder\b|\bJOIN FETCH\b|\bEntityGraph\b",
        # Go ORMs
        r"\bPreload\(|\bJoins\(|\bLimit\(|\bOffset\(",
        r"\.Query\(\)\b|\bWith[A-Z]\w*\(",
        # Suspicious loop patterns (very heuristic)
        r"for\s*\(.*\)\s*\{.*(\.query\(|\.execute\(|\.find\()",
        r"for\s+.+:\s+.*(\.query\(|\.execute\(|\.find\()",
    ]

    all_findings: List[Finding] = []
    for p in patterns:
        try:
            all_findings.extend(_run_rg(p, globs=(include_globs + exclude_globs), cwd=cwd))
        except RuntimeError as e:
            print(f"[scan_query_perf] Warning: {e}", file=sys.stderr)

    findings = _dedupe(all_findings)[: max(0, args.max)]

    if args.json:
        payload = [asdict(f) for f in findings]
        out_s = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        sys.stdout.write(out_s)
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(out_s)
        return 0

    for f in findings:
        sys.stdout.write(f"{f.id}  {f.file}:{f.line}  pattern={f.pattern}  {f.excerpt}\n")
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            for fnd in findings:
                f.write(f"{fnd.id}  {fnd.file}:{fnd.line}  pattern={fnd.pattern}  {fnd.excerpt}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
