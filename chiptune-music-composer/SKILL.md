---
name: chiptune-music-composer
description: |
  Sáng tác nhạc phong cách chiptune/8-bit cho game: loop background,
  jingle ngắn, và bộ SFX (jump, hit, pickup, UI click...) kèm spec triển khai.

  Dùng khi người dùng yêu cầu: "viết nhạc 8-bit", "chiptune", "nhạc game pixel",
  "SFX", "jingle", "theme", "tempo/loop", "sound design".
---

# Chiptune Music Composer

## Mục tiêu

Tạo “music spec” đủ rõ để người làm nhạc (hoặc bạn) có thể dựng trong tracker/DAW, và đủ gọn để dev tích hợp (loop points, BPM, key, stem/track nếu có).

## Quy trình

### 1) Chốt mood & ràng buộc kỹ thuật

- Mood: vui/căng thẳng/bí ẩn…
- Tempo (BPM), nhịp (4/4 thường đủ), key.
- Loop length: 8 hoặc 16 bar cho MVP.
- “Âm sắc” giả lập: pulse/triangle/noise (tư duy kiểu chip).

### 2) Viết theme (hook) 1–2 ô nhịp

- Một motif dễ nhớ (4–8 nốt) lặp/biến tấu.
- Đảm bảo không “lèo lái” quá nhiều nốt, ưu tiên giai điệu rõ.

### 3) Dựng vòng lặp (arrangement)

- A (bars 1–4): theme + bass đơn
- B (bars 5–8): biến tấu + fill
- Nếu 16 bar: A (1–8), B (9–16) + turnaround về bar 1

### 4) Danh sách SFX theo gameplay

- Tạo bảng SFX: event → mô tả → độ dài (ms) → cao độ tương đối.
- Đọc gợi ý: `references/sfx-catalog.md`.

## Đầu ra đề xuất

- `AUDIO-SPEC.md`:
  - BPM, key, loop bars, mood keywords
  - cấu trúc track (lead/bass/percussion)
  - danh sách SFX
- Nếu cần bàn giao cho dev:
  - loop start/end rõ ràng
  - tên file thống nhất (`bgm_stage1_loop`, `sfx_jump_01`…)

## Tham chiếu

- Loop templates: `references/loop-templates.md`
- SFX catalog: `references/sfx-catalog.md`
