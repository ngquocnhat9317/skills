#!/usr/bin/env python3
"""Compute diff coverage for changed lines from coverage.xml or lcov.info.

Usage examples:
  python3 scripts/diff_coverage.py --base main --head HEAD --coverage-file coverage.xml
  python3 scripts/diff_coverage.py --base main --head HEAD --coverage-file lcov.info
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

SOURCE_BUCKETS = ["backend", "article_model", "frontend/main", "frontend/admin"]


@dataclass
class LineStat:
    hits: Optional[int]  # None = not coverable, int >= 0 = coverable


def run_cmd(cmd: List[str]) -> str:
    try:
        out = subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as exc:
        print(exc.output, file=sys.stderr)
        raise
    return out


def normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def detect_bucket(path: str) -> Optional[str]:
    p = normalize(path)
    for bucket in SOURCE_BUCKETS:
        if p == bucket or p.startswith(bucket + "/"):
            return bucket
    return None


def parse_changed_lines(base: str, head: str) -> Dict[str, Set[int]]:
    diff = run_cmd(["git", "diff", "--unified=0", f"{base}...{head}", "--"]) 

    changes: Dict[str, Set[int]] = {}
    current_file: Optional[str] = None

    # Example: @@ -10,2 +20,3 @@
    hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = normalize(line[6:])
            changes.setdefault(current_file, set())
            continue

        if current_file is None:
            continue

        m = hunk_re.match(line)
        if not m:
            continue

        start = int(m.group(1))
        count = int(m.group(2) or "1")
        if count <= 0:
            continue

        for ln in range(start, start + count):
            changes[current_file].add(ln)

    return {k: v for k, v in changes.items() if v}


def parse_coverage_xml(path: Path) -> Dict[str, Dict[int, LineStat]]:
    tree = ET.parse(path)
    root = tree.getroot()

    data: Dict[str, Dict[int, LineStat]] = {}

    for class_el in root.findall(".//class"):
        filename = class_el.get("filename")
        if not filename:
            continue
        filename = normalize(filename)

        line_map = data.setdefault(filename, {})
        for line_el in class_el.findall("./lines/line"):
            num = line_el.get("number")
            hits = line_el.get("hits")
            if not num or hits is None:
                continue
            try:
                ln = int(num)
                hv = int(hits)
            except ValueError:
                continue
            line_map[ln] = LineStat(hits=hv)

    return data


def parse_lcov_info(path: Path) -> Dict[str, Dict[int, LineStat]]:
    data: Dict[str, Dict[int, LineStat]] = {}
    current_file: Optional[str] = None

    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line.startswith("SF:"):
            sf = normalize(line[3:])
            current_file = sf
            data.setdefault(current_file, {})
            continue

        if line == "end_of_record":
            current_file = None
            continue

        if current_file is None:
            continue

        if line.startswith("DA:"):
            payload = line[3:]
            parts = payload.split(",")
            if len(parts) < 2:
                continue
            try:
                ln = int(parts[0])
                hits = int(parts[1])
            except ValueError:
                continue
            data[current_file][ln] = LineStat(hits=hits)

    return data


def load_coverage(path: Path) -> Dict[str, Dict[int, LineStat]]:
    lower = path.name.lower()
    if lower.endswith(".xml"):
        return parse_coverage_xml(path)
    if lower.endswith(".info"):
        return parse_lcov_info(path)
    raise ValueError("Unsupported coverage file. Use .xml or .info")


def resolve_coverage_path(changed_file: str, coverage_files: Iterable[str]) -> Optional[str]:
    c = normalize(changed_file)

    # Exact match first
    for cf in coverage_files:
        if normalize(cf) == c:
            return cf

    # Suffix match as fallback
    for cf in coverage_files:
        ncf = normalize(cf)
        if ncf.endswith("/" + c) or c.endswith("/" + ncf):
            return cf

    return None


def is_executable_line(src_file: Path, line_no: int) -> bool:
    """Heuristic: ignore blank/comment/docstring/decorator-only lines.

    Final coverability is still decided by coverage artifact presence.
    """
    try:
        lines = src_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return True

    if line_no < 1 or line_no > len(lines):
        return True

    s = lines[line_no - 1].strip()
    if not s:
        return False
    if s.startswith("#") or s.startswith("//"):
        return False
    if s in {"(", ")", "[", "]", "{", "}", ",", ":"}:
        return False
    return True


def compute(base: str, head: str, coverage_file: Path, repo_root: Path) -> Dict[str, object]:
    changed = parse_changed_lines(base, head)
    coverage = load_coverage(coverage_file)

    coverage_files = list(coverage.keys())

    bucket_data: Dict[str, Dict[str, object]] = {
        b: {
            "source": b,
            "changed_files": set(),
            "coverable_changed_lines": 0,
            "covered_changed_lines": 0,
            "diff_coverage_percent": None,
        }
        for b in SOURCE_BUCKETS
    }

    for changed_file, lines in changed.items():
        bucket = detect_bucket(changed_file)
        if not bucket:
            continue

        bucket_data[bucket]["changed_files"].add(changed_file)
        cov_path = resolve_coverage_path(changed_file, coverage_files)
        if cov_path is None:
            continue

        line_stats = coverage[cov_path]

        for ln in sorted(lines):
            src_path = repo_root / changed_file
            if not is_executable_line(src_path, ln):
                continue

            st = line_stats.get(ln)
            if st is None or st.hits is None:
                continue

            bucket_data[bucket]["coverable_changed_lines"] += 1
            if st.hits > 0:
                bucket_data[bucket]["covered_changed_lines"] += 1

    results = []
    for b in SOURCE_BUCKETS:
        item = bucket_data[b]
        cov = item["coverable_changed_lines"]
        hit = item["covered_changed_lines"]

        if cov == 0:
            pct = None
        else:
            pct = round((hit / cov) * 100, 2)

        results.append(
            {
                "source": b,
                "changed_files": sorted(item["changed_files"]),
                "coverable_changed_lines": cov,
                "covered_changed_lines": hit,
                "diff_coverage_percent": pct,
                "status": "N/A" if pct is None else ("PASS" if pct >= 60 else "FAIL"),
            }
        )

    return {
        "base": base,
        "head": head,
        "coverage_file": str(coverage_file),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute diff coverage from .xml or .info")
    parser.add_argument("--base", default="main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--coverage-file", required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    coverage_file = Path(args.coverage_file).resolve()

    if not coverage_file.exists():
        print(f"Coverage file not found: {coverage_file}", file=sys.stderr)
        return 2

    try:
        out = compute(args.base, args.head, coverage_file, repo_root)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
