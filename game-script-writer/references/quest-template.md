# Quest template (MVP-friendly)

## 1 quest = 1 “đơn vị triển khai”

- Ít mơ hồ, có điều kiện rõ để code trigger.
- Một quest nên hoàn thành trong 1–5 phút (tuỳ game).

## Mẫu

```yaml
id: quest_find_key_01
title: "Chìa khoá gỉ"
giver: npc_blacksmith

start:
  trigger: on_talk
  target: npc_blacksmith
  prerequisites:
    - flag.intro_done == true

steps:
  - id: step_get_key
    objective: "Tìm chìa khoá trong kho."
    completion:
      trigger: on_pickup
      item: item_rusty_key

finish:
  trigger: on_talk
  target: npc_blacksmith
  reward:
    - item: item_coin
      amount: 50
    - flag: flag_has_shop_access
      set: true
```

## Quy ước

- `id` ổn định, không đổi khi dịch ngôn ngữ.
- `trigger` là event mà code có thể phát ra (talk, pickup, enter_area, kill…).
- Dùng `flag.*` để lưu tiến trình.

