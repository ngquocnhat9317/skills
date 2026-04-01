---
name: pixel-art-maker
description: |
  Thiết kế và tạo đồ hoạ pixel cho game: tileset, sprite nhân vật, animation,
  UI/HUD pixel, icon, spritesheet packing, và quy ước xuất file để đưa vào engine.

  Dùng khi người dùng yêu cầu: "vẽ pixel art", "sprite", "tileset", "pixel UI",
  "animation 8 hướng", "spritesheet", "palette", "aseprite".
---

# Pixel Art Maker

## Mục tiêu

Tạo asset pixel nhất quán (kích thước, palette, style, animation) và xuất ra định dạng dễ tích hợp (PNG spritesheet + metadata) cho game 2D.

## Quy trình (làm đúng 1 lần để khỏi sửa về sau)

### 1) Chốt “style spec”

- Tile size (8/16), outline có/không, mức shading (1–3 tone), độ tương phản.
- Palette: bắt đầu ít màu (16–32). Có thể dùng `assets/palettes/codex16.hex` để prototype.
- Chốt tỉ lệ nhân vật so với tile (vd cao 24px trong tile 16px).

### 2) Tạo tileset nền (đủ để test gameplay)

- 5–10 tile quan trọng: ground, wall, platform edge, slope (nếu có), hazard.
- Ưu tiên readability hơn chi tiết.

### 3) Tạo nhân vật + animation tối thiểu

- Start với 3 trạng thái: idle, walk/run, hit.
- Nếu top-down: 4 hướng trước, 8 hướng sau khi gameplay ổn.

### 4) UI/HUD pixel

- Font/bitmap font (nếu có), icon 16×16/24×24, thanh HP/energy.
- Tránh text quá dài; ưu tiên icon + số.

### 5) Xuất file & naming

- PNG: giữ alpha sạch, tránh semi-transparent nếu muốn pixel “cứng”.
- Spritesheet: grid nhất quán; naming theo `assets/spritesheet-naming.txt`.
- Nếu cần metadata: xuất JSON (frame name → rect, duration) hoặc Aseprite JSON.

## Đầu ra đề xuất

- `ART-SPEC.md`: tile size, palette, style rules.
- `tileset.png`, `characters.png`, `ui.png` (spritesheets).
- `frames.json` (nếu dùng animation theo frame).

## Tài nguyên kèm theo

- Palette prototype: `assets/palettes/codex16.hex`
- Quy ước naming spritesheet: `assets/spritesheet-naming.txt`
