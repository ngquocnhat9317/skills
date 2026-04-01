---
name: game-script-writer
description: |
  Viết và cấu trúc kịch bản game: logline, world/character bible, nhiệm vụ (quest),
  hội thoại phân nhánh, cutscene, item lore, tutorial text và nhịp độ kể chuyện.

  Dùng khi người dùng yêu cầu: "viết kịch bản game", "cốt truyện", "hội thoại NPC",
  "quest chain", "dialogue tree", "lore", "nội dung level", "text tutorial".
---

# Game Script Writer (Game Narrative)

## Mục tiêu

Tạo nội dung game rõ ràng, có cấu trúc để triển khai vào code/level: từ ý tưởng → outline → nhiệm vụ → hội thoại → text trong game, kèm format xuất dữ liệu.

## Quy trình

### 1) Thu thập yêu cầu (5 phút)

- Thể loại + tone (hài/horror/phiêu lưu…)
- “Core fantasy” (người chơi được làm gì?)
- Thời lượng mục tiêu (demo 10 phút / game 2 giờ…)
- Mức phân nhánh (tuyến tính / chọn lựa nhẹ / nhiều nhánh)
- Ngôn ngữ (VI/EN), có cần dễ dịch (localization) không

### 2) Viết “1 trang” nền (foundation)

- Logline (1 câu)
- Hook (điểm hấp dẫn trong 10 giây)
- Setting + luật thế giới (3–7 gạch đầu dòng)
- Nhân vật chính/phụ (mục tiêu, điểm yếu, động cơ)

### 3) Outline theo “beats”

- Chia 3 hồi hoặc 5 hồi (tuỳ độ dài), mỗi hồi 3–5 “beat”
- Với game level-based: mỗi level có mục tiêu, biến cố, tutorial mới, và reward

### 4) Nhiệm vụ (quest) & trigger

- Viết quest theo template: xem `references/quest-template.md`
- Rõ điều kiện kích hoạt, điều kiện hoàn thành, và reward

### 5) Hội thoại phân nhánh

- Giới hạn nhánh cho MVP (vd tối đa 2 lựa chọn mỗi lượt, độ sâu 2–3).
- Mỗi câu thoại có “ý định” (thuyết phục/đe doạ/chọc ghẹo…) để giữ giọng nhân vật.
- Khi cần xuất dữ liệu cho code: dùng schema ở `references/dialogue-json.md`.

### 6) Text in-game & localization

- Viết text ngắn, rõ, tránh câu dài trong UI.
- Tạo key ổn định (`tutorial.move`, `npc.bob.greeting`) nếu sẽ dịch nhiều ngôn ngữ.

## Đầu ra đề xuất

- `NARRATIVE.md`: logline + setting + nhân vật.
- `QUESTS.md` hoặc `quests.json`: danh sách quest và trigger.
- `DIALOGUE.md` hoặc `dialogue.json`: hội thoại (theo schema).
- `TEXT_KEYS.csv`: key, vi, en (nếu cần).

## Tham chiếu

- Quest template: `references/quest-template.md`
- Dialogue JSON schema: `references/dialogue-json.md`
