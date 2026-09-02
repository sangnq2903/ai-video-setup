---
description: Dựng video từ folder chứa footage + file thu âm giọng nói — transcribe, viết kịch bản Notion, dựng cut trong Resolve, rồi xuất bản tiếng Anh cho Instagram.
---

Chạy trọn pipeline "AI Edits My Videos for Me" cho folder người dùng đưa.

`$ARGUMENTS` chứa đường dẫn folder, và có thể kèm: nền tảng (Reels/TikTok/Shorts),
độ dài mong muốn, tông giọng, `text`, `music`, `sfx`, `broll`, `auto`, hoặc `vn-only` / `en-only`.

- Mặc định: **dừng xin duyệt ở 3 chốt** (sau transcript, sau kịch bản, và sau bản
  dịch tiếng Anh — trước khi gửi lên ElevenLabs).
- Có `auto`: bỏ chốt 1 và 2, chạy thẳng, vẫn báo cáo đầy đủ ở cuối.
  **`auto` KHÔNG bỏ được chốt 3** — text tiếng Anh luôn phải được duyệt trước khi
  thành giọng của người dùng.
- **Không có đường dẫn trong `$ARGUMENTS`: đó là bình thường, không phải thiếu sót.**
  Người dùng gán thư mục vào phiên (added directory) thay vì dán path. Tự xác định
  folder theo thứ tự:
  1. Đường dẫn có trong `$ARGUMENTS` (nếu người dùng dán).
  2. Thư mục đã gán vào phiên — lấy working directory **không phải**
     `/Volumes/Data/davinci-resolve-mcp` (repo này là nơi chạy code, không bao giờ
     là folder footage).
  3. Nhiều thư mục gán cùng lúc → liệt kê ra và hỏi dùng cái nào.
  4. Không có gì cả → lúc đó mới hỏi.
  Xác định xong, **nói rõ đang dùng folder nào** trước khi chạy tiếp, để người dùng
  kịp chặn nếu tôi bắt nhầm thư mục.

## Luật không được phá

1. **Không bao giờ sửa/chuyển mã/tạo bản sao của source media.** Mọi file sinh ra
   phải nằm trong `<folder>/elevenlabs/` hoặc scratch. Đọc thì thoải mái.
2. **Dựng trong Resolve project MỚI**, đặt tên `AI Edits - <tên dự án>`. Kiểm tra
   `project_manager list` trước. Nếu đã có project của người dùng cho cùng buổi quay:
   **không mở, không sửa, không xoá timeline nào trong đó.** Bản edit tay của họ là
   mốc so sánh, không phải rác cần dọn.
3. **Bản tiếng Việt = file thu âm GỐC nằm sẵn trong folder.** Không TTS, không
   ngoại lệ. ElevenLabs ở bước này chỉ dùng để *nghe hiểu* (`speech_to_text`,
   `isolate_audio`), tuyệt đối không để *tạo giọng*.
   Nếu file thu âm thiếu, hỏng, hay chỉ có một phần: **dừng lại hỏi người dùng.**
   Không được lấy TTS trám vào chỗ trống — giọng thật của họ là lý do video tồn tại,
   thay bằng giọng máy là làm hỏng sản phẩm chứ không phải cứu nó.
4. **Chỉ bản tiếng Anh mới dùng giọng ElevenLabs** (voice "Sáng"). Đây là lần duy
   nhất trong cả pipeline được gọi `text_to_speech`.

5. **KHÔNG render, KHÔNG export video.** Việc của skill này là **dựng timeline**,
   dừng ở đó. Không tạo render job, không xuất mp4, không đụng trang Deliver.
   Người dùng tự export khi họ ưng. Ngoại lệ duy nhất: grab still/đọc frame để
   *kiểm tra* — đó là soi hình, không phải giao sản phẩm.

## B1 — Kiểm kê folder

