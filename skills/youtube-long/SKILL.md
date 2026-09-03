---
name: youtube-long
description: Dựng video YouTube dài (ngang 16:9, nhiều phút) từ folder footage + file thu âm giọng người dùng — tự nhận diện giữa một bản thu dài cần cắt dead air và nhiều clip ghép theo kịch bản, cắm marker theo chương, sinh chapters kèm timecode và tiêu đề/mô tả SEO vào Notion. Dùng khi người dùng nói làm video YouTube, video dài, vlog dài, hướng dẫn dài, hoặc cần chapters/timestamp. KHÔNG dùng cho Reels/TikTok/Shorts dọc — cái đó dùng lệnh /video.
---

# Dựng video YouTube dài

Anh em với lệnh `/video` (short-form dọc). Khác biệt cốt lõi: **ngang 1920x1080,
dài nhiều phút, có chapters, chỉ tiếng Việt.**

## Luật không được phá

1. **Không sửa/transcode/tạo bản sao source media.** File sinh ra chỉ vào
   `<folder>/elevenlabs/` hoặc scratch. Đọc thì thoải mái.
2. **Dựng trong Resolve project MỚI** tên `AI Edits - <tên dự án>`. Kiểm tra
   `project_manager list` trước. Có project sẵn của người dùng cho cùng buổi quay
   thì **không mở, không sửa, không xoá timeline nào trong đó**.
3. **Giọng trên timeline là FILE THU ÂM GỐC.** Skill này **không bao giờ gọi
   `text_to_speech`** — YouTube dài chỉ làm tiếng Việt, không lồng tiếng máy.
   File thu âm thiếu/hỏng thì **dừng hỏi người dùng**, không trám bằng TTS.
4. ElevenLabs ở đây chỉ dùng để *nghe hiểu*: `speech_to_text`, `isolate_audio`.

5. **KHÔNG render, KHÔNG export video.** Việc của skill này là **dựng timeline**,
   dừng ở đó. Không tạo render job, không xuất mp4, không đụng trang Deliver.
   Người dùng tự export khi họ ưng. Ngoại lệ duy nhất: grab still/đọc frame để
   *kiểm tra* — đó là soi hình, không phải giao sản phẩm.

## B0 — Xác định folder

Ưu tiên: đường dẫn người dùng đưa → thư mục đã gán vào phiên (bỏ qua
`/Volumes/Data/davinci-resolve-mcp`, đó là repo code) → nhiều thư mục thì hỏi →
không có gì mới hỏi. **Nói rõ folder đang dùng trước khi chạy.**

## B1 — Kiểm kê và CHỌN ĐƯỜNG

Dùng ffmpeg cho rẻ (xem mục cuối). Một vòng `ffprobe` cho cả folder, không gọi
`media_analysis` từng clip.

Rồi quyết định đi đường nào — **nói rõ chọn đường nào và vì sao**:

- **Đường A — cắt dead air:** có MỘT file thu dài (talking head, screencast,
  podcast) chiếm gần hết thời lượng, các file còn lại là b-roll ngắn.
  → nạp skill `resolve-tighten-recording`.
- **Đường B — ghép theo kịch bản:** nhiều clip rời độ dài tương đương, giọng nói
  nằm ở file audio riêng.
  → làm như `/video` nhưng ngang và dài hơn.
- Mơ hồ → hỏi, đừng đoán.

## B2 — Voice → text

**Nếu người dùng đã chạy `voice-timecode` cho folder này**, trang Notion đã có sẵn
bảng timecode + kịch bản. **Dùng lại, đừng bóc lời và viết kịch bản lại từ đầu** —
tốn API, tốn thời gian, và tạo ra một bản kịch bản thứ hai lệch với bản họ đã duyệt.
Hỏi link Notion, hoặc tìm trang theo tên dự án.

`isolate_audio` trước nếu ồn. `speech_to_text` bật timestamp (cần cho chapters và
text). Lưu `<folder>/elevenlabs/transcript.json`.

Bản thu dài cho ra transcript rất dài. **Đừng đổ cả transcript ra chat** — tóm tắt
theo ý chính kèm timecode, hỏi người dùng có muốn đọc đầy đủ không.

