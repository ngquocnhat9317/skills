# Mẫu điều khiển cho game pixel iOS

## Chọn 1 mẫu cho MVP

### A) D-pad 4 hướng

- Ưu: rõ ràng, hợp platformer/top-down cổ điển.
- Nhược: ít “analog”.
- Output: vector (dx, dy) ∈ { -1, 0, 1 }.

### B) Joystick ảo

- Ưu: mượt, hợp di chuyển tự do.
- Nhược: dễ che màn hình; cần deadzone.
- Output: vector chuẩn hoá + “magnitude” (0..1).

### C) Swipe / Flick

- Ưu: hợp dash/né/nhảy kiểu arcade.
- Nhược: khó điều khiển chính xác nếu gameplay phức tạp.
- Output: hướng + lực (độ dài swipe).

### D) Tap-to-move

- Ưu: hợp puzzle/ARPG nhịp chậm.
- Nhược: pathfinding/avoid obstacle phức tạp hơn.

## Quy tắc chung

- Luôn có “deadzone” cho joystick.
- Luôn có “input debug overlay” khi test (vector + vị trí touch).
- Tránh multi-touch rối cho MVP: chỉ một ngón di chuyển + một nút hành động.