Xác định folder theo luật trên, báo tên folder đang dùng, rồi liệt kê nội dung. Tách ra: file video, và file thu âm giọng (thường là audio-only:
.m4a/.wav/.mp3, hoặc clip dài bất thường). Nếu mơ hồ về đâu là file thu âm → hỏi,
đừng đoán. Dùng `media_analysis` để lấy thời lượng, độ phân giải, hướng khung hình.

## B2 — Voice → text

**Nếu người dùng đã chạy `voice-timecode` cho folder này**, trang Notion đã có sẵn
bảng timecode + kịch bản. **Dùng lại, đừng bóc lời và viết kịch bản lại từ đầu** —
tốn API, tốn thời gian, và tạo ra một bản kịch bản thứ hai lệch với bản họ đã duyệt.
Hỏi link Notion, hoặc tìm trang theo tên dự án.

- Nếu file thu âm ồn: chạy `isolate_audio` trước, ghi ra `<folder>/elevenlabs/`.
- `speech_to_text` với timestamp bật (cần cho phụ đề). Tiếng Việt.
- Lưu transcript vào `<folder>/elevenlabs/transcript.json`.
- ElevenLabs base path đã là `/Volumes/Data/share`, nên `output_directory` truyền
  đường dẫn **tương đối** từ đó.

**CHỐT 1:** đưa transcript cho người dùng đọc. Transcript sai mà dựng xong thì phải
làm lại từ đầu. Bỏ qua chốt này nếu có `auto`.

## B3 — Kịch bản + dựng cut

1. Từ transcript, viết kịch bản tiếng Việt: hook, thân, kết. Bám sát ý người dùng
   đã nói — đây là lời của họ, không phải dịp để sáng tác lại.
2. Ghi kịch bản vào Notion (tạo page mới, tên theo dự án).

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

**CẢNH BÁO — timecode chỉ gần đúng (đo 2026-09-02):** tool `speech_to_text` của
ElevenLabs MCP chỉ trả về `transcription.text`, **vứt bỏ `start`/`end` của từng từ**
mà API vốn có. `format_diarized_transcript` cũng vậy. Không có đường nào lấy
timestamp thật.

Đường thay thế đã đo trên `voice.mov` (28,5 giây):
`ffmpeg -af silencedetect=n=-32dB:d=0.35` → ra **9 đoạn nói**, trong khi transcript
có **8 câu**. Gần khớp nhưng **không 1:1** — vài khoảng lặng là ngắt giữa câu, và
`d=0.5` thì gộp quá tay còn 6 đoạn. Việc gán câu vào đoạn phải dùng phán đoán theo
độ dài câu.

Hệ quả: **sai số khoảng ±0,5 giây.**

- Đủ tốt cho **bảng cảnh quay** và **marker** — lệch nửa giây không ảnh hưởng.
- **KHÔNG đủ** cho phụ đề chạy theo lời. Nếu người dùng bật `text` và cần chữ khớp
  từng câu, **nói rõ giới hạn này trước**, đừng để họ phát hiện khi xem lại.

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

**CHỐT 2:** xin duyệt kịch bản. Bỏ qua nếu có `auto`.

3. Tạo Resolve project mới, import footage + file thu âm.
4. Timeline **dọc 1080x1920** (trừ khi người dùng nói khác).
5. Dựng theo kịch bản: chọn shot khớp từng đoạn lời, cắt gapless.
6. Đặt **file thu âm gốc** lên track audio, làm xương sống timing.
7. **Marker theo kịch bản.** Mỗi đoạn trong kịch bản (hook / từng ý / kết) cắm một
   marker ở frame bắt đầu đoạn đó, dùng `timeline_markers`. Tên marker = tên đoạn
   trong kịch bản, note = câu thoại của đoạn. Đổi màu theo loại đoạn để nhìn phát
   ra ngay. Timestamp lấy từ `speech_to_text`, **không ước lượng bằng tay**.
   Lưu ý: sửa marker khiến Resolve tự archive timeline — dọn các timeline
   `_archived_vNN` sau khi xong.
