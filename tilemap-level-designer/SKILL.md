---
name: tilemap-level-designer
description: |
  Thiết kế map/level cho game 2D pixel (ưu tiên tilemap) và xuất dữ liệu triển khai được:
  layout, độ khó, tuyến tính/nhánh, spawn, trigger, collision, và quy ước layer/object.

  Dùng khi người dùng yêu cầu: "tạo map/level", "tilemap", "Tiled", "thiết kế level",
  "spawn point", "trigger/warp", "collision", "pacing độ khó".
---

# Tilemap Level Designer

## Mục tiêu

Tạo level chơi được (có mục tiêu, nhịp độ, thử thách) và dữ liệu map rõ quy ước để code import (đặc biệt phù hợp khi kết hợp với `ios-pixel-game-builder`).

## Quy trình thiết kế level (MVP → mở rộng)

### 1) Chốt “grammar” của level

- Tile size (8/16), kiểu camera (fixed/follow), tốc độ người chơi.
- 3–6 “khối” lặp lại (platform, gap, ladder, enemy, puzzle switch…).

### 2) Sketch level bằng khối (blockout)

- Vẽ nhanh bằng 1 tileset placeholder (1 màu).
- Đảm bảo người chơi luôn hiểu “đi đâu” (đường dẫn thị giác).
- Thêm checkpoint sớm nếu level dài.

### 3) Đặt object gameplay (spawn/trigger)

- Spawn: player, enemy, item.
- Trigger: warp, dialogue, tutorial popup, boss gate.
- Đọc quy ước layer/object: `references/tiled-conventions.md`.

### 4) Collision & kiểm thử

- Vẽ collision layer riêng (không render).
- Tạo “debug overlay” trong game để kiểm tra collision/triggers.
- Tối ưu: hạn chế tạo quá nhiều physics body nhỏ (merge rect khi import).

## Đầu ra đề xuất

- `LEVELS.md`: danh sách level (mục tiêu, mechanic mới, độ dài).
- `tiled/*.json` (export): map dữ liệu.
- `MAP-SPEC.md`: layer/object conventions.

## Tài nguyên kèm theo

- Quy ước Tiled: `references/tiled-conventions.md`
- File mẫu object types (Tiled): `assets/tiled-object-types.json`
