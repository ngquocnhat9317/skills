---
name: cleanup-mac
description: |
  Invoke for `/cleanup-mac` commands or when a Mac user wants to free disk space,
  clean build caches, or find what's consuming storage.

  Triggers: disk đầy, dọn dẹp mac, ổ cứng đầy, xoá cache, dung lượng,
  "disk full", "free up space", "clean cache", "what's eating my disk".

  Covers: Xcode DerivedData, Gradle, Flutter, node_modules, npm/yarn/pnpm,
  Rust/Maven/Go/Python, ~/Library/Caches, simulator runtimes, Ollama models,
  Electron app caches, iOS Device Backups, ML model caches.

  Skip for: cloud upload, installing simulators, CPU slowness, git cleanup.
---

# Mac Disk Cleanup Skill

Help the user reclaim disk space on macOS safely — always show sizes before
deleting, explain trade-offs for risky items, and confirm before acting.

## Mode Router

Identify the mode from the user's command before doing anything else.

| Mode      | Trigger                   | Phases        | Scope                  |
|-----------|---------------------------|---------------|------------------------|
| `full`    | `/cleanup-mac`            | 1→2→3→4→5→6  | All ecosystems         |
| `scan`    | `/cleanup-mac scan`       | 1→2→3 (stop) | All, report only       |
| `safe`    | `/cleanup-mac safe`       | 1→2→3→5→6    | SAFE items, 1 confirm  |
| `xcode`   | `/cleanup-mac xcode`      | 1→2→3→4→5→6  | Xcode/iOS only         |
| `android` | `/cleanup-mac android`    | 1→2→3→4→5→6  | Gradle/Android only    |
| `flutter` | `/cleanup-mac flutter`    | 1→2→3→4→5→6  | Flutter/Dart only      |
| `node`    | `/cleanup-mac node`       | 1→2→3→4→5→6  | Node/npm only          |
| `help`    | `/cleanup-mac help`       | —             | Print this guide       |

**`scan`** — report only, never delete. End with: "Gõ `/cleanup-mac safe` để dọn SAFE items."

**`safe`** — find SAFE items → show list → ask once "Xoá tất cả? (y/N)" → execute. Skip all CAUTION items.

**`xcode/android/flutter/node`** — focused modes: detect → scan that ecosystem only → report → confirm → execute. After finishing, suggest next mode if other stacks detected.

**`help`** — print the mode table above and exit.

---

## Phase 1 — DETECT

Run these checks to know which ecosystems are present, then announce: "Phát hiện stack: [list]"

```bash
which xcodebuild 2>/dev/null && echo "HAS_XCODE=true"
which flutter 2>/dev/null && echo "HAS_FLUTTER=true"
ls ~/fvm 2>/dev/null && echo "HAS_FVM=true"
ls ~/.gradle 2>/dev/null && echo "HAS_GRADLE=true"
which node 2>/dev/null && echo "HAS_NODE=true"
which yarn 2>/dev/null && echo "HAS_YARN=true"
which brew 2>/dev/null && echo "HAS_BREW=true"
which docker 2>/dev/null && echo "HAS_DOCKER=true"
which pip3 2>/dev/null && echo "HAS_PIP=true"
which pnpm 2>/dev/null && echo "HAS_PNPM=true"
which go 2>/dev/null && echo "HAS_GO=true"
which gem 2>/dev/null && echo "HAS_RUBY=true"
which rbenv 2>/dev/null && echo "HAS_RBENV=true"
which rvm 2>/dev/null && ls ~/.rvm 2>/dev/null && echo "HAS_RVM=true"
which composer 2>/dev/null && echo "HAS_COMPOSER=true"
which cargo 2>/dev/null && echo "HAS_RUST=true"
which mvn 2>/dev/null && ls ~/.m2 2>/dev/null && echo "HAS_MAVEN=true"
which sbt 2>/dev/null && ls ~/.sbt 2>/dev/null && echo "HAS_SBT=true"
which conda 2>/dev/null && echo "HAS_CONDA=true"
which uv 2>/dev/null && echo "HAS_UV=true"
which poetry 2>/dev/null && echo "HAS_POETRY=true"
which terraform 2>/dev/null && echo "HAS_TERRAFORM=true"
which deno 2>/dev/null && echo "HAS_DENO=true"
which bun 2>/dev/null && echo "HAS_BUN=true"
ls ~/.cache/huggingface 2>/dev/null && echo "HAS_HF=true"
ls ~/.cache/torch 2>/dev/null && echo "HAS_TORCH=true"

# Save baseline for delta calculation in Phase 6
DISK_BEFORE=$(df / | tail -1 | awk '{print $4}')
df -h / | awk 'NR==2 {printf "💾 Disk: %s used / %s total (%s free)\n", $3, $2, $4}'
```

> **If bash is unavailable:** show the commands above, ask the user to run them in Terminal, and continue based on what they report.

---

## Phase 2 — SCAN

Read **`references/scan-commands.md`** and run the sections that match the detected stack.
Always show sizes before reporting — never skip a section that has matching tools.

Sections in scan-commands.md:
- **2.1** iOS / Xcode
- **2.2** Android / Gradle
- **2.3** Flutter / FVM
- **2.4** Node.js
- **2.5** General (always run)
- **2.6** Extended ecosystems (Rust, Maven, Python ML, Terraform, Deno, Bun, Ruby+)
- **2.7** Missing paths (Saved App State, Mail Downloads, Trash, Downloads)
- **2.8** App caches (Discord, Zoom, Notion, Sketch, Spotify, etc.)