**CHỐT 1:** người dùng duyệt transcript.

## B3 — Kịch bản, chương, SEO

1. Chia nội dung thành **chương** theo ý, không theo đồng hồ. Mỗi chương một ý trọn vẹn.
2. Viết kịch bản/outline tiếng Việt bám sát lời người dùng đã nói. Đây là lời của
   họ, không phải dịp sáng tác lại.
3. **Tiêu đề + mô tả SEO**: 3–5 phương án tiêu đề để người dùng chọn, một đoạn mô tả,
   và tag. Tiêu đề bám từ khoá người dùng thực sự nói, không nhồi từ khoá sáo rỗng.
4. Ghi tất cả vào **một Notion page**: kịch bản, chapters, tiêu đề, mô tả, tag.

### Kịch bản = BẢNG CẢNH QUAY có timestamp, không phải đoạn văn

Kịch bản phải dựng **từ chính giọng nói của người dùng**, chia đoạn theo ý, và mỗi
đoạn có **gợi ý cảnh quay**. Đây mới là thứ giúp họ quản được cảnh; một đoạn văn
liền mạch thì không dùng được vào việc gì.

Mỗi đoạn gồm đủ bốn cột:

| Cột | Nội dung |
|---|---|
| **Timecode** | Vào–ra. **ElevenLabs MCP KHÔNG trả timestamp** (xem cảnh báo dưới) — dò bằng `ffmpeg -af silencedetect` rồi khớp câu vào các đoạn nói |
| **Lời** | Câu thoại nguyên văn người dùng đã nói |
| **Ý** | Đoạn này đang nói gì — một cụm ngắn, dùng làm tên marker |
| **Cảnh quay** | **Quay/dùng cảnh gì cho đoạn này** |

**Timecode:** ưu tiên **REST API** `POST https://api.elevenlabs.io/v1/speech-to-text`
(`model_id=scribe_v1`, `timestamps_granularity=word`) — trả `words[]` có `start`/`end`
thật, không sai số. MCP tool `speech_to_text` vứt bỏ chúng, nên **đừng dùng nó khi cần
mốc thời gian**. Không gọi được REST thì mới dò `ffmpeg -af silencedetect`, và khi đó
sai số ±0,5 giây — đủ cho bảng cảnh quay và marker, **không đủ cho phụ đề**.

Cột "Cảnh quay" viết theo hai kiểu tuỳ tình huống:

- **Folder đã có clip khớp** → ghi tên file cụ thể, vd `C0805.MP4 — cận tay gắn khung`.
- **Chưa có clip nào khớp** → mô tả cảnh **cần quay thêm**, đủ cụ thể để cầm máy đi
  quay: góc máy, chủ thể, hành động. Không viết chung chung kiểu "cảnh minh hoạ".

Gợi ý phải bám **đúng thứ đang được nói tại giây đó**. Nói về cái khung thì gợi cảnh
cái khung, không gợi cảnh toàn phòng cho đẹp.

Độ dài đoạn: **TikTok 3–8 giây** mỗi đoạn, **YouTube 15–40 giây** — ngắn quá thì
bảng vụn không quản được, dài quá thì một đoạn cần nhiều cảnh mà chỉ ghi được một.

Bảng này ghi vào Notion cùng kịch bản, **và** là nguồn cho note của marker — mỗi
marker mang theo gợi ý cảnh của đoạn đó, để mở Resolve ra là thấy ngay phải làm gì.

**CHỐT 2:** duyệt kịch bản + tiêu đề.

## B4 — Dựng timeline

1. Project mới, import footage + file thu âm.
2. Timeline **ngang 1920x1080** (trừ khi người dùng nói khác).
3. Theo đường đã chọn ở B1:
   - **A:** cắt dead air trước bằng `silencedetect`, rồi phủ b-roll lên V2 bằng
     `AppendToTimeline` với `clipInfo` có `trackIndex` + `recordFrame`.
     (Cả clip media lẫn title đều đặt được lên track chỉ định — xem công thức dưới.)
   - **B:** chọn shot khớp từng đoạn lời, cắt gapless.
