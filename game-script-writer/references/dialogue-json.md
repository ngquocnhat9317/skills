# Dialogue JSON schema (đơn giản, dễ đưa vào code)

## Mục tiêu

- Hội thoại phân nhánh tối thiểu cho MVP.
- Dễ kiểm tra bằng mắt và dễ parse.

## Schema gợi ý

```json
{
  "nodes": [
    {
      "id": "npc_bob_greeting",
      "speaker": "bob",
      "text": "Chào bạn. Bạn cần gì?",
      "choices": [
        { "text": "Tôi cần việc làm.", "to": "npc_bob_job" },
        { "text": "Tạm biệt.", "to": "END" }
      ]
    }
  ]
}
```

## Quy ước

- `id`: duy nhất.
- `speaker`: key nhân vật.
- `text`: string hiển thị (hoặc thay bằng `textKey` nếu dùng localization).
- `choices`: mảng lựa chọn; nếu rỗng thì coi là kết thúc node.
- Thêm `conditions` / `effects` khi cần:
  - `conditions`: yêu cầu flag/item
  - `effects`: set flag, give item, start quest…

