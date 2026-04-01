# Execute Commands Reference

Delete commands for Phase 5. Run only what the user confirmed in Phase 4.

---

## SAFE Items — Delete without risk

These regenerate automatically. Safe to run immediately after confirmation.

```bash
# ── Xcode ──────────────────────────────────────────────────────────
# DerivedData SMART: only stale projects (>30 days since last build)
find ~/Library/Developer/Xcode/DerivedData -mindepth 1 -maxdepth 1 -type d 2>/dev/null | while read d; do
    days_old=$(( ( $(date +%s) - $(stat -f "%m" "$d" 2>/dev/null || echo 0) ) / 86400 ))
    if [ "$days_old" -gt 30 ]; then
        size=$(du -sh "$d" 2>/dev/null | awk '{print $1}')
        rm -rf "$d" && echo "✅ DerivedData removed (${days_old}d, $size): $(basename $d)"
    else
        echo "⏭ Kept (${days_old}d): $(basename $d)"
    fi
done
# To remove ALL DerivedData instead: rm -rf ~/Library/Developer/Xcode/DerivedData

rm -rf ~/Library/Developer/Xcode/DocumentationCache && echo "✅ DocumentationCache"
rm -rf ~/Library/Developer/Xcode/UserData/Previews && echo "✅ Xcode Previews"
rm -rf ~/Library/Logs/CoreSimulator && echo "✅ CoreSimulator logs"
rm -rf ~/Library/Developer/CoreSimulator/Caches && echo "✅ CoreSimulator caches"

# ── Gradle ─────────────────────────────────────────────────────────
rm -rf ~/.gradle/caches/build-cache-*/ && echo "✅ Gradle build-cache"
rm -rf ~/.gradle/caches/transforms-*/ && echo "✅ Gradle transforms"
rm -rf ~/.gradle/caches/jars-*/       && echo "✅ Gradle jars"
rm -rf ~/.gradle/caches/*/kotlin-dsl/ && echo "✅ Gradle kotlin-dsl"
find ~/.gradle/daemon -name "*.log" -delete 2>/dev/null && echo "✅ Gradle daemon logs"

# ── Flutter / Dart ──────────────────────────────────────────────────
# [Loop over stale project paths found in Phase 2 scan]
# rm -rf "[project_path]/build"
# rm -rf "[project_path]/.dart_tool"
rm -rf ~/.dartServer && echo "✅ Dart analysis server cache"

# ── Node.js ─────────────────────────────────────────────────────────
# [Loop over stale node_modules paths found in Phase 2 scan]
# rm -rf "[stale_nm_path]"
npm cache clean --force 2>/dev/null && echo "✅ npm cache"
yarn cache clean --force 2>/dev/null && echo "✅ yarn cache" || true
pnpm store prune 2>/dev/null && echo "✅ pnpm store" || true
rm -rf ~/.node-gyp && echo "✅ node-gyp"
rm -rf ~/.cache/webpack && echo "✅ webpack cache"
rm -rf ~/.cache/puppeteer && echo "✅ Puppeteer"
rm -rf ~/.cache/prisma && echo "✅ Prisma engines"

# ── Rust ─────────────────────────────────────────────────────────────
rm -rf ~/.cargo/registry/cache && echo "✅ Cargo registry cache"
rm -rf ~/.rustup/downloads ~/.rustup/tmp && echo "✅ Rustup downloads"

# ── Python ───────────────────────────────────────────────────────────
pip3 cache purge 2>/dev/null && echo "✅ pip cache"
rm -rf ~/.cache/uv && echo "✅ uv cache"
rm -rf ~/Library/Caches/pypoetry && echo "✅ Poetry cache"
rm -rf ~/.pyenv/cache && echo "✅ pyenv cache"
conda clean --all --yes 2>/dev/null || \
  rm -rf ~/.conda/pkgs/* ~/anaconda3/pkgs/* ~/miniconda3/pkgs/* 2>/dev/null
echo "✅ Conda pkgs"

# ── Scala / SBT ──────────────────────────────────────────────────────
rm -rf ~/.sbt/boot ~/.sbt/preloaded && echo "✅ SBT cache"
rm -rf ~/.ivy2/cache && echo "✅ Ivy2 cache"

# ── Ruby ──────────────────────────────────────────────────────────────
gem cleanup 2>/dev/null || true && echo "✅ Old gem versions"
rm -rf ~/.bundle/cache && echo "✅ Bundler cache"

# ── PHP ───────────────────────────────────────────────────────────────
composer clearcache --no-interaction 2>/dev/null || true && echo "✅ Composer cache"

# ── Deno / Bun ───────────────────────────────────────────────────────
rm -rf ~/Library/Caches/deno ~/.deno/deps && echo "✅ Deno cache"
rm -rf ~/.bun/install/cache && echo "✅ Bun cache"

# ── Terraform ────────────────────────────────────────────────────────
rm -rf ~/.terraform.d/plugin-cache && echo "✅ Terraform plugin cache"

# ── Homebrew ─────────────────────────────────────────────────────────
brew cleanup --prune=all 2>/dev/null && echo "✅ Homebrew"
brew tap --repair 2>/dev/null

# ── General caches ───────────────────────────────────────────────────
# Library Caches (skip locked files)
find ~/Library/Caches -mindepth 1 -maxdepth 1 -type d | while read d; do
    rm -rf "$d" 2>/dev/null && echo "✅ $d" || echo "⏭ Locked: $d"
done
rm -rf ~/.cache && echo "✅ ~/.cache"

# ── IDE / Electron app caches (close apps before running) ────────────
rm -rf ~/Library/Application\ Support/Slack/Cache      2>/dev/null && echo "✅ Slack cache"
rm -rf ~/Library/Application\ Support/Slack/CachedData 2>/dev/null
rm -rf ~/Library/Application\ Support/Code/Cache       2>/dev/null && echo "✅ VSCode cache"
rm -rf ~/Library/Application\ Support/Code/CachedData  2>/dev/null
rm -rf ~/Library/Application\ Support/Cursor/Cache     2>/dev/null && echo "✅ Cursor cache"
rm -rf ~/Library/Application\ Support/Cursor/CachedData 2>/dev/null
rm -rf ~/Library/Application\ Support/Figma/Cache      2>/dev/null && echo "✅ Figma cache"
rm -rf ~/Library/Application\ Support/Microsoft/Teams/Cache         2>/dev/null
rm -rf ~/Library/Application\ Support/Microsoft/Teams/CachedData    2>/dev/null
rm -rf ~/Library/Application\ Support/Microsoft/Teams/Code\ Cache   2>/dev/null
rm -rf ~/Library/Application\ Support/Microsoft/Teams/blob_storage  2>/dev/null
echo "✅ Teams cache"

# ── VSCode old extension versions ────────────────────────────────────
ls ~/.vscode/extensions/ 2>/dev/null | sed 's/-[0-9]*\.[0-9]*\.[0-9]*-.*//' | sort | uniq -d | \
  while read ext; do
    ls ~/.vscode/extensions/ | grep "^$ext-" | sort -V | head -n -1 | \
      while read old; do rm -rf ~/.vscode/extensions/"$old" && echo "✅ Old ext: $old"; done
  done

# ── System artifacts ─────────────────────────────────────────────────
rm -rf ~/Library/Logs/*              2>/dev/null && echo "✅ ~/Library/Logs"
rm -rf ~/Library/Logs/JetBrains/*/  2>/dev/null && echo "✅ JetBrains logs"
rm -rf ~/Library/Saved\ Application\ State/* 2>/dev/null && echo "✅ Saved App State"
rm -rf ~/Library/Caches/*.ShipIt    2>/dev/null && echo "✅ Sparkle ShipIt caches"
rm -rf ~/Library/Caches/Google/AndroidStudio*/ 2>/dev/null && echo "✅ Android Studio cache"
rm -rf ~/Library/Containers/com.apple.mail/Data/Library/Mail\ Downloads/* 2>/dev/null && echo "✅ Mail downloads"
rm -rf ~/.Trash/*                    2>/dev/null && echo "✅ Trash"
rm -rf /Volumes/*/.Trashes/*         2>/dev/null && echo "✅ External drive Trash"
find ~ -maxdepth 2 -name "*.hprof" -type f -delete 2>/dev/null && echo "✅ Java .hprof dumps"

# ── Cloud storage caches ─────────────────────────────────────────────
rm -rf ~/Dropbox/.dropbox.cache/* 2>/dev/null && echo "✅ Dropbox cache"

# ── Popular app caches ───────────────────────────────────────────────
for cache_path in \
  ~/Library/Application\ Support/discord/Cache \
  ~/Library/Application\ Support/discord/Code\ Cache \
  ~/Library/Caches/us.zoom.xos \
  ~/Library/Application\ Support/Notion/Cache \
  ~/Library/Application\ Support/obsidian/Cache \
  ~/Library/Application\ Support/Windsurf/Cache \
  ~/Library/Caches/com.charlesproxy.charles \
  ~/Library/Caches/com.sequel-ace.sequel-ace \
  ~/Library/Caches/com.tinyapp.TablePlus \
  ~/Library/Caches/com.mongodb.compass \
  ~/Library/Caches/com.bohemiancoding.sketch3 \
  ~/Library/Caches/com.spotify.client \
  ~/Library/Caches/com.microsoft.OneDrive \
  ~/Library/Caches/com.anthropic.claudefordesktop \
  ~/Library/Caches/com.openai.chat; do
  [ -d "$cache_path" ] && rm -rf "$cache_path" && echo "✅ $(basename $cache_path)"
done

# ── Browser caches (close browser first) ─────────────────────────────
rm -rf ~/Library/Caches/Google && echo "✅ Chrome cache"
rm -rf ~/Library/Caches/com.google.Chrome
rm -rf ~/Library/Caches/CocoaPods && echo "✅ CocoaPods cache"
rm -rf ~/Library/Caches/ms-playwright-go && echo "✅ Playwright cache"
rm -rf ~/Library/Caches/ms-playwright
```

