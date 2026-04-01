#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    out: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def _append_jsonl(path: str, obj: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _default_log_dir(repo_root: str) -> str:
    skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    repo_key = hashlib.sha1(repo_root.encode("utf-8", errors="replace")).hexdigest()[:12]
    return os.path.join(skill_root, "logs", repo_key)


def _default_log_path(repo_root: str) -> str:
    return os.path.join(_default_log_dir(repo_root), "qpd-log.jsonl")


def _normalize_repo_root(repo_root: str) -> str:
    return os.path.abspath(repo_root)


@dataclass(frozen=True)
class IssueState:
    id: str
    severity: Optional[str]
    status: str
    last_seen_at: Optional[str]
    last_updated_at: Optional[str]
    location: Optional[str]
    note: Optional[str]


def _is_issue_status(value: str) -> bool:
    return value in {"open", "fixed", "skipped", "blocked", "needs-review"}


def _compute_state(events: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, IssueState], List[str]]:
    warnings: List[str] = []
    state: Dict[str, IssueState] = {}

    def upsert(
        issue_id: str,
        *,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        last_seen_at: Optional[str] = None,
        last_updated_at: Optional[str] = None,
        location: Optional[str] = None,
        note: Optional[str] = None,
    ) -> None:
        prev = state.get(issue_id)
        state[issue_id] = IssueState(
            id=issue_id,
            severity=severity if severity is not None else (prev.severity if prev else None),
            status=status if status is not None else (prev.status if prev else "open"),
            last_seen_at=last_seen_at if last_seen_at is not None else (prev.last_seen_at if prev else None),
            last_updated_at=last_updated_at if last_updated_at is not None else (prev.last_updated_at if prev else None),
            location=location if location is not None else (prev.location if prev else None),
            note=note if note is not None else (prev.note if prev else None),
        )

    for ev in events:
        ev_type = ev.get("type")
        at = ev.get("at")
        if not isinstance(at, str):
            at = None

        if ev_type == "scan":
            issues = ev.get("issues", [])
            if not isinstance(issues, list):
                continue
            for issue in issues:
                if not isinstance(issue, dict):
                    continue
                issue_id = issue.get("id")
                if not isinstance(issue_id, str) or not issue_id:
                    continue
                severity = issue.get("severity") if isinstance(issue.get("severity"), str) else None
                location = issue.get("location") if isinstance(issue.get("location"), str) else None

                prev = state.get(issue_id)
                if prev and prev.status == "fixed":
                    upsert(
                        issue_id,
                        severity=severity,
                        status="open",
                        last_seen_at=at,
                        last_updated_at=at,
                        location=location,
                        note="regressed (seen again in scan)",
                    )
                else:
                    upsert(
                        issue_id,
                        severity=severity,
                        status="open",
                        last_seen_at=at,
                        last_updated_at=at,
                        location=location,
                        note=None,
                    )
        elif ev_type == "fix":
            results = ev.get("results", [])
            if not isinstance(results, list):
                continue
            for r in results:
                if not isinstance(r, dict):
                    continue
                issue_id = r.get("id")
                status = r.get("status")
                if not isinstance(issue_id, str) or not issue_id:
                    continue
                if not isinstance(status, str) or not _is_issue_status(status):
                    warnings.append(f"Invalid status for {issue_id}: {status!r}")
                    continue
                note = r.get("note") if isinstance(r.get("note"), str) else None
                upsert(issue_id, status=status, last_updated_at=at, note=note)
        elif ev_type == "note":
            # Notes are not issue-scoped unless issue_ids is provided
            issue_ids = ev.get("issue_ids", [])
            if isinstance(issue_ids, list):
                for issue_id in issue_ids:
                    if not isinstance(issue_id, str) or not issue_id:
                        continue
                    note = ev.get("note") if isinstance(ev.get("note"), str) else None
                    if note:
                        upsert(issue_id, last_updated_at=at, note=note)

    return state, warnings


def _print_markdown_status(state: Dict[str, IssueState]) -> None:
    by_status: Dict[str, List[IssueState]] = {}
    for s in state.values():
        by_status.setdefault(s.status, []).append(s)

    def count(st: str) -> int:
        return len(by_status.get(st, []))

    sys.stdout.write("## QPD status (from log)\n\n")
    sys.stdout.write(
        f"- Open: {count('open')}\n- Fixed: {count('fixed')}\n- Blocked: {count('blocked')}\n- Skipped: {count('skipped')}\n- Needs review: {count('needs-review')}\n\n"
    )

    rows = sorted(state.values(), key=lambda s: (s.status, s.severity or "", s.id))
    sys.stdout.write("| ID | Status | Severity | Location | Last seen | Last updated |\n")
    sys.stdout.write("|---|---|---|---|---|---|\n")
    for s in rows:
        loc = (s.location or "").replace("\n", " ")
        sys.stdout.write(
            f"| {s.id} | {s.status} | {s.severity or ''} | {loc} | {s.last_seen_at or ''} | {s.last_updated_at or ''} |\n"
        )


def cmd_init(args: argparse.Namespace) -> int:
    repo_root = _normalize_repo_root(args.repo)
    log_dir = args.log_dir or _default_log_dir(repo_root)
    _ensure_dir(log_dir)
    log_path = os.path.join(log_dir, "qpd-log.jsonl")
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8"):
            pass
    sys.stdout.write(log_path + "\n")
    return 0


