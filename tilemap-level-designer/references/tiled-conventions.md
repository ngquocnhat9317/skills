# Quy ước Tiled cho tilemap (gợi ý)

## Layer naming

- `ground`: tile hiển thị, có thể va chạm hoặc không (tuỳ game)
- `decor`: tile hiển thị, không va chạm
- `collision`: tile/object chỉ dùng collision, không render
- `spawns`: object spawn (player/enemy/item)
- `triggers`: object trigger (warp, checkpoint, dialogue, tutorial…)

## Object types (nên chuẩn hoá)

- `spawn_player`: điểm spawn player
- `spawn_enemy`: spawn enemy (properties: `enemyId`, `patrolPathId`…)
- `warp`: dịch chuyển (properties: `toLevel`, `toX`, `toY`)
- `checkpoint`: lưu tiến trình (properties: `checkpointId`)
- `trigger_dialogue`: bật hội thoại (properties: `dialogueId`)

## Properties

- Dùng `camelCase` cho key.
- Tránh thay đổi key sau khi đã triển khai vào code.

## Toạ độ

- Ghi rõ trong importer: origin của Tiled thường là top-left; SpriteKit coordinate có thể khác.
- Thêm một bước “normalize coordinates” duy nhất trong importer để tránh lỗi rải rác.

