# Scan Commands Reference

Detailed scan commands for Phase 2. Run only the sections matching the detected stack.

---

## 2.1 iOS / Xcode (HAS_XCODE)

```bash
# DerivedData — per-project analysis with mtime
echo "=== DerivedData per-project ==="
find ~/Library/Developer/Xcode/DerivedData -mindepth 1 -maxdepth 1 -type d 2>/dev/null | while read d; do
    last_mod=$(stat -f "%m" "$d" 2>/dev/null || echo 0)
    days_old=$(( ( $(date +%s) - $last_mod ) / 86400 ))
    size=$(du -sh "$d" 2>/dev/null | awk '{print $1}')
    proj=$(basename "$d" | sed 's/-[a-zA-Z0-9]*$//')
    status=$( [ "$days_old" -gt 30 ] && echo "STALE" || echo "RECENT" )
    echo "$status | ${days_old}d | $size | $proj"
done | sort -t'|' -k2 -rn
du -sh ~/Library/Developer/Xcode/DerivedData 2>/dev/null

# iOS DeviceSupport — list versions to identify old ones
echo "=== iOS DeviceSupport versions ==="
du -sh ~/Library/Developer/Xcode/iOS\ DeviceSupport/* 2>/dev/null | sort -rh

# Other Xcode artifacts
du -sh ~/Library/Developer/Xcode/DocumentationCache 2>/dev/null   # SAFE
du -sh ~/Library/Developer/Xcode/Archives 2>/dev/null              # CAUTION
du -sh ~/Library/Developer/Xcode/UserData/Previews 2>/dev/null    # SAFE
du -sh ~/Library/Logs/CoreSimulator 2>/dev/null                    # SAFE
du -sh ~/Library/Developer/CoreSimulator/Caches 2>/dev/null        # SAFE

# Simulator runtimes
xcrun simctl runtime list 2>/dev/null
du -sh /Library/Developer/CoreSimulator/Volumes/* 2>/dev/null | sort -rh
xcrun simctl list devices | grep -c "unavailable" 2>/dev/null
```

---

## 2.2 Android / Gradle (HAS_GRADLE)

```bash
# Gradle caches — SAFE vs CAUTION
du -sh ~/.gradle/caches/build-cache-* 2>/dev/null | sort -rh   # SAFE
du -sh ~/.gradle/caches/transforms-* 2>/dev/null                # SAFE
du -sh ~/.gradle/caches/jars-* 2>/dev/null                      # SAFE
du -sh ~/.gradle/caches/*/kotlin-dsl 2>/dev/null                # SAFE
du -sh ~/.gradle/caches/modules-* 2>/dev/null                   # CAUTION
du -sh ~/.gradle/wrapper/dists 2>/dev/null                      # CAUTION
du -sh ~/.gradle 2>/dev/null                                    # Total

# Android AVDs — often 5-15 GB each
ls ~/.android/avd/ 2>/dev/null
du -sh ~/.android/avd/* 2>/dev/null | sort -rh                  # CAUTION
du -sh ~/.android 2>/dev/null

# Android SDK
du -sh ~/Library/Android/sdk 2>/dev/null                        # Review only
du -sh ~/Library/Caches/Google/AndroidStudio*/ 2>/dev/null      # SAFE
```

---

## 2.3 Flutter / FVM

