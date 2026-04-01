# Skeleton code đề xuất (SpriteKit)

## Tối thiểu cần có

- `GameScene`: update loop, spawn entity, camera follow, pause.
- `InputState`: gom touch → vector + action button.
- `PlayerController`: đọc InputState → velocity/animation.
- `Tilemap` (tuỳ game): load JSON/Tiled và cung cấp collision/triggers.

## Ranh giới module (để dễ mở rộng)

- `Core/`: input, time-step, camera, math util.
- `Game/`: scene, systems, entities.
- `Content/`: tilemaps, spritesheets, audio.

## Khi cần sinh file nhanh

Chạy: `python3 scripts/scaffold_spritekit_core.py --out <thư_mục>` trong workspace dự án để tạo các file Swift mẫu (có TODO rõ ràng).

