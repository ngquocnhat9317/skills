---
name: ios-pixel-game-builder
description: |
  Hỗ trợ thiết kế và xây dựng game mobile 2D đồ hoạ pixel cho iOS bằng Swift + SpriteKit:
  gameplay loop, điều khiển cảm ứng, camera, vật lý/collision, tilemap, UI/HUD, tối ưu hiệu năng,
  và đóng gói chạy trên Simulator/thiết bị.

  Dùng khi người dùng yêu cầu: "làm game pixel iOS", "SpriteKit", "game 2D iPhone",
  "tilemap", "pixel perfect scaling", "điều khiển joystick/button", "tối ưu FPS".
---

# iOS Pixel Game Builder

## Mục tiêu

Chuyển một ý tưởng game pixel (thể loại, vòng lặp chơi, art, map, nhạc) thành bộ tài liệu + cấu trúc code SpriteKit tối thiểu để chạy được trên iOS, rồi mở rộng an toàn theo phạm vi.

## Luồng làm việc (ưu tiên theo thứ tự)

### 1) Chốt ràng buộc “pixel” (đừng bắt tay vào code trước)

- Hỏi và chốt: màn hình dọc/ngang, target FPS (60/120), “base resolution” (vd 320×180 hoặc 256×144),
  tỉ lệ scale **nguyên** (2x/3x/4x…), kích thước tile (vd 16px), và palette.
- Đọc: `references/pixel-rendering-spritekit.md` để setup “pixel perfect” trong SpriteKit.

### 2) Chốt “core loop” và phạm vi (GDD mini)

- Viết 1 trang: mục tiêu người chơi, 30–60 giây đầu, điều kiện thắng/thua, tiến triển (level/score),
  danh sách hệ thống (movement, combat, inventory…), và “MVP cutline”.
- Nếu cần kịch bản/hội thoại/quest: dùng `game-script-writer`.

### 3) Dựng khung SpriteKit chạy được (prototype)

- Tạo một Scene chơi được với: player placeholder, 1 map phẳng, camera theo player, input cảm ứng.
- Nếu có workspace code: tạo/điền các file Swift theo skeleton trong `references/project-skeleton.md`.
- Nếu cần tạo nhanh file mẫu: chạy `scripts/scaffold_spritekit_core.py --out <thư_mục>`.

### 4) Điều khiển (touch) + cảm giác nhân vật

- Chọn 1 trong: D-pad 4 hướng, joystick ảo, swipe-dash, hoặc tap-to-move.
- Đọc: `references/controls-patterns.md` và dùng đúng một kiểu cho MVP.
- Luôn có “input debug overlay” (hiện vector joystick/điểm chạm) khi test.

### 5) Tilemap + va chạm + trigger

- Thiết kế map bằng Tiled (khuyến nghị) hoặc viết tay dữ liệu.
- Chuẩn hoá layer/object: ground, collision, spawns, triggers, decor.
- Đọc: `references/tilemap-import.md`.
- Nếu cần tạo map/level nhanh: dùng `tilemap-level-designer`. Nếu cần vẽ tiles/sprites: dùng `pixel-art-maker`.

### 6) UI/HUD + tiến triển + lưu game

- UI tối thiểu: HP/score/timer + pause.
- Lưu state tối thiểu: level hiện tại, coin/score, tuỳ chọn điều khiển.

### 7) Hiệu năng & phát hành

- Giữ draw calls thấp (texture atlas/spritesheet), tránh node count quá cao, dùng culling đơn giản.
- Test trên Simulator và ít nhất 1 thiết bị thật trước khi tăng scope.

## Đầu ra tiêu chuẩn (để dễ phối hợp)

- `GDD-mini.md`: 1 trang core loop + scope MVP.
- `ART-SPEC.md`: base resolution, tile size, palette, naming spritesheets.
- `MAP-SPEC.md`: layer/object conventions + danh sách level.
- `AUDIO-SPEC.md`: mood/tempo + list SFX.
- Code: tối thiểu một Scene chạy được, input hoạt động, camera + scaling “pixel perfect”.

## Tài liệu tham chiếu

- Pixel rendering: `references/pixel-rendering-spritekit.md`
- Skeleton dự án: `references/project-skeleton.md`
- Controls: `references/controls-patterns.md`
- Tilemap: `references/tilemap-import.md`
