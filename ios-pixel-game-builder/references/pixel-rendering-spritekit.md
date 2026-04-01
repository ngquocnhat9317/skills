# Pixel rendering trong SpriteKit (iOS)

## Mục tiêu

- Giữ pixel “sắc” (nearest-neighbor), không blur.
- Giữ tỉ lệ scale **nguyên** (2x/3x/4x…) giữa “base resolution” và màn hình thực.
- Tránh jitter khi camera di chuyển.

## Checklist nhanh

- Dùng texture filtering nearest:
  - `SKTexture.defaultFilteringMode = .nearest` (đặt sớm, trước khi tạo texture)
  - Hoặc `texture.filteringMode = .nearest` cho từng texture quan trọng
- Không dùng scale lẻ cho sprite nếu muốn pixel-perfect.
- Khi cập nhật vị trí camera/player, “snap” về lưới pixel (theo base resolution) để giảm jitter.

## Base resolution & scale

1) Chọn `baseSize` (px) cho toàn game (vd 320×180 cho 16:9).
2) Tính `scale = floor(min(viewW/baseW, viewH/baseH))` và ép `scale >= 1`.
3) Render world theo đơn vị “pixel” của baseSize; camera/scene scale theo `1/scale` hoặc ngược lại tuỳ pipeline.

Gợi ý: Nếu bạn coi 1 unit = 1 pixel trong base resolution, hãy luôn đảm bảo camera scale và node scale không tạo số lẻ ở “pixel-space”.

## Camera snapping (ý tưởng)

- Tính vị trí camera theo player.
- Chuyển sang “pixel-space”: `px = world * scale`.
- Làm tròn: `px = round(px)`.
- Đưa về world: `world = px / scale`.

## iOS điểm ảnh

- SpriteKit làm việc theo “points” (không phải device pixels). iPhone có scale factor (2x/3x).
- “Pixel-perfect” ở đây là pixel theo base resolution của game, không nhất thiết khớp 1:1 với device pixel.