```bash
# pub-cache
du -sh ~/.pub-cache/hosted 2>/dev/null    # SAFE
du -sh ~/.pub-cache 2>/dev/null

# Flutter projects — find stale build/ and .dart_tool/
find ~/Documents ~/Developer ~/Desktop ~/projects -name "pubspec.yaml" \
  -not -path "*/.*" -maxdepth 6 2>/dev/null | while read f; do
    project=$(dirname "$f")
    days_old=$(( ( $(date +%s) - $(stat -f "%m" "$project/pubspec.yaml" 2>/dev/null || echo 0) ) / 86400 ))
    status=$( [ "$days_old" -gt 60 ] && echo "STALE" || echo "ACTIVE" )
    build_size=$(du -sh "$project/build" 2>/dev/null | awk '{print $1}')
    dart_size=$(du -sh "$project/.dart_tool" 2>/dev/null | awk '{print $1}')
    [ -n "$build_size" ] && echo "$status ${days_old}d | build: $build_size | $project"
    [ -n "$dart_size" ]  && echo "$status ${days_old}d | .dart_tool: $dart_size | $project"
done | sort -rh

# Flutter SDK cache
du -sh ~/flutter/bin/cache 2>/dev/null    # SAFE

# FVM (HAS_FVM) — check active version before suggesting removal
echo "=== FVM versions ==="
ls ~/fvm/versions/ 2>/dev/null
du -sh ~/fvm/versions/* 2>/dev/null | sort -rh    # CAUTION
cat ~/fvm/default 2>/dev/null || fvm list 2>/dev/null
du -sh ~/fvm 2>/dev/null
```

---

## 2.4 Node.js (HAS_NODE)

```bash
du -sh ~/.npm/_cacache 2>/dev/null

# Stale node_modules (project not touched in >60 days)
find ~/Documents ~/Developer ~/projects ~/Desktop \
  -name "node_modules" -type d \
  -not -path "*/node_modules/*/node_modules" \
  -maxdepth 7 2>/dev/null | while read nm; do
    parent=$(dirname "$nm")
    pkg="$parent/package.json"
    if [ -f "$pkg" ]; then
        days_old=$(( ( $(date +%s) - $(stat -f "%m" "$pkg" 2>/dev/null || echo 0) ) / 86400 ))
        size=$(du -sh "$nm" 2>/dev/null | awk '{print $1}')
        [ "$days_old" -gt 60 ] && echo "STALE ${days_old}d | $size | $nm" \
                                || echo "ACTIVE ${days_old}d | $size | $nm"
    fi
done 2>/dev/null | sort

# Yarn cache (HAS_YARN)
du -sh "$(yarn cache dir 2>/dev/null)" 2>/dev/null

# pnpm
pnpm store status 2>/dev/null || true

# node-gyp, webpack, puppeteer, prisma
du -sh ~/.node-gyp 2>/dev/null
du -sh ~/.cache/webpack 2>/dev/null
du -sh ~/.cache/puppeteer 2>/dev/null
du -sh ~/.cache/prisma 2>/dev/null
```

---

## 2.5 General (always run)

```bash
# Library Caches — top consumers
du -sh ~/Library/Caches 2>/dev/null
du -sh ~/Library/Caches/* 2>/dev/null | sort -rh | head -15

# Browser caches (SAFE)
du -sh ~/Library/Caches/Google 2>/dev/null
du -sh ~/Library/Caches/com.google.Chrome 2>/dev/null
du -sh ~/Library/Caches/Firefox 2>/dev/null

# Dev tool caches (SAFE)
du -sh ~/Library/Caches/CocoaPods 2>/dev/null
du -sh ~/Library/Caches/ms-playwright-go 2>/dev/null
du -sh ~/Library/Caches/ms-playwright 2>/dev/null
du -sh ~/Library/Caches/Homebrew 2>/dev/null
du -sh ~/.dartServer 2>/dev/null
du -sh ~/.cache 2>/dev/null

# Electron IDE app caches (SAFE — close app first)
du -sh ~/Library/Application\ Support/Slack/Cache 2>/dev/null
du -sh ~/Library/Application\ Support/Slack/CachedData 2>/dev/null
du -sh ~/Library/Application\ Support/Code/Cache 2>/dev/null
du -sh ~/Library/Application\ Support/Code/CachedData 2>/dev/null
du -sh ~/Library/Application\ Support/Cursor/Cache 2>/dev/null
du -sh ~/Library/Application\ Support/Cursor/CachedData 2>/dev/null
du -sh ~/Library/Application\ Support/Figma/Cache 2>/dev/null
# Top Application Support (report only — never delete wholesale)
du -sh ~/Library/Application\ Support/* 2>/dev/null | sort -rh | head -10

# VSCode old extension versions
ls ~/.vscode/extensions/ 2>/dev/null | sed 's/-[0-9]*\.[0-9]*\.[0-9]*-.*//' | sort | uniq -d | \
  while read ext; do echo "=== Dup: $ext ==="; ls ~/.vscode/extensions/ | grep "^$ext-" | sort -V; done
du -sh ~/.vscode/extensions 2>/dev/null

# System logs
du -sh ~/Library/Logs 2>/dev/null
du -sh ~/Library/Logs/* 2>/dev/null | sort -rh | head -10

# JetBrains logs
du -sh ~/Library/Logs/JetBrains/*/ 2>/dev/null | sort -rh

# Teams cache
du -sh ~/Library/Application\ Support/Microsoft/Teams/Cache 2>/dev/null
du -sh ~/Library/Application\ Support/Microsoft/Teams/Code\ Cache 2>/dev/null

# iOS Device Backups — CAUTION: can be 1-30 GB, permanent loss if deleted
du -sh ~/Library/Application\ Support/MobileSync/Backup 2>/dev/null
ls ~/Library/Application\ Support/MobileSync/Backup/ 2>/dev/null | wc -l | xargs echo "backups found:"

# Other
du -sh ~/.Trash 2>/dev/null
du -sh /Volumes/*/.Trashes 2>/dev/null | sort -rh
find ~ -maxdepth 2 -name "*.hprof" -type f 2>/dev/null | xargs du -sh 2>/dev/null | sort -rh
du -sh ~/Dropbox/.dropbox.cache 2>/dev/null
du -sh ~/Library/Application\ Support/Google/DriveFS/*/content_cache 2>/dev/null

# Package managers
pip3 cache info 2>/dev/null
du -sh ~/go/pkg/mod 2>/dev/null
du -sh ~/.gem 2>/dev/null
du -sh ~/.composer/cache 2>/dev/null
docker system df 2>/dev/null || true
```