8. **Text trên timeline** (chỉ khi có `text` — xem mục riêng bên dưới).
9. **Kiểm tra bằng frame thật** trước khi tuyên bố xong: render/đọc frame đại diện,
   soi pacing và continuity. Không kết luận từ metadata.

### Hook — cách người dùng tự dựng, học từ bản EN `tranhtreotuong` (2026-09-02)

Tôi dựng hook thành **một shot toàn cảnh giữ 68 frame**. Người dùng vào Resolve dựng
lại toàn bộ. Cấu trúc họ làm, đo trực tiếp từ timeline:

| Frame | Dài | Nội dung |
|---|---|---|
| 0–22 | 22f | `C0784` zoom **1.88** — ba tấm poster nằm trên bàn, cận, đầy khung |
| 22–38 | **16f** | `C0805` — nháy một cái thành phẩm đã treo trên tường |
| 38–68 | 30f | `C0784` zoom 1.88 — quay lại poster |
| 57–79 | 22f | `Blur Dissolve` cưỡi lên điểm cắt f68, sang thân bài |

Rút ra năm điều, áp cho mọi hook short-form:

1. **Mở bằng chính món đồ, cận và đầy khung — không phải toàn cảnh căn phòng.** Chủ đề
   là bộ tranh thì frame đầu tiên phải là bộ tranh. Toàn cảnh để dành cho đoạn bối cảnh.
2. **Hook cắt nhanh, kiểu A–B–A.** 22f → 16f → 30f. Cái 16 frame là một cú *nháy*
   thành phẩm, nửa giây, đủ để tò mò chứ không đủ để xem kỹ. Giữ một shot suốt 68f là
   quá tĩnh cho hook.
3. **Ra khỏi hook bằng transition, không hard cut.** Họ đặt `Blur Dissolve` 22f cưỡi
   lên đúng ranh giới hook → thân.
4. **Có riser SFX chạy dưới hook.** Vào đúng frame nháy (f22), tan sau transition
   (f105) — nghĩa là riser *đưa* người xem sang phần nội dung, không dừng ở hook.
5. **VO có nhịp thở sau câu hook.** Họ cắt VO ở f68 rồi đẩy phần còn lại sang f75 —
   chừa 7 frame im lặng. Đừng đặt VO thành một khối liền từ đầu tới cuối.

Thêm một điều về framing: **cùng một clip có thể mang hai zoom khác nhau tuỳ vai trò.**
`C0784` để zoom 1.88 ở hook (đọc được cả ba tấm poster) nhưng 3.16 ở S5. Đừng copy một
giá trị zoom rồi dùng lại cho mọi lần xuất hiện của clip đó.

**Transition tôi KHÔNG đặt được — đã đo lại 2026-09-02.** Resolve 20.3.3 không có API
transition: `timeline.CreateTransition`, `timeline.AddTransition`, `item.AddTransition`,
`item.GetTransition` đều resolve ra `None` (`'NoneType' object is not callable`).
`dir()` cũng không liệt kê method nào. Nên việc đúng là: **để hard cut, cắm một marker
ngay điểm đó ghi rõ transition đề xuất, và nói trong báo cáo cuối** để người dùng kéo
tay — chứ không im lặng giao một bản thiếu nhịp.

### Text động trên timeline — CÔNG THỨC ĐÃ CHỨNG MINH (2026-09-02)

**Chỉ làm khi có `text`** — mặc định là không thêm chữ. Không có thì bỏ qua toàn bộ mục này.

Chạy thật trên 20.3.3, chứng minh bằng frame render. Không còn là giả thiết.

#### Đặt chữ Ở ĐÂU — chỉ chỗ có sản phẩm, thông số, hoặc điểm nhấn

