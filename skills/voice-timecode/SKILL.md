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

## Bước 2 — Dò mốc thời gian

**Timestamp KHÔNG lấy được từ ElevenLabs.** Tool chỉ trả `transcription.text` và
vứt bỏ `start`/`end` của từng từ mà API vốn có; `format_diarized_transcript` cũng
vậy. Đo và xác nhận 2026-09-02. Đừng mất công tìm tham số — không có.

Dùng ffmpeg (nhớ `export PATH="/opt/homebrew/bin:$PATH";` trước):

```
ffmpeg -hide_banner -i <file> -af silencedetect=n=-32dB:d=0.35 -f null - 2>&1 \
  | grep -oE "silence_(start|end): [0-9.]+"
```

Khoảng giữa hai lần lặng là một **đoạn nói**. `d=0.35` là điểm khởi đầu tốt:

- Ra **nhiều đoạn hơn số câu** → có ngắt giữa câu. Nâng `d` lên 0.4–0.5.
- Ra **ít đoạn hơn số câu** → hai câu dính nhau. Hạ `d` xuống 0.25–0.3.
- Thu ồn nền → hạ ngưỡng dB, thử `-38dB` hoặc `-42dB`.

Chỉnh vài lần cho số đoạn gần số câu nhất rồi dừng. **Không bao giờ khớp hoàn hảo** —
đó là bản chất của phương pháp, không phải lỗi cần sửa tiếp.

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

**Timecode chỉ gần đúng, sai số khoảng ±0,5 giây.** Nó suy ra từ khoảng lặng chứ
không phải từ mốc thật của từng từ.

- Đủ tốt: lên khung nội dung, chia đoạn, bảng cảnh quay, cắm marker.
- **Không đủ:** phụ đề chạy theo lời, hay bất cứ thứ gì cần khớp từng chữ.

Nếu người dùng định dùng cho phụ đề, **báo trước**, đừng để họ phát hiện lúc xem lại.

## Ranh giới

Không mở Resolve, không tạo project, không dựng, không render. Muốn dựng thì đó là
việc của `/video` hoặc `youtube-long`.