---

## 2.6 Extended Ecosystems

```bash
# Rust (HAS_RUST)
du -sh ~/.cargo/registry/cache 2>/dev/null    # SAFE
du -sh ~/.rustup/downloads 2>/dev/null        # SAFE
du -sh ~/.rustup/tmp 2>/dev/null              # SAFE

# Maven (HAS_MAVEN)
du -sh ~/.m2/repository 2>/dev/null           # CAUTION

# SBT / Scala (HAS_SBT)
du -sh ~/.sbt/boot 2>/dev/null                # SAFE
du -sh ~/.sbt/preloaded 2>/dev/null           # SAFE
du -sh ~/.ivy2/cache 2>/dev/null              # SAFE

# Python extended
du -sh ~/.cache/uv 2>/dev/null               # SAFE (HAS_UV)
du -sh ~/Library/Caches/pypoetry 2>/dev/null # SAFE (HAS_POETRY)
du -sh ~/.pyenv/cache 2>/dev/null            # SAFE
du -sh ~/.conda/pkgs 2>/dev/null             # SAFE (HAS_CONDA)
du -sh ~/anaconda3/pkgs 2>/dev/null          # SAFE
du -sh ~/miniconda3/pkgs 2>/dev/null         # SAFE

# ML / AI models — can be very large
du -sh ~/.cache/huggingface 2>/dev/null      # CAUTION: model weights
du -sh ~/.cache/torch 2>/dev/null            # CAUTION
du -sh ~/.cache/tensorflow 2>/dev/null       # CAUTION
du -sh ~/.keras/models 2>/dev/null           # CAUTION
du -sh ~/.wandb 2>/dev/null                  # SAFE: logs only

# Terraform (HAS_TERRAFORM)
du -sh ~/.terraform.d 2>/dev/null
find ~/Documents ~/Developer ~/Desktop ~/projects -name ".terraform" \
  -type d -maxdepth 6 2>/dev/null | xargs du -sh 2>/dev/null | sort -rh | head -10

# Deno (HAS_DENO)
du -sh ~/.deno 2>/dev/null
du -sh ~/Library/Caches/deno 2>/dev/null

# Bun (HAS_BUN)
du -sh ~/.bun/install/cache 2>/dev/null

# Ruby (HAS_RBENV / HAS_RVM)
du -sh ~/.rbenv/versions 2>/dev/null          # CAUTION
du -sh ~/.rvm 2>/dev/null                     # CAUTION
du -sh ~/.bundle/cache 2>/dev/null            # SAFE

# Cloud CLI caches
du -sh ~/.kube/cache 2>/dev/null
du -sh ~/.aws/sso/cache 2>/dev/null
du -sh ~/.config/gcloud 2>/dev/null
```

