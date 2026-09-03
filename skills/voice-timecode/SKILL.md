---
name: voice-timecode
description: Bóc lời từ file thu âm thành bảng timecode rồi viết kịch bản vào Notion. Đây là bước B1+B2 của quy trình dựng video — chạy riêng được, và /video hay youtube-long dùng lại kết quả thay vì làm lại. Dùng khi người dùng muốn bóc lời kèm mốc thời gian, lên khung nội dung, chia đoạn quản cảnh quay, hoặc chuẩn bị kịch bản trước khi dựng. KHÔNG dựng phim, không đụng DaVinci Resolve.
---

# Voice → bảng timecode → Notion

**Đây là B1 + B2 của quy trình dựng video, tách ra chạy riêng.** File thu âm vào →
bảng timecode → kịch bản nằm trong Notion. Không mở Resolve, không dựng.

`/video` và `youtube-long` **dùng lại trang Notion này** thay vì bóc lời lại từ đầu.
Chạy skill này trước rồi mới dựng là cách tiết kiệm nhất: duyệt kịch bản xong xuôi
mới đụng tới Resolve.

## Đầu vào

Người dùng đưa file (`.mov`, `.mp4`, `.m4a`, `.wav`, `.mp3`) hoặc một thư mục.

Nếu là thư mục: tìm file thu âm — thường là file audio-only, hoặc file tên
`voice.*`, hoặc clip dài bất thường so với phần còn lại. **Nhiều ứng viên thì hỏi,
đừng đoán.** Nói rõ đang dùng file nào trước khi chạy.

## Bước 1 — Bóc lời

`speech_to_text` của ElevenLabs, `language_code` theo ngôn ngữ thật của file.

## Bước 2 — Lấy mốc thời gian

**Ưu tiên REST API — nó trả timestamp THẬT của từng từ.** MCP tool `speech_to_text`
vứt bỏ `start`/`end`, nhưng endpoint gốc thì giữ:

```
POST https://api.elevenlabs.io/v1/speech-to-text
multipart, model_id=scribe_v1, language_code=vie, timestamps_granularity=word
```

Trả về mảng `words[]`, mỗi từ có `start` và `end`. Đo 2026-09-02: 153 từ trong
31,54 giây, chia sạch thành 12 câu với điểm vào–ra chính xác. **Không sai số.**

Key đọc lúc chạy từ `mcpServers.elevenlabs.env.ELEVENLABS_API_KEY` trong
`/Volumes/Data/davinci-resolve-mcp/.mcp.json` — cùng nguồn `en-vo.py` dùng.

### Chỉ khi không gọi được REST: dò khoảng lặng

```
ffmpeg -hide_banner -i <file> -af silencedetect=n=-32dB:d=0.35 -f null - 2>&1 \
  | grep -oE "silence_(start|end): [0-9.]+"
```

Khoảng giữa hai lần lặng là một đoạn nói. Chỉnh `d`: ra nhiều đoạn hơn số câu thì
nâng lên 0.4–0.5, ít hơn thì hạ xuống 0.25–0.3. Thu ồn thì hạ ngưỡng dB.

**Đường này sai số ±0,5 giây** vì mốc suy từ khoảng lặng chứ không phải từ từng từ.
Đủ cho bảng cảnh quay và marker, **không đủ cho phụ đề**. Dùng REST thì hết vấn đề này.

## Bước 3 — Gán câu vào đoạn

Tách transcript theo câu. Gán vào các đoạn nói theo thứ tự, dùng **độ dài câu** làm
căn cứ khi số lượng lệch nhau: câu dài nhất nhận đoạn dài nhất.

## Bước 4 — Bảng kết quả

| Cột | Nội dung |
|---|---|
| **#** | Số thứ tự |
| **Timecode** | `mm:ss.d` vào–ra |
| **Thời lượng** | Giây |
| **Lời** | Câu nguyên văn |
| **Ý** | Cụm ngắn tóm ý đoạn đó |

Người dùng nói **"kèm cảnh quay"** thì thêm cột gợi ý cảnh: có clip khớp trong thư
mục thì ghi tên file, chưa có thì mô tả cảnh cần quay đủ cụ thể để cầm máy đi làm —
góc máy, chủ thể, hành động. Không viết "cảnh minh hoạ".

Đưa bảng ra cho người dùng xem **trước**, rồi mới ghi Notion.

## Bước 5 — Kịch bản vào Notion

Tạo **một** Notion page, tên theo dự án (lấy từ tên thư mục hoặc nội dung), chứa:

1. **Bảng timecode** ở trên, nguyên vẹn.
2. **Kịch bản** viết từ chính lời người dùng — bám sát ý họ đã nói, chia hook / thân /
   kết. Đây là lời của họ, không phải dịp sáng tác lại.
3. **Ghi chú sai số**: một dòng nói timecode là ±0,5 giây, suy từ khoảng lặng.
4. Nếu có cột cảnh quay: **danh sách cảnh còn thiếu** — những đoạn chưa có clip nào
   khớp. Đây thường là thứ giá trị nhất trên trang, vì nó là việc phải đi quay.

Trả lại **link Notion** cho người dùng.

Lưu thêm bảng ra file cạnh nguồn (`<tên>_timecode.md`) nếu họ muốn giữ bản offline.

## Nói thẳng về sai số

Đi bằng **REST** thì timecode chính xác tới từng từ — dùng cho phụ đề cũng được.

Đi bằng **silencedetect** thì sai số **±0,5 giây**: đủ cho lên khung, chia đoạn và
cắm marker, **không đủ cho phụ đề**. Rơi vào đường này mà người dùng định làm phụ đề
thì **báo trước**.

Báo cáo luôn ghi rõ đã đi đường nào.

## Ranh giới

Không mở Resolve, không tạo project, không dựng, không render. Muốn dựng thì đó là
việc của `/video` hoặc `youtube-long`.
