# Prompt Templates

Use placeholders in `{UPPER_CASE}`.

## 1) South Anchor (Canonical)

```text
Generate one SOUTH-facing full-body neutral anchor for {CHARACTER_NAME}.
Preserve identity and readable silhouette for pixel-style game use.
Keep centered composition and stable foot plant.
Background must be transparent (#00000000).
No extra characters, no environment, no text, no action effects.
```

## 2) Directional Anchor

```text
Using approved SOUTH identity anchor, generate one {DIRECTION} neutral anchor.
Preserve exact identity, style, scale, and proportions.
Keep both feet visible on the same baseline and centered.
Background must be transparent (#00000000).
No dynamic effects, no scene, no text.
```

## 3) Idle (5 Frames)

```text
Create one {SHEET_SIZE} spritesheet for {DIRECTION} idle with exactly 5 frames.
Reject outputs with more than 5 frames.
Preserve identity, scale, center, and foot baseline in all frames.
Add subtle torso and arm breathing motion across frames.
No walking, no running, no turning, no attack effects.
No static duplicated frames.
Background must be transparent (#00000000).
```

## 4) Walk (5 Frames)

```text
Create one {SHEET_SIZE} spritesheet for {DIRECTION} walk with exactly 5 frames.
Reject outputs with more than 5 frames.
Preserve identity, direction, scale, center, and foot baseline in all frames.
Use a clear walk rhythm with visible alternating arm/leg motion.
No duplicated adjacent pose: frame1!=frame2, frame2!=frame3, frame3!=frame4.
Keep movement readable as WALK (moderate stride, moderate speed).
Background must be transparent (#00000000).
No camera motion, no scene, no text.
```

## 5) Run (5 Frames)

```text
Create one {SHEET_SIZE} spritesheet for {DIRECTION} run with exactly 5 frames.
Reject outputs with more than 5 frames.
Preserve identity, direction, scale, center, and foot baseline in all frames.
Use a clear run rhythm with stronger arm drive and longer stride than walk.
No duplicated adjacent pose: frame1!=frame2, frame2!=frame3, frame3!=frame4.
Keep movement readable as RUN (faster cadence, dynamic lean).
Background must be transparent (#00000000).
No camera motion, no scene, no text.
```

## 6) Regeneration Gate (If Failed)

```text
If output violates any gate (wrong frame count, repeated adjacent poses, static idle, wrong direction/state), regenerate with stricter enforcement and return only a valid 5-frame sheet.
```