---

## 2.7 Miscellaneous Paths

```bash
# macOS Resume snapshots (SAFE)
du -sh ~/Library/Saved\ Application\ State 2>/dev/null

# Xcode SwiftUI Previews (SAFE — separate from DerivedData)
du -sh ~/Library/Developer/Xcode/UserData/Previews 2>/dev/null

# Sparkle auto-updater remnants (SAFE — covers all apps using Sparkle)
du -sh ~/Library/Caches/*.ShipIt 2>/dev/null | sort -rh

# Mail attachment downloads (silent accumulator)
du -sh ~/Library/Containers/com.apple.mail/Data/Library/Mail\ Downloads 2>/dev/null

# Downloads folder — flag files older than 30 days (report only, don't delete)
echo "=== ~/Downloads older than 30 days ==="
find ~/Downloads -maxdepth 1 -type f -mtime +30 2>/dev/null | \
  xargs du -sh 2>/dev/null | sort -rh | head -10
```

---

## 2.8 App Caches

Only report if the cache directory exists (app is installed).

```bash
check_app_cache() { [ -d "$2" ] && du -sh "$2" 2>/dev/null; }

# Communication
check_app_cache "Discord"   ~/Library/Application\ Support/discord/Cache
check_app_cache "Discord"   ~/Library/Application\ Support/discord/Code\ Cache
check_app_cache "Zoom"      ~/Library/Caches/us.zoom.xos
check_app_cache "WhatsApp"  ~/Library/Caches/net.whatsapp.WhatsApp
check_app_cache "Telegram"  ~/Library/Application\ Support/Telegram\ Desktop/tdata/user_data/cache

# Productivity
check_app_cache "Notion"    ~/Library/Application\ Support/Notion/Cache
check_app_cache "Obsidian"  ~/Library/Application\ Support/obsidian/Cache
check_app_cache "Linear"    ~/Library/Application\ Support/Linear/Cache
check_app_cache "Alfred"    ~/Library/Caches/com.runningwithcrayons.Alfred

# Dev tools
check_app_cache "Windsurf"  ~/Library/Application\ Support/Windsurf/Cache
check_app_cache "Charles"   ~/Library/Caches/com.charlesproxy.charles
check_app_cache "SequelAce" ~/Library/Caches/com.sequel-ace.sequel-ace
check_app_cache "TablePlus" ~/Library/Caches/com.tinyapp.TablePlus
check_app_cache "MongoDB"   ~/Library/Caches/com.mongodb.compass
check_app_cache "Postman"   ~/Library/Caches/com.postmanlabs.mac

# Design
check_app_cache "Sketch"    ~/Library/Caches/com.bohemiancoding.sketch3
check_app_cache "Figma"     ~/Library/Caches/com.figma.desktop

# Media / Cloud
check_app_cache "Spotify"   ~/Library/Caches/com.spotify.client
check_app_cache "VLC"       ~/Library/Caches/org.videolan.vlc
check_app_cache "OneDrive"  ~/Library/Caches/com.microsoft.OneDrive

# AI apps
check_app_cache "Claude"    ~/Library/Caches/com.anthropic.claudefordesktop
check_app_cache "ChatGPT"   ~/Library/Caches/com.openai.chat

# Sparkle (any app using Sparkle auto-updater framework)
du -sh ~/Library/Caches/*.ShipIt 2>/dev/null | sort -rh
```

> **DO NOT report or suggest deleting:**
> `~/Library/CloudStorage` (iCloud mount), `~/Library/Metadata` (Spotlight),
> `~/Library/Biome` (system activity), `~/Library/IntelligencePlatform` (Apple AI),
> `~/Library/Containers` (sandboxed app data wholesale).