4. **File thu âm gốc** lên track audio, làm xương sống timing.
5. **Marker mỗi chương** tại frame bắt đầu: tên marker = tên chương, note = ý chính,
   màu phân loại. Timecode lấy từ `speech_to_text`, **không ước lượng tay**.
   Sửa marker khiến Resolve tự archive timeline — dọn `_archived_vNN` sau khi xong.
7. **Kiểm bằng frame thật** trước khi báo xong. Không kết luận từ metadata.

## Chapters cho phần mô tả YouTube

Xuất danh sách dán thẳng vào mô tả, dạng `0:00 Tên chương`. Luật YouTube:

- Chương đầu **bắt buộc** là `0:00`.
- Tối thiểu **3 chương**.
- Mỗi chương tối thiểu **10 giây**.

Không đủ điều kiện thì chapters sẽ không hiện — **báo người dùng**, đừng xuất danh
sách hỏng rồi coi như xong.

### Dựng cut: `end_frame` EXCLUSIVE, và dùng `mediaType` khi cần

**Đây là lỗi đã vấp 2026-09-04, người dùng bắt được, phải sửa lại cả timeline.**

`end_frame` trong `create_timeline_from_clips` và `append_to_timeline` là
**EXCLUSIVE**. Muốn clip dài N frame từ source S thì truyền `end_frame = S + N`.
Truyền `S + N - 1` thì clip **ngắn đi 1 frame**, nhưng `record_frame` vẫn được tôn
trọng nguyên — kết quả là **một khoảng trống 1 frame ở MỌI điểm cắt**, và lệnh vẫn
báo `success: true`.

**Luôn chạy `timeline detect_gaps_overlaps` sau khi dựng xong.** `gap_count: 0` trên
V1 mới là dựng đúng. Gap trên track text thì bình thường — caption vốn rời nhau.

**`mediaType` khi track audio đã có sẵn item:** clip Video+Audio append vào V1 sẽ
kéo theo audio, và nếu A1 đang bận thì cả lệnh **thất bại** với
`missing timeline item at index 0` — thông báo không hề nói tới audio. Chỉ cần hình
thì truyền **`mediaType: 1`**. Chỉ cần tiếng thì `mediaType: 2`.

**Tiếng máy quay:** cut này dùng VO riêng nên tiếng camera là rác — **xoá hẳn khỏi
A1**, đừng chỉ tắt track. Tắt track còn làm hỏng lệnh append sau đó.

## Text động trên timeline — CÔNG THỨC ĐÃ CHỨNG MINH (2026-09-02)

### Caption phải HIỆN XONG đúng lúc từ khoá tới — không phải bắt đầu ở đó

**Chốt 2026-09-04, sau hai lần đặt sai liên tiếp.**

Caption cần thời gian để hiện. Chữ chạy stagger từng ký tự nên mất
**≈ số ký tự × `Delay` + ramp**. Với `Delay 1` và ramp mặc định 20 thì một caption
20 ký tự mất **40 frame** mới hiện đủ.

Neo vào lúc từ khoá bắt đầu là **muộn** — khi lời tới, chữ mới hiện được một phần.
Người xem nghe xong rồi mà mắt vẫn thấy chữ đang bò ra.

**Thời gian chữ hiện xong: ĐO, đừng tính.** Công thức "số ký tự + ramp" tôi suy ra
là **sai gần gấp đôi**. Đo thật 2026-09-04 trên preset `Word Slide Up + Fade`,
`Delay 1`, caption 21 ký tự: đặt ở frame 240, chụp frame 258 chữ còn đang mờ vào,
frame 265 đã đủ → **hiện xong sau ~23 frame**, không phải 41.

Xấp xỉ dùng được: **anim ≈ số ký tự + 3** với ramp mặc định.

Nhưng preset khác nhau chạy khác nhau. Cách đúng: đặt caption đầu tiên, **chụp hai
frame để tìm chỗ chữ vừa hiện đủ**, lấy số đó làm `anim` cho cả bài. Một lần đo
thay cho bốn lần đoán.

**Công thức:**

```
frame_đặt = frame_từ_khoá − (số_ký_tự × Delay + ramp)
```

Đo thật trên cut tranhtreotuong:

