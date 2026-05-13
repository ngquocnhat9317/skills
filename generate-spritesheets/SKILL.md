---
name: generate-spritesheets
description: Generate a single consistent 2D top-down character spritesheet per request using anchor-first generation and normalization. Use when input specifies one direction (north/south/west/east), one state (idle/walk/run), 5-frame output, and engine-ready transparent PNG sprite assets.
---

# Generate Spritesheets

Dùng skill này để tạo **một spritesheet duy nhất cho hoạt động được yêu cầu**, thay vì generate cả bộ nhiều hướng/trạng thái.

## Input Contract

User cần cung cấp:
- Hướng: `north` | `south` | `west` | `east`
- Trạng thái: `idle` | `walk` | `run`
- Character spec: identity, outfit, style, frame size
- Background (mặc định): `#00000000`

## Output Contract

- Chỉ trả về **1 spritesheet** đúng theo `Hướng + Trạng thái` user yêu cầu.
- Mỗi spritesheet có **exactly 5 frames**.
- Không trả thêm animation khác nếu user không yêu cầu.

## Workflow

1. Xác định đặc tả
- Chốt identity, palette, outfit, frame size runtime.
- Chốt `direction` và `state` duy nhất cho lần generate này.

2. Tạo anchor theo pipeline gốc
- Tạo concept nếu cần.
- Tạo south anchor trung tính (canonical).
- Reset neutral nếu có effect bake-in.
- Suy ra anchor theo hướng yêu cầu (west/north; east có thể flip từ west nếu cần consistency).

3. Generate animation theo trạng thái yêu cầu
- `idle`: tạo loop 5 frame với chuyển động nhẹ.
- `walk`: tạo loop 5 frame nhịp đi bộ rõ ràng.
- `run`: tạo loop 5 frame nhịp chạy nhanh hơn walk, stride dài hơn, thân nghiêng tiến.

4. Chuẩn hóa frame
- Bắt buộc alpha nền trong suốt `#00000000`.
- Khóa `center_x`, baseline chân, scale nhất quán.
- Rebuild sheet đúng 5 frame.

## Quality Gates

- Cấm output có số frame khác 5.
- Cấm trả về nhiều hơn 1 animation trong một lần generate.
- Giữ identity, tỷ lệ, baseline chân ổn định trên toàn bộ frame.
- Cấm duplicate pose liên tiếp cho movement:
- `frame1 != frame2`
- `frame2 != frame3`
- `frame3 != frame4`
- Với `walk` và `run`, pose tay/chân phải đọc được pha chuyển động và đúng ngữ nghĩa trạng thái (run phải năng động hơn walk).
- Với `idle`, bắt buộc có chuyển động nhẹ thân + tay theo nhịp thở; cấm copy-paste frame tĩnh.

## Prompt-Level Gates

- Mọi prompt animation phải có `exactly 5 frames` và `reject outputs with more than 5 frames`.
- Prompt `walk/run` phải có ràng buộc không lặp pose liên tiếp (`1!=2`, `2!=3`, `3!=4`).
- Prompt `idle` phải có ràng buộc `subtle torso and arm breathing motion` + `no static duplicated frames`.
- Nếu output sai gate, bắt buộc regenerate bằng prompt cứng hơn, không chấp nhận output lỗi.

## References

- Dùng [prompt-templates.md](references/prompt-templates.md) để fill prompt theo đúng `direction` + `state` user yêu cầu.