def cmd_append_scan(args: argparse.Namespace) -> int:
    repo_root = _normalize_repo_root(args.repo)
    log_path = args.log_path or _default_log_path(repo_root)
    run_id = args.run_id or f"scan-{uuid.uuid4().hex[:10]}"

    issues: List[Dict[str, Any]] = []
    if args.issues_json:
        with open(args.issues_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise SystemExit("--issues-json must be a JSON array")
        for it in data:
            if not isinstance(it, dict):
                continue
            issue_id = it.get("id")
            if not isinstance(issue_id, str) or not issue_id:
                continue
            issues.append(
                {
                    "id": issue_id,
                    "severity": it.get("severity"),
                    "location": it.get("location"),
                }
            )
    else:
        # Allow appending a scan marker even without structured issues
        issues = []

    ev: Dict[str, Any] = {
        "v": 1,
        "type": "scan",
        "at": _utc_now_iso(),
        "repo_root": repo_root,
        "run_id": run_id,
        "issues": issues,
        "meta": {
            "command": args.command,
            "notes": args.notes,
        },
    }
    _append_jsonl(log_path, ev)
    sys.stdout.write(log_path + "\n")
    return 0


def cmd_append_fix(args: argparse.Namespace) -> int:
    repo_root = _normalize_repo_root(args.repo)
    log_path = args.log_path or _default_log_path(repo_root)
    run_id = args.run_id or f"fix-{uuid.uuid4().hex[:10]}"

    results: List[Dict[str, Any]] = []
    for item in args.result:
        # Format: QPD-XXX:fixed[:note...]
        parts = item.split(":", 2)
        if len(parts) < 2:
            raise SystemExit(f"Invalid --result {item!r}. Expected ID:STATUS[:NOTE]")
        issue_id, status = parts[0].strip(), parts[1].strip()
        note = parts[2].strip() if len(parts) == 3 else None
        if not issue_id.startswith("QPD-"):
            raise SystemExit(f"Invalid issue id: {issue_id!r}")
        if not _is_issue_status(status):
            raise SystemExit(f"Invalid status {status!r}. Allowed: open,fixed,skipped,blocked,needs-review")
        results.append({"id": issue_id, "status": status, "note": note})

    ev: Dict[str, Any] = {
        "v": 1,
        "type": "fix",
        "at": _utc_now_iso(),
        "repo_root": repo_root,
        "run_id": run_id,
        "results": results,
        "meta": {
            "command": args.command,
            "tests": args.tests,
            "notes": args.notes,
            "touched_files": args.touched_file,
        },
    }
    _append_jsonl(log_path, ev)
    sys.stdout.write(log_path + "\n")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    repo_root = _normalize_repo_root(args.repo)
    log_path = args.log_path or _default_log_path(repo_root)
    events = _read_jsonl(log_path)
    state, warnings = _compute_state(events)
    if warnings and not args.quiet:
        for w in warnings:
            print(f"[qpd_log] Warning: {w}", file=sys.stderr)

    if args.out_json:
        payload = {
            "repo_root": repo_root,
            "log_path": log_path,
            "generated_at": _utc_now_iso(),
            "issues": [s.__dict__ for s in sorted(state.values(), key=lambda x: x.id)],
        }
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return 0

    _print_markdown_status(state)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Append/read scan-query-perf logs (JSONL).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create log directory and empty log file.")
    p_init.add_argument("--repo", required=True, help="Repo root path.")
    p_init.add_argument("--log-dir", help="Override log directory (default: <repo>/.codex/scan-query-perf).")
    p_init.set_defaults(fn=cmd_init)

    p_scan = sub.add_parser("append-scan", help="Append a scan event to the log.")
    p_scan.add_argument("--repo", required=True, help="Repo root path.")
    p_scan.add_argument("--log-path", help="Override log path (default: <repo>/.codex/scan-query-perf/qpd-log.jsonl).")
    p_scan.add_argument("--run-id", help="Optional run id (default: auto).")
    p_scan.add_argument("--issues-json", help="JSON array of issues with {id,severity,location}.")
    p_scan.add_argument("--command", help="Command(s) used for scan (for audit).")
    p_scan.add_argument("--notes", help="Freeform notes.")
    p_scan.set_defaults(fn=cmd_append_scan)

    p_fix = sub.add_parser("append-fix", help="Append a fix event to the log.")
    p_fix.add_argument("--repo", required=True, help="Repo root path.")
    p_fix.add_argument("--log-path", help="Override log path (default: <repo>/.codex/scan-query-perf/qpd-log.jsonl).")
    p_fix.add_argument("--run-id", help="Optional run id (default: auto).")
    p_fix.add_argument(
        "--result",
        action="append",
        required=True,
        help="Result item: QPD-XXXX:STATUS[:NOTE] where STATUS is fixed|skipped|blocked|needs-review|open.",
    )
    p_fix.add_argument("--touched-file", action="append", default=[], help="Touched file path (repeatable).")
    p_fix.add_argument("--tests", help="Exact test command(s) run + outcome.")
    p_fix.add_argument("--command", help="Command(s) used for fix (for audit).")
    p_fix.add_argument("--notes", help="Freeform notes.")
    p_fix.set_defaults(fn=cmd_append_fix)

    p_status = sub.add_parser("status", help="Compute issue status from the log.")
    p_status.add_argument("--repo", required=True, help="Repo root path.")
    p_status.add_argument("--log-path", help="Override log path (default: <repo>/.codex/scan-query-perf/qpd-log.jsonl).")
    p_status.add_argument("--out-json", action="store_true", help="Output JSON state instead of markdown.")
    p_status.add_argument("--quiet", action="store_true", help="Suppress warnings.")
    p_status.set_defaults(fn=cmd_status)

    args = parser.parse_args(argv)
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