| Caption | Ký tự | Hiện xong sau | Từ khoá ở frame | Đặt ở |
|---|---|---|---|---|
| Tạo hình bằng ChatGPT | 21 | 41f | 281 | 240 |
| Giá treo cố định | 16 | 36f | 509 | 473 |
| Băng keo Nano 2 mặt | 19 | 39f | 556 | 517 |
| Thử cho góc của bạn | 19 | 27f (ramp 8) | 731 | 704 |

Người dùng tự kéo caption 2 về **478** trước khi tôi tính ra **473** — hai con số gần
trùng, đó là xác nhận công thức đúng.

**Độ dài caption:** giữ trên hình tới hết cụm từ + khoảng 15 frame. Lấy `end` của từ
cuối trong cụm từ `words[]`.

**Khi hai cụm từ khoá quá gần nhau:** đoạn "giá treo / băng keo Nano" có hai cụm cách
nhau 47 frame trong khi mỗi caption cần 36–39 frame để hiện. Không đủ chỗ cho cả hai
chạy trọn — phải **nén ramp xuống 8** hoặc chấp nhận caption trước tắt sớm. Đừng để
chúng chồng lên nhau: hai item trên cùng một track là lỗi.

**Tự kiểm:** `frame_đặt + thời_gian_hiện ≤ frame_từ_khoá`. Vi phạm là caption muộn.

#### Mỗi caption PHẢI có một tiếng động đi kèm

**Chốt 2026-09-04.** Có `text` là **tự động có SFX cho từng caption** — không cần cờ
`sfx` riêng. Chữ hiện lên câm là thiếu, không phải là tối giản.

- **Một SFX cho mỗi caption**, đặt ở **đúng frame caption bắt đầu** (lúc chữ bắt đầu
  chạy, không phải lúc chữ hiện xong).
- Đặt xuống **một track audio riêng** — không trộn với VO hay tiếng source.
- **Dùng nguyên độ dài file, không cắt** (xem mục Nhạc & SFX).
- Loại tiếng: `pop` / `whoosh` / `tick` ngắn cho caption thường; caption CTA hoặc câu
  chốt thì được dùng tiếng dày hơn.
- **Không dùng cùng một file cho mọi caption** — nghe ra ngay là lặp. Xoay vòng như
  xoay vòng preset chữ.

Nguồn: `SearchSoundEffects` của Epidemic trước; kho `~/Downloads` của người dùng
(`whoosh-*`, `pop_*`, `*-riser-*`) dùng được, nhưng **phải nói rõ trong báo cáo lấy
từ đâu**.

## Hiệu ứng text: DÙNG PRESET DỰNG SẴN, đừng tự keyframe

Resolve có **113 title template dựng sẵn** trong
`/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Resources/Fusion/Templates/Templates.drfx`
(file .drfx là zip, `unzip -l` để liệt kê). Chúng đã có sẵn stagger từng ký tự,
easing chuyên nghiệp, BezierSpline — làm tay không lại được, và nhanh hơn nhiều.

**Cách dùng: y hệt công thức Text+, chỉ đổi tên ở bước 2.**
`timeline insert_fusion_title` với tên preset thay vì `"Text+"`.

**Bẫy phải tránh:** tool chứa chữ **đổi tên theo từng preset** — `Rise Fade` dùng
`upperText`, `Word Highlight` dùng `Template`. **Luôn `get_tool_list` trước**, rồi
mới `set_input` vào đúng tool TextPlus. Set nhầm tên là lệnh trôi vào hư không mà
vẫn báo thành công.

Tên truyền vào là **tên lá, bỏ đường dẫn thư mục**: `"Word Highlight"`, không phải
`"Subtitles/Animated/Word Highlight"`.

**Hai loại preset, đừng nhầm:**

- **Title preset** (`Rise Fade`, `Scale Up`, `Drop In`…) — chuyển động nằm sẵn
  trong comp, insert vào là chạy ngay. Đây là loại dùng cho text trên timeline.
- **Subtitle preset** (nhóm `Subtitles/…`, gồm `Word Highlight`) — chỉ là **kiểu
  trang trí cho track phụ đề**. Insert như title thì nó hiện ra đẹp nhưng **đứng
  im**. Đã đo 2026-09-02: keyframe `Input31` ("Write On Words") trên MacroTool1
  không làm nó chạy; chuyển động của nhóm này do **subtitle track** điều khiển,
  không phải do title item. Muốn dùng thì phải tạo phụ đề trên subtitle track rồi
  áp preset, không phải insert làm title.

