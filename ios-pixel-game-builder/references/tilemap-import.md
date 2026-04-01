# Tilemap cho SpriteKit (khuyến nghị: Tiled)

## Quy ước (nên chốt trước khi vẽ map)

- `tileSize`: 16×16 hoặc 8×8.
- Layer:
  - `ground` (tile hiển thị)
  - `decor` (tile hiển thị, không va chạm)
  - `collision` (tile hoặc object, không render)
  - `triggers` (object: warp, checkpoint, dialog, pickup…)
  - `spawns` (object: player/enemy spawn)

## Xuất dữ liệu

- Ưu tiên export JSON từ Tiled (dễ parse).
- Mỗi object nên có:
  - `type` (spawn/warp/trigger…)
  - `name` (tuỳ chọn)
  - `properties` (key/value: targetLevel, toX, toY, itemId…)

## Import (hướng tiếp cận)

- Parse JSON → tạo node cho layer hiển thị.
- Collision:
  - Cách đơn giản: mỗi tile collision → 1 physics body (dễ nhưng nặng)
  - Cách tốt hơn: “merge” các ô liền nhau thành rect lớn (giảm body count)

## Sanity check

- Vẽ overlay collision (màu semi-transparent) để debug.
- Kiểm tra toạ độ: Tiled thường dùng origin top-left, SpriteKit mặc định origin khác; luôn chuẩn hoá một lần ở importer.