**Không rải chữ suốt bài.** Có cờ `text` không có nghĩa là mọi đoạn đều được một
caption. Chốt 2026-09-02, sau khi bản EN `tranhtreotuong` dựng 9 caption cho 9 đoạn
và người dùng bắt cắt xuống còn 4.

Đặt caption khi đoạn đó có **một trong ba** thứ:

| Đặt chữ | Ví dụ thật |
|---|---|
| **Tên sản phẩm / công cụ cụ thể** | `Nano double-sided tape`, `Made with ChatGPT` |
| **Thông số, cách làm, con số** | `Fixed wall mount`, `CRI 97 · 1200 lumens` |
| **Điểm nhấn** — hook mạnh, CTA, câu chốt | `Try it yourself` |

Bỏ qua đoạn chỉ **kể chuyện, dẫn dắt, hay tả cảm xúc** — bối cảnh, "kết quả khá ưng
ý", "sau khi hoàn thành đây là góc làm việc". Ở những đoạn đó hình đã nói đủ; đặt chữ
vào chỉ là chép lại lời thoại lên màn hình, người xem đọc một thứ họ đang nghe.

Hệ quả về cách viết chữ: caption **gọi tên món đồ**, không tóm tắt đoạn.
`Nano double-sided tape` chứ không phải `Small: nano tape`; `Made with ChatGPT` chứ
không phải `Asked ChatGPT`.

Tỉ lệ thường thấy: **3–5 caption cho một Reel 25–30 giây.** Nhiều hơn thì gần như
chắc chắn là đang rải chữ. Báo cáo cuối phải nói rõ **giữ mấy cái, bỏ mấy cái, và bỏ
đoạn nào** — để người dùng biết đó là lựa chọn, không phải làm thiếu.

#### Làm THẾ NÀO — công thức 6 bước

**TUYỆT ĐỐI KHÔNG dùng `insert_title`** — nó ripple insert trên V1, đẩy lệch cả cut,
rồi vẫn báo `success: true`.

Mỗi text làm theo đúng 6 bước này:

1. `media_pool create_timeline` → timeline con riêng cho text đó.
2. `timeline insert_fusion_title` với name **`"Text+"`** → rơi V1 của timeline con.
3. `fusion_comp set_input` tool **`Template`**, input `StyledText` → nội dung chữ.
4. `fusion_comp add_keyframe` trên `Template` để tạo hiệu ứng.
   **Thời gian là CLIP-RELATIVE**: time 0 = frame đầu của text, không phải frame
   tuyệt đối của timeline. Input động được: `Size`, `Opacity`, `Transform1Offset`…
5. `timeline get_media_pool_item` (khi timeline con đang là current) → lấy id.
6. `media_pool append_to_timeline` với
   `{media_pool_item_id, start_frame: 0, end_frame: <độ dài-1>, trackIndex: 2,
   recordFrame: <frame muốn đặt>}`.
   **`start_frame`/`end_frame` là BẮT BUỘC** — thiếu là lỗi ngay.

**Chứng minh động:** `timeline_frame capture` hai lần ở hai thời điểm khác nhau
CỦA CÙNG text, đặt `max_width: 400` cho nhẹ. Hai frame phải khác nhau nhìn thấy được.
Làm 1 cái đầu tiên phải chứng minh; các cái sau cùng công thức thì không cần lặp lại.

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

### Timeline: 1080 × 1920, 30 fps

Đặt qua `project_settings` **NGAY khi tạo project, TRƯỚC khi import clip nào**:

| Key | Giá trị |
|---|---|
| `timelineResolutionWidth` | `1080` |
| `timelineResolutionHeight` | `1920` |
| `timelineFrameRate` | `30` |
| `timelinePlaybackFrameRate` | `30` |

**Đổi fps sau khi timeline đã có clip là hỏng** — mọi điểm cắt và marker lệch hết
so với VO. Sai thứ tự thì dựng lại, không chữa được.