Đây đúng là lý do luật "chứng minh bằng 2 frame" tồn tại: preset hiện ra đẹp,
readback sạch, mà vẫn bất động.

### Nguồn preset ƯU TIÊN: "Preset Manager" (đã cài 2026-09-02)

Preset mặc định của Resolve **người dùng chê xấu** — chỉ dùng khi không còn gì khác.
Ưu tiên theo thứ tự này:

1. **`Preset Manager` — 53 preset, đây là nguồn chính.** Tên preset tự mô tả theo
   công thức `[Tầng] + [Chuyển động] + [Biến thể]`:
   - Tầng: **`Letter`** (từng ký tự) · **`Word`** (từng từ) · không tiền tố (cả khối)
   - Chuyển động: `Slide Up/Down/Left/Right`, `Scale In/Out`, `Rotate`, `Fade`, `Flicker`
   - Biến thể: `+ Fade`, `+ Blur`, `+ Bounce`
   Ví dụ có thật: `Word Slide Up + Fade`, `Letter Scale In Bounce`,
   `Letter Slide Down + Blur`, `Fade + Blur`, `Word Fade In`, `Letter Rotate`.
   **Tool chữ: `Template`** (có thêm `Instance_Template` — set vào `Template`).
   Đã test: `Word Slide Up + Fade` → frame 8 hiện "Tự làm", frame 16 "Tự làm tranh".
   Stagger theo từ, nền trong suốt. Đây là mặc định nên dùng.
2. **`Text Elite Presets 01` … `20`** — 20 preset, khi cần kiểu khác.
3. **`AkittPro_Presets`** — 257 title + 32 effect, kho dự phòng rất lớn.
4. Preset gốc của Resolve (`Rise Fade`, `Center Reveal`…) — **chỉ khi hết cách**.

Người dùng còn vài preset tự lưu ở gốc thư mục Titles: `elite-1`, `Rise`,
`text-effect-*`. Lưu ý `Rise` chỉ có MediaIn→MediaOut, **không chứa tool chữ nào** —
đừng dùng cho text.

Chọn "không trùng nhau" giờ dễ: xoay vòng trong 53 cái của Preset Manager, đổi tầng
(Letter/Word/khối) trước rồi mới đổi hướng.