---

## Phase 3 — REPORT

Present findings in this format:

```
📊 DISK USAGE REPORT
════════════════════════════════════════
💾 Hiện tại: [X] GB used / [Y] GB free

✅ SAFE — Delete immediately (auto-regenerates)
─────────────────────────────────────
  [size]  DerivedData stale (>30d, N projects)
  [size]  ~/Library/Caches (breakdown by app)
  [size]  Gradle build-cache + transforms
  [size]  Flutter build/ stale projects
  [size]  node_modules stale (>60d)
  [size]  ~/.dartServer, Electron caches, Logs
  [size]  Rust/Python/SBT/Deno caches
  ──────────────────────────────────
  Total SAFE: ~X GB

⚠️  CAUTION — Deletable but has trade-offs
─────────────────────────────────────
  [size]  DerivedData RECENT (<30d)    → rebuild needed
  [size]  iOS DeviceSupport [old vers] → reconnect device
  [size]  iOS Device Backups           → PERMANENT LOSS ⛔
  [size]  ~/.gradle/caches/modules-2  → re-download deps
  [size]  Simulator runtimes           → re-download 5-8GB
  [size]  ML models (HF/Torch/Keras)  → re-download GB-level
  [size]  Maven ~/.m2, rbenv, RVM      → re-download
  ──────────────────────────────────
  Total CAUTION: ~X GB

🔴 DO NOT DELETE
─────────────────────────────────────
  ~/Library/Preferences, Keychains, Containers,
  CloudStorage (iCloud), Metadata (Spotlight),
  Biome, IntelligencePlatform
════════════════════════════════════════
Potential: ~X GB (SAFE) + ~X GB (CAUTION if chosen)
```

---

## Phase 4 — CONFIRM

Ask once per group — never ask item by item:

```
Bạn muốn xoá nhóm nào?
[1] ✅ SAFE (~X GB) — No risk
[2] ⚠️  CAUTION — Choose per item
[3] Both
[4] Report only, no delete
```

For CAUTION items (if user picks 2 or 3), ask each separately with its trade-off clearly stated.

---

## Phase 5 — EXECUTE

Read **`references/execute-commands.md`** for the full delete commands.

Before executing, run these safety checks:

```bash
# Xcode running? (block DerivedData delete if yes)
pgrep -x Xcode > /dev/null && echo "⚠️ XCODE RUNNING — close before deleting DerivedData"

# Stop Gradle daemon before deleting .gradle
pkill -f GradleDaemon 2>/dev/null && echo "Gradle daemon stopped"

# Shut down simulators before deleting runtimes
xcrun simctl shutdown all 2>/dev/null
```

Show `✅ Done: [item] [size]` for each deleted item. Show `⏭ Skipped: [item]` for locked files.

---

## Phase 6 — SUMMARY

```bash
DISK_AFTER=$(df / | tail -1 | awk '{print $4}')
FREED_BLOCKS=$((DISK_AFTER - DISK_BEFORE))
FREED_GB=$(awk "BEGIN {printf \"%.1f\", $FREED_BLOCKS * 512 / 1073741824}")
df -h / | awk 'NR==2 {printf "💾 Free now: %s / %s\n", $4, $2}'
```

Display and save log:

```
════════════════════════════════════════
✅ CLEANUP COMPLETE
════════════════════════════════════════
Before:  [X] GB free
After:   [Y] GB free
Freed:   [Z] GB 🎉

Details:
  ✅ DerivedData        X GB
  ✅ ~/Library/Caches   X GB
  ...
📋 Log saved: ~/cleanup-logs/YYYY-MM-DD_HH-MM.md
════════════════════════════════════════
```

Save log to `~/cleanup-logs/$(date '+%Y-%m-%d_%H-%M').md`.

Always remind the user what to run next:
```
🔄 After cleanup:
  • Flutter:  flutter pub get
  • Node:     npm install
  • Android:  open Android Studio (Gradle auto-syncs)
  • Xcode:    re-index takes ~5-15 min automatically
  • Simulator: Xcode > Settings > Platforms to re-download

📅 Run /cleanup-mac safe monthly — takes ~2 min, zero risk.
```

---

## Safety Rules (Never violate)

1. **Never delete** these regardless of user request:
   `~/Library/Preferences`, `~/Library/Keychains`, `~/Library/Containers`,
   `~/Library/Group Containers`, `~/.ssh`, `~/.gnupg`,
   `~/Library/Application Support` (whole dir — only Cache/CachedData subfolders OK),
   `~/Library/CloudStorage`, `~/Library/Metadata`, `~/Library/Biome`,
   `~/Library/IntelligencePlatform`

2. **Never `rm -rf` simulators directly** — always use `xcrun simctl`

3. **Never delete DerivedData** while Xcode is running

4. **Never delete `.gradle`** while Gradle daemon is running — stop it first

5. **Always show size** before deleting anything

6. **Always explain trade-offs** for CAUTION items before asking to confirm

7. **Stale threshold** — node_modules/build dirs are only "stale" if the marker file
   (`package.json` / `pubspec.yaml`) hasn't been modified in **60+ days**