---

## CAUTION Items — Ask each one before deleting

Each item below requires individual user confirmation. Explain the trade-off first.

```bash
# ── Xcode Archives ───────────────────────────────────────────────────
# Trade-off: lose ability to symbolicate old crash reports
rm -rf ~/Library/Developer/Xcode/Archives/[specific-archive]

# ── iOS DeviceSupport (old versions only) ────────────────────────────
# Trade-off: must reconnect physical device to regenerate
# Keep the version matching the user's current iOS device
# List first: du -sh ~/Library/Developer/Xcode/iOS\ DeviceSupport/* | sort -rh
rm -rf ~/Library/Developer/Xcode/iOS\ DeviceSupport/"[old-version]"

# ── iOS Device Backups ───────────────────────────────────────────────
# ⛔ Trade-off: PERMANENT — cannot recover without restore from iCloud/iTunes
# Only delete if user explicitly says they have another backup
rm -rf ~/Library/Application\ Support/MobileSync/Backup/"[specific-backup]"

# ── Simulator runtimes ───────────────────────────────────────────────
# Trade-off: must re-download 5-8 GB per runtime
# ALWAYS use xcrun, never rm -rf directly
xcrun simctl delete unavailable
xcrun simctl runtime delete "iOS X.X"
# Or clean up runtimes unused for 90+ days:
xcrun simctl runtime delete all --notUsedSinceDays 90

# ── Gradle modules cache ─────────────────────────────────────────────
# Trade-off: re-downloads all Maven/JCenter dependencies on next build
rm -rf ~/.gradle/caches/modules-*/
rm -rf ~/.gradle/wrapper/dists/

# ── Flutter pub-cache ────────────────────────────────────────────────
# Trade-off: triggers re-download on next flutter pub get; removes globally activated tools
# Run after: flutter pub cache repair
rm -rf ~/.pub-cache/

# ── FVM Flutter versions ─────────────────────────────────────────────
# Trade-off: must re-download if needed again
# Check active version first: cat ~/fvm/default
# fvm remove [version] OR:
rm -rf ~/fvm/versions/[unused-version]

# ── Go module cache ──────────────────────────────────────────────────
# Trade-off: re-downloads on next go build
go clean -modcache

# ── Maven repository ─────────────────────────────────────────────────
# Trade-off: re-downloads all Java/Kotlin dependencies
rm -rf ~/.m2/repository

# ── ML model weights ─────────────────────────────────────────────────
# Trade-off: re-download can be several GB per model
# Use ollama rm <model-name> — never delete blobs directly (shared layers)
ollama rm [model-name]
# Hugging Face — remove specific model dirs inside hub/
rm -rf ~/.cache/huggingface/hub/models--[org]--[model]
# PyTorch / Keras
rm -rf ~/.cache/torch/[specific-model]
rm -rf ~/.keras/models/[specific-model]

# ── Ruby version managers ────────────────────────────────────────────
# Trade-off: must reinstall Ruby versions if needed
rbenv uninstall [version]     # or: rm -rf ~/.rbenv/versions/[version]
# RVM: rvm remove [version]   # or: rm -rf ~/.rvm/rubies/[version]

# ── Android AVD emulators ────────────────────────────────────────────
# Trade-off: must recreate AVD + re-download system image (2-4 GB each)
# Back up debug.keystore first!
cp ~/.android/debug.keystore ~/Desktop/debug.keystore.backup
avdmanager delete avd -n "[avd-name]"
```