Thư mục cài: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Titles/`.
Resolve nhận preset mới **không cần khởi động lại**.

## Màu — CHỈ khi người dùng gọi tên look

**MẶC ĐỊNH KHÔNG GRADE.** Không gõ gì về màu thì **không đụng vào màu** — clip để
nguyên như quay. Chỉ áp look khi người dùng gọi tên: `lấy 1.5.1`, `lấy 1.4.2`,
`lấy Iphone 1.2.1`.

Người dùng ra lệnh theo kiểu **"lấy 1.5.1"** — nghĩa là still nhãn `1.5.1` trong
**PowerGrade album `Sony`** (Gallery của họ có 3 album: `Iphone`, `Sony`, `DJI`;
chọn album theo máy quay của footage).

### Lấy PowerGrade theo số — CÔNG THỨC ĐÃ CHẠY THẬT (2026-09-02)

**Nhãn still gần như để trống** (chỉ 1/5 cái có nhãn "Final"), nên `get_label`
KHÔNG tìm được "1.5.1". Số đó chỉ hiện ra trong **tên file khi export**.

1. `gallery_stills export_stills` với `album_type: "power_grade"`,
   `album_name: "Sony"`, `format: "drx"`, `folder_path` là thư mục scratch.
   Thư mục **phải tồn tại sẵn** — chưa có thì `mkdir -p` trước, không thì trả
   `success: false` không kèm lý do.
2. Đọc tên file: chúng ra dạng `<prefix>_1.1.1.drx`, `<prefix>_1.5.1.drx`…
   **Khớp đúng con số người dùng gọi.**
3. `timeline_item_color add_version` (tham số tên là **`name`**, không phải
   `version_name`) — tạo version mới TRƯỚC KHI áp.
4. `timeline_item_color safe_apply_drx` với đường dẫn file khớp. Gọi lần đầu trả
   `confirm_token`, gọi lại kèm token mới chạy.

**BẮT BUỘC tạo grade version mới trước.** `safe_apply_drx` **thay thế TOÀN BỘ
graph** của clip, không có chế độ chèn thêm — áp thẳng là xoá sạch grade người dùng
đã làm trên clip đó.

**Đừng đoán index theo thứ tự.** Số của album Sony là `1.1.1`, `1.1.2`, `1.43.1`,
`1.5.1`, `1.9.1` — **không tuần tự**. Đoán "1.5.1 là cái thứ 5" sẽ lấy nhầm sang
`1.9.1`. Luôn export rồi khớp theo tên file.

**Khâu đo cần một thao tác tay của người dùng:** `grab_and_export` đòi **panel
Gallery đang mở** trên trang Color (Workspace > Gallery). `resolve_control open_page`
chuyển được sang trang Color nhưng **không mở được panel**. Chưa mở thì báo người
dùng mở, đừng thử lại vòng vòng.

### Áp grade — chỉ vậy thôi, không tự cân sáng

Áp look rồi dừng. **Không đo, không chỉnh node `WB`/`EXP`, không vòng lặp cân sáng.**
Người dùng đã bỏ tính năng đó ngày 2026-09-02 vì rườm rà so với giá trị nó mang lại.
Muốn tinh chỉnh thì họ tự làm trong Resolve — đó là phần việc họ thích tự tay.

Nếu sau này ai định thêm lại vòng đo tự động: **hỏi trước**, đừng tự ý.

## Cấu hình timeline

Người dùng dựng ở Full HD 30fps. Phần xuất file là việc của họ — xem mục dưới.

### Timeline: 1920 × 1080, 30 fps

Đặt qua `project_settings` **NGAY khi tạo project, TRƯỚC khi import clip nào**:

| Key | Giá trị |
|---|---|
| `timelineResolutionWidth` | `1920` |
| `timelineResolutionHeight` | `1080` |
| `timelineFrameRate` | `30` |
| `timelinePlaybackFrameRate` | `30` |

**Đổi fps sau khi timeline đã có clip là hỏng** — mọi điểm cắt và marker lệch hết
so với VO. Sai thứ tự thì dựng lại, không chữa được.

### KHÔNG đụng vào Deliver

Không đặt render settings, **không tạo render job**, không mở trang Deliver. Người
dùng bỏ bước này ngày 2026-09-02. Việc kết thúc ở timeline.

Thông số họ dùng khi tự xuất (chỉ để tham khảo nếu được hỏi, không tự áp):
4K **3840×2160**, `VideoQuality` 20000.

## `broll` — một bản quay dài, đánh dấu chỗ chèn B-roll

Người dùng quay **MỘT video dài nói liên tục**. Việc duy nhất: **đánh dấu những đoạn
nên đè B-roll**. Không cắt, không bỏ hình, không tách tiếng — bản quay để nguyên vẹn
trên timeline. Họ tự chèn B-roll sau.

Kích hoạt: `broll`, hoặc người dùng nói "đánh dấu chỗ chèn B-roll", "chừa chỗ B-roll".

**Độ dài chuẩn:** TikTok **30–45 giây** · YouTube **4–10 phút**. Không hỏi lại.

### Chọn đoạn nào cần B-roll

Đọc transcript kèm timestamp, phân loại từng câu:

| Giữ mặt người nói | Đè B-roll |
|---|---|
| Nói thẳng với khán giả, chào, chốt ý | **Mô tả một vật, một thao tác** ("cái này mình dùng…") |
| Câu có cảm xúc, biểu cảm mặt mang thông tin | Liệt kê, kể số liệu, nói về nơi chốn |
| Hook mở đầu và CTA cuối | Đoạn nói dài trên 8–10 giây không đổi ý |

Nguyên tắc: **B-roll phải minh hoạ đúng thứ đang được nói tại giây đó.** Không đánh
dấu chỉ vì đoạn đó dài. Nghĩ không ra cảnh hợp thì bỏ qua — hình tĩnh còn hơn hình
lạc đề. Đoạn ngắn dưới 1,5 giây thì bỏ, chớp một cái là hết.

### Đánh dấu

Đặt nguyên bản quay lên timeline, **không cắt một nhát nào**. Rồi mỗi đoạn B-roll
cắm **một marker có `duration`** — nó trải thành thanh ngang đúng khoảng cần chèn,
nhìn phát thấy cả điểm vào lẫn điểm ra:

- `frame` = frame bắt đầu đoạn
- `duration` = độ dài đoạn (frame)
- `name` = `BROLL 01`, `BROLL 02`… đánh số theo thứ tự thời gian
- `note` = **mô tả cảnh cần quay/chèn**, viết cho người đọc, lấy từ chính câu nói
  tại giây đó
- `color` = một màu riêng, khác màu marker chương, để phân biệt trong nháy mắt

Timecode lấy từ `speech_to_text`, **không ước lượng bằng tay**.

Lưu ý: sửa marker khiến Resolve tự archive timeline — dọn các `_archived_vNN` sau khi xong.

### Báo cáo cuối

Ngoài project/timeline, đưa **bảng danh sách khoảng chèn**: số thứ tự, timecode
vào–ra, độ dài, và cảnh B-roll đề xuất. Đây mới là thứ người dùng cầm đi quay.

## Mặc định: KHÔNG nhạc, KHÔNG text

**Chỉ thêm khi người dùng gọi tên.** Không tự ý thêm nhạc hay chữ vì thấy "video
nên có". Thêm thừa thì người dùng phải vào Resolve xoá tay, tốn công hơn nhiều so
với việc họ gõ thêm một từ.

| Từ khoá | Thêm gì |
|---|---|
| `text` | Text động trên timeline — **chỉ ở đoạn có sản phẩm, thông số, hoặc điểm nhấn**. Kéo theo **một SFX cho mỗi caption**, tự động |
| `music` | Nhạc nền từ Epidemic Sound — gửi 2–3 link nghe thử, người dùng chọn |
| `music-auto` | Nhạc nền, tự chọn bài hợp gu, khỏi gửi preview |
| `sfx` | Tiếng động điểm nhấn |

Nói tự nhiên cũng nhận: "thêm nhạc", "có text nhé", "thêm tiếng động".

`no-text` / `no-music` vẫn hiểu được nhưng **thừa** — đó đã là mặc định rồi.

**Marker luôn được cắm**, không phụ thuộc option nào. Marker là bản đồ điều hướng
trong timeline, không phải chữ hiện trên hình — có nó thì người dùng tự thêm text
sau cũng dễ.

Báo cáo cuối liệt kê rõ đã thêm gì và **không thêm gì**, để không ai tưởng là làm thiếu.

## Nhạc & SFX — Epidemic Sound

**Nhạc và SFX là opt-in** — xem mục "Mặc định: KHÔNG nhạc, KHÔNG text".
Không có `music` / `music-auto` / `sfx` thì **bỏ qua toàn bộ mục này**,
không search, không tải, không đụng server Epidemic.

**Nhạc nền: bắt buộc Epidemic.** Không dùng `compose_music` của ElevenLabs — nhạc
Epidemic có license đầy đủ cho YouTube và Instagram, nhạc AI sinh ra thì không.

**SFX: ưu tiên Epidemic, nhưng được dùng file có sẵn của người dùng** (chốt
2026-09-02). Tìm `SearchSoundEffects` trước; nếu trong máy đã có file hợp hơn thì
dùng, và **nói rõ trong báo cáo là lấy từ đâu** — đừng im lặng đổi nguồn.

Kho SFX của người dùng nằm rải trong **`~/Downloads`** — không phải thư mục được
sắp xếp, chỉ là chỗ đọng lại: `whoosh-*`, `pop_*`, `*-riser-*`, `error_*`,
`duolingo-wrong`… Trộn lẫn với bản render VO ElevenLabs và audio tải từ mạng, nên
**nghe/`ffprobe` kiểm trước khi đặt lên timeline**, đừng tin mỗi cái tên file.

Họ dùng file SFX **nguyên độ dài, không cắt** (riser 2,76s ở bản EN
`tranhtreotuong`) — đừng tự trim SFX cho "vừa khít" trừ khi được bảo.

**Tên tool thật** (đã xác minh bằng gọi thật, khác tên trong tài liệu):
`SearchRecordings` (nhạc), `SearchSoundEffects` (SFX),
`SearchSimilarToRecording`, `SearchSimilarToSoundEffect`,
`EditRecording` + `PollEditRecordingJob` (cắt nhạc theo độ dài),
`DownloadRecording`, `DownloadRecordingEdit`, `DownloadSoundEffect`.

Quy trình:

1. `SearchRecordings` với `query.term` theo mood lấy từ kịch bản, kèm
   `filter.duration` (mili-giây) khớp độ dài video. `first: 3-5` thôi — kết quả rất
   dài, tốn token.
2. **Đưa người dùng nghe trước rồi mới tải.** Mỗi kết quả có `audioFile.lqmp3Url`
   là bản preview — gửi 2–3 link cho họ chọn. Trừ khi có `music-auto`.
3. Nhạc dài hơn video thì dùng `EditRecording` + `PollEditRecordingJob` để cắt đúng
   độ dài, rồi `DownloadRecordingEdit`. Đừng cắt thô bằng ffmpeg — bản edit chính
   thức giữ được cấu trúc bài, kết bài không bị cụt.
4. Tải về `<folder>/music/` — thư mục mới, **không ghi vào chỗ để footage gốc**.
5. Import vào media pool, đặt xuống **track audio riêng**, không trộn với track VO.
6. **Nhạc phải chìm dưới giọng nói.** Gain nhạc thấp hẳn so với VO, kiểm bằng
   `ebur128` chứ không nghe áng chừng.
7. SFX đặt đúng frame sự kiện, timecode lấy từ marker/transcript.

Chỉ tải khi người dùng đã chọn — mỗi lượt tải tính vào tài khoản của họ.

**Gu nhạc: GÂY TÒ MÒ + HÀO HỨNG.** Ghép một vế tò mò (`curious`, `mysterious`,
`suspense`, `quirky`) với một vế hào hứng (`energetic`, `driving`, `upbeat`,
`euphoric`, `build up`). `filter.bpm` **110–140**. `filter.vocals: false` **luôn
luôn** — nhạc có lời cãi nhau với giọng tiếng Việt. Mood tag có thật đã kiểm chứng:
`suspense`, `dark`, `happy`, `hopeful`, `euphoric`.

Track có `stems` (BASS/MELODY/INSTRUMENTS/VOCALS) — nhạc cãi giọng nói thì dùng stem
instrumental thay vì hạ gain cả bài.

## Dùng ffmpeg để đỡ tốn token

ffmpeg/ffprobe 9.0.1 ở `/opt/homebrew/bin/` nhưng **không có trong PATH của Bash
tool** — mở đầu lệnh bằng `export PATH="/opt/homebrew/bin:$PATH";`. MCP server tự lo.

- Kiểm kê: một vòng `ffprobe -v error -show_entries format=duration:stream=width,height,codec_type -of json` cho cả folder.
- Xem hình: **contact sheet** `-vf "fps=1/2,scale=320:-1,tile=4x4"` rồi đọc MỘT ảnh,
  thay vì đọc hàng chục frame rời. Đây là khoản tiết kiệm lớn nhất.
- Dead air / điểm cắt: `-af silencedetect=n=-35dB:d=0.4` rồi đọc log.
- Âm lượng: `-af ebur128`.

**Build này KHÔNG có `drawtext`, `subtitles`, `ass`** — đừng định burn text bằng
ffmpeg. Có: `silencedetect`, `ebur128`, `tile`, `thumbnail`, `scale`, `crop`,
`select`, `fps`, `loudnorm`, `atrim`, `volumedetect`.

ffmpeg ở đây chỉ để **ĐỌC**. Không transcode, không ghi đè source.

## Báo cáo cuối

Nêu rõ: project + timeline đã tạo, link Notion, file đã sinh, và **những gì KHÔNG
làm** (không grade / không text / không nhạc / không render) để không ai tưởng là
làm thiếu. Bước nào bị bỏ vì vướng thì nói thẳng lý do — đừng báo hoàn thành khi
mới xong một nửa.