### KHÔNG đụng vào Deliver

Không đặt render settings, **không tạo render job**, không mở trang Deliver. Người
dùng bỏ bước này ngày 2026-09-02. Việc kết thúc ở timeline.

Thông số họ dùng khi tự xuất (chỉ để tham khảo nếu được hỏi, không tự áp):
4K **2160×3840**, `VideoQuality` 20000.

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
| `text` | Text động trên timeline (preset + cân tốc độ theo lời nói) — **chỉ đặt ở đoạn có sản phẩm, thông số, hoặc điểm nhấn**, xem mục "Đặt chữ Ở ĐÂU" |
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

## B4 — Bản tiếng Anh cho Instagram

Bỏ qua nếu có `vn-only`. Chạy riêng được bằng `en-only` khi bản Việt đã dựng xong.

1. Dịch kịch bản đã duyệt sang tiếng Anh — dịch cho tự nhiên với người bản xứ,
   không dịch từng chữ.

   **CHỐT 3 — ĐƯA TEXT CHO NGƯỜI DÙNG DUYỆT TRƯỚC KHI GỌI ELEVENLABS.**
   Chốt 2026-09-02. Bắt buộc, **kể cả khi có cờ `auto`** — hai chốt kia bỏ được,
   chốt này thì không.

   In ra **nguyên văn từng dòng sẽ gửi đi**, đánh số theo segment, kèm audio tag
   nếu có. Không tóm tắt, không "đại khái là" — người dùng phải đọc đúng chuỗi ký
   tự sắp thành giọng của họ.

   Lý do: đây là **giọng của họ** nói những câu đó. Dịch sai hay chọn từ lệch chỉ
   lộ ra lúc nghe, mà lúc đó đã tốn quota, và vì tiếng Anh dài ngắn khác tiếng
   Việt nên sửa một câu là phải **dựng lại toàn bộ điểm cắt**. Đọc trước tốn ba
   mươi giây, sửa sau tốn cả lượt dựng.

   Đợi duyệt xong mới sang bước 2.

2. `text_to_speech`, **voice "Sáng" `xYGgUqVrkXAXMWJZtqgF`** — giọng clone của
   chính người dùng, đã có sẵn. **Không clone lại.** Đây là **lần duy nhất**
   trong cả quy trình gọi TTS.

   **Cấu hình hiện hành — "E2", chốt 2026-09-02 sau khi người dùng nghe 13 bản:**

   ```
   model eleven_v3 · stability 0.5 · similarity_boost 0.20 · language_code "en"
   audio tag [British accent] ở MỌI dòng
   ```

   **Đây là bản thay cho `eleven_turbo_v2`.** turbo_v2 sạch accent nhưng người
   dùng chê **không có cảm xúc**. `eleven_v3` mở ra hai thứ turbo_v2 không có:
   `language_code` (ghim phoneme tiếng Anh) và **audio tag** (lấy cảm xúc).

   Ba con số đã đo, đừng đo lại:
   - `language_code` **chỉ nhận `"en"`** — `"en-GB"` bị API trả 400
     *"Model 'eleven_v3' does not support language_code 'en-GB'"*.
   - `stability` của v3 **chỉ nhận 0.0 / 0.5 / 1.0** (Creative / Natural / Robust).
   - `similarity_boost` **0.20, không phải 0.35.** 0.35 vẫn còn accent Ấn. Càng
     hạ càng sạch accent nhưng **càng bớt giống giọng người dùng** — 0.20 là chỗ
     họ chấp nhận. Đừng nâng lên cho "giống hơn", accent quay lại ngay.
   - **v3 đọc chậm hơn turbo_v2 ~20%** (27,9s so với 23,1s cho cùng 10 câu). Đổi
     model là phải dựng lại điểm cắt, không thay mỗi file audio.
   - **v3 không tất định** — cùng text cùng setting, chạy lại ra khác. Câu nào
     nghe hỏng thì roll lại riêng câu đó, đừng dựng lại cả bài.

   **Audio tag:** `[British accent]` gắn mọi dòng, đó là thứ đuổi accent Ấn. Tag
   cảm xúc thì theo đúng luật caption — **chỉ gắn ở câu thật sự có cảm xúc**, dòng
   chỉ dẫn để trơn. Rải tag khắp nơi thì mọi câu đều diễn như nhau, không câu nào
   nổi. **Chỉ dùng tag đã nghe qua** (`[curious]`, `[pleased]`); tag lạ có nguy cơ
   bị đọc thành lời.

   **BẮT BUỘC đọc TỪNG CÂU NGẮN rồi ghép — không được đọc cả đoạn một lần.**
   Dùng `python3 ~/.claude/scripts/en-vo.py <kichban.txt> -o <folder>/elevenlabs/en`
   (mỗi dòng một câu, script tự gọi TTS từng dòng rồi ghép bằng ffmpeg).

   Lý do, đo ngày 2026-09-02: clone "Sáng" chỉ dựng từ 17 giây audio nên nó
   **giữ được giọng khoảng 1-2 giây rồi trôi sang accent Ấn**. Cùng một nội dung,
   cùng cấu hình: đọc liền cả đoạn 9s → người dùng loại; cắt 5 câu 1.0-2.2s rồi
   ghép → người dùng duyệt. Câu dài quá 12 từ là vào vùng hỏng, script sẽ cảnh báo.

   Bảng shot vốn đã chia theo từng ý nên mỗi dòng bảng là một segment — khớp sẵn.

   Nếu gọi tay thay vì dùng script thì **phải truyền đủ setting trong MỖI lần
   gọi** — không được bỏ trống:

   ```
   model_id=eleven_v3  stability=0.5  similarity_boost=0.20  language_code=en
   ```

   Setting lưu làm mặc định của voice trên ElevenLabs **không có tác dụng qua
   API**: MCP tool phớt lờ nó: `elevenlabs_mcp/server.py` khai báo
   `stability=0.5, similarity_boost=0.75, use_speaker_boost=True` làm default
   của hàm và luôn gửi nguyên khối `voice_settings` lên API. Gọi mà không truyền
   tham số là accent quay lại y như cũ. Mặc định lưu trên voice chỉ có tác dụng
   ở web ElevenLabs.

   **Đừng nâng `similarity_boost` hay bật `use_speaker_boost` để giọng "giống
   hơn"** — hai thứ đó kéo accent quay lại.

   Script `en-vo.py` đã mặc định sẵn cấu hình E2, và nhận `--model` /
   `--stability` / `--similarity` / `--language` nếu cần thử lại. Nó tự bỏ
   `language_code` khi model không phải v3 (turbo_v2 không nhận tham số đó), và
   đếm giới hạn 12 từ **sau khi bỏ audio tag**.
3. Xuất ra `<folder>/elevenlabs/en/`.
4. Nhân bản timeline tiếng Việt thành `<tên> - EN`, thay VO bằng file tiếng Anh.
   **Giữ nguyên timeline tiếng Việt.**
5. Timing tiếng Anh sẽ lệch tiếng Việt — chỉnh lại điểm cắt cho khớp VO mới, đừng
   để hình trôi khỏi lời.

Text, nhạc, màu vẫn theo luật opt-in như bản Việt — không tự thêm.

Gói Starter chỉ có 40.000 ký tự/tháng. Kịch bản dài bất thường thì **báo trước khi đọc**.

## Báo cáo cuối

Nêu rõ: project + timeline đã tạo, link Notion, file đã sinh, và **những gì KHÔNG
làm** (không grade / không text / không nhạc / không render) để không ai tưởng là
làm thiếu. Bước nào bị bỏ vì vướng thì nói thẳng lý do — đừng báo hoàn thành khi
mới xong một nửa.
