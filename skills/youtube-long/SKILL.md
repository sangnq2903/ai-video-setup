---
name: youtube-long
description: Dựng video YouTube dài (ngang 16:9, nhiều phút) từ folder footage + file thu âm giọng người dùng — tự nhận diện giữa một bản thu dài cần cắt dead air, nhiều clip ghép theo kịch bản, và trường hợp mới có giọng chưa có hình; lọc bản thu vấp thành danh sách giữ nguyên văn rồi cắt thẳng trên timeline từ media gốc, kiểm chứng thông số người dùng nói, cắm marker theo chương, sinh chapters kèm timecode và tiêu đề/mô tả SEO vào Notion. Dùng khi người dùng nói làm video YouTube, video dài, vlog dài, hướng dẫn dài, cần chapters/timestamp, hoặc cần lọc/cắt một bản thu giọng dài. KHÔNG dùng cho Reels/TikTok/Shorts dọc — cái đó dùng lệnh /video.
---

# Dựng video YouTube dài

Anh em với lệnh `/video` (short-form dọc). Khác biệt cốt lõi: **ngang 1920x1080,
dài nhiều phút, có chapters, chỉ tiếng Việt.**

## Luật không được phá

1. **Không sửa/transcode/tạo bản sao source media.** File sinh ra chỉ vào
   `<folder>/elevenlabs/` hoặc scratch. Đọc thì thoải mái.
   **Hệ quả bắt buộc: mọi cú cắt làm TRÊN TIMELINE, từ media gốc.** Không render
   một file trung gian bằng ffmpeg rồi đặt file đó lên timeline — làm vậy là
   resample, là nướng fade vào file, và là giao cho người dùng một khối phẳng
   không sửa lại được. Đúng cách: nhiều clip trên một track, mỗi clip trỏ vào
   source chưa đụng tới. **Áp cho cả audio lẫn video.** Chốt 2026-09-04 sau khi
   tôi làm sai và bị bắt. Công thức ở mục *Cắt trên timeline từ media gốc*.
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
- **Đường C — CHỈ CÓ GIỌNG, chưa có hình:** trong folder không có clip nào.
  **Đây không phải lý do dừng.** Vẫn làm được, và làm hết:
  bóc lời → bảng cảnh quay (cột "Cảnh quay" khi đó **toàn bộ là cảnh cần quay
  thêm**, viết đủ cụ thể để cầm máy đi quay) → chương + SEO vào Notion →
  timeline chỉ có giọng đã lọc + marker, để mở Resolve ra là thấy phải quay gì ở
  đâu. Nói thẳng cái gì chưa dựng được và vì sao, rồi giao phần còn lại.
- Mơ hồ → hỏi, đừng đoán.

**Nghe kỹ xem trong lời họ có nhắc tới hình không.** Ở cut 17 Pro người dùng nói
*"cái scene mà các bạn đang được xem ở đây"* và *"setup quay ProRes RAW để quay
trực tiếp video này"* — tức là có buổi quay song song ở đâu đó. Hỏi ngay: footage
đó nằm đâu, hay chưa quay. Và cảnh **behind-the-scene / so sánh hai máy phải quay
CÙNG BUỔI** với A-roll, quay bù sau không khớp ánh sáng — đưa lên đầu danh sách.

## B2 — Voice → text

**Nếu người dùng đã chạy `voice-timecode` cho folder này**, trang Notion đã có sẵn
bảng timecode + kịch bản. **Dùng lại, đừng bóc lời và viết kịch bản lại từ đầu** —
tốn API, tốn thời gian, và tạo ra một bản kịch bản thứ hai lệch với bản họ đã duyệt.
Hỏi link Notion, hoặc tìm trang theo tên dự án.

`isolate_audio` trước nếu ồn. `speech_to_text` bật timestamp (cần cho chapters và
text). Lưu `<folder>/elevenlabs/transcript.json`.

**NÉN TRƯỚC KHI UPLOAD.** Bản thu của người dùng có thể rất nặng — đo 2026-09-04:
ALAC 192kHz stereo, **105,7MB cho 25 phút**. ASR không dùng gì trên 16kHz mono, nên
tạo bản nén vứt đi rồi upload bản đó:

```
ffmpeg -v error -y -i <source> -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 32k \
  <folder>/elevenlabs/voice-stt.mp3
```

Ra **6,08MB (nhỏ hơn 17 lần)**, transcript vẫn đủ 4936 từ với timestamp sạch. Người
dùng đã dừng một lần chạy để yêu cầu đúng việc này. Xoá bản nén trung gian bitrate
cao nếu lỡ tạo, đừng để hai file cùng lúc.

Bản thu dài cho ra transcript rất dài. **Đừng đổ cả transcript ra chat** — tóm tắt
theo ý chính kèm timecode, hỏi người dùng có muốn đọc đầy đủ không.

**CHỐT 1:** người dùng duyệt transcript.

## B3 — Kịch bản, chương, SEO

1. Chia nội dung thành **chương** theo ý, không theo đồng hồ. Mỗi chương một ý trọn vẹn.
2. Viết kịch bản/outline tiếng Việt bám sát lời người dùng đã nói. Đây là lời của
   họ, không phải dịp sáng tác lại.
3. **Tiêu đề + mô tả SEO**: 3–5 phương án tiêu đề để người dùng chọn, một đoạn mô tả,
   và tag. Tiêu đề bám từ khoá người dùng thực sự nói, không nhồi từ khoá sáo rỗng.
4. **KIỂM CHỨNG MỌI CON SỐ NGƯỜI DÙNG NÓI.** Video review nào cũng đầy thông số, và
   người nói giữa chừng rất dễ lấy nhầm số của đời máy trước. Tra nguồn hãng, dẫn
   link vào Notion, và **ghi cảnh báo ngay tại câu sai** chứ không gom vào một chỗ.
   Đo thật ở cut 17 Pro: sai 5 con số (độ sáng lấy nhầm số đời trước, gọi crop là
   tiêu cự, giá lệch, gọi sai tên dòng máy sắp ra, nói "y chang" cho cả máy trong
   khi tin đồn chỉ đúng mặt lưng) và 3 chỗ gọi sai tên riêng.
   Ba loại phải tách bạch: **sai số liệu** (phải sửa) · **suy đoán nguyên nhân**
   (bỏ mệnh đề giải thích, giữ trải nghiệm) · **tin đồn** (giữ, nhưng bắt buộc nói
   rõ là tin đồn và chèn chữ lên hình — hôm sau hãng ra mắt là biết ai đúng).
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

**CHỐT không phải là chỗ đứng đợi.** Cứ viết trang Notion ra rồi đưa link; câu hỏi
đặt BÊN CẠNH sản phẩm, không thay cho sản phẩm. Người dùng duyệt bằng cách nhìn,
không bằng cách trả lời. (Chốt 2026-09-04: tôi tóm tắt transcript rồi ngồi hỏi ba
câu, họ đáp lại đúng một câu — *"sao chưa đưa vào notion"*.)

## Bản thu thô nhiều vấp — LỌC, đừng viết lại

Khi bản thu là **một mạch nói có vấp, có nói lại** (không phải bản đọc sạch), sản
phẩm là **DANH SÁCH GIỮ**, không phải một kịch bản hay hơn.

**Luật gốc: giữ nguyên văn lời họ. Không sửa câu chữ.** Chốt 2026-09-04 sau khi tôi
viết lại cả bài — dời chỗ đoạn hay lên đầu, chế thêm câu đố giữ chân người xem — và
bị bác thẳng: *"chỉ lọc voice để lọc các đoạn trùng lặp, sai thông số, chứ không sửa
câu từ của tôi."* Gợi ý về cấu trúc/nhịp được phép, nhưng **để ở cột ghi chú cạnh
câu nguyên văn**, không thay vào chỗ lời họ.

Cách làm:

1. **Chọn lần nói sạch nhất của mỗi ý, giữ nguyên văn**, kèm mốc vào–ra để cắt được
   thẳng từ bản thu — không phải thu lại giọng.
2. **Trích chữ bằng máy, đừng gõ tay.** Neo vào cụm đầu + cụm cuối rồi lấy đoạn
   thẳng từ `words[]`. Coi chừng token gộp hai từ qua chỗ vấp (`"chúng...Vậy"`):
   khớp trên **chuỗi ký tự phẳng có map char→token**, không so từng token.
3. **Chỗ sai thông số thì chú ở ngay câu đó**, kèm *cụ thể mấy tiếng cần thu lại*.
   Bốn con số sai chỉ tốn bốn lần thu vài giây, không phải thu lại cả bài.
4. **Lần nói đúng thường đã nằm sẵn trong một take bị bỏ.** Kiểm trước khi bắt họ
   thu thêm — ở cut 17 Pro, take đầu nói đúng "iPhone 18 Pro" còn take sau mới sai
   thành "dòng iPhone 18".
5. **Có câu chỉ cần CẮT là hết sai** — bỏ mệnh đề suy đoán nguyên nhân, bỏ số sai
   rồi bỏ luôn liên từ bị treo phía sau.

### Cắt không tạo ra được cái đúng — cắm marker THU BÙ

Skill này không lồng tiếng máy, nên chỗ nào sai số mà cắt xong là **mất hẳn ý**, thì
cắm một marker riêng: **màu Cyan, `duration` 90 frame** để nhìn ra thanh ngang ngay,
tên `THU BÙ 01/02/03`, note ghi **đúng câu cần thu và ghép vào đâu**.

### Cắt một phần có thể đẻ ra lỗi mới

Đo thật: câu *"ba tiêu cự không chấm năm, một X và tám X"* sai ở "tám X". Cắt riêng
"và tám X" thì còn *"ba tiêu cự 0.5x"* — hô ba mà kể một, **sai kiểu khác**. Phải bỏ
cả câu liệt kê. **Cắt xong luôn đọc lại câu còn lại thành tiếng trong đầu** trước khi
coi là xong.

### Mối nối phải soi riêng

Sau khi ghép, dò hai chỗ này — cả hai đều đã xảy ra:

- **Lặp từ ở điểm nối**: 3 từ cuối đoạn trước trùng 3 từ đầu đoạn sau (`hub dock`,
  `nên là`, `có màn hình đẹp`, `quá chuyên biệt`). So tự động, đừng đọc bằng mắt.
- **Mất liên từ đầu câu**: cắt mất *"Trừ cái"* làm câu kết cụt đầu thành *"Vỏ của nó
  khá là dễ cấn trầy"*.

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

## Kiểm chứng — luật rút ra sau ba lỗi lọt lưới (2026-09-04)

Cả ba lỗi dưới đây đều đi kèm `success: true`. Lệnh chạy đúng, kết quả sai.

**1. Cắt xong thì BÓC LỜI LẠI chính bản vừa dựng**, rồi dò từng cụm sai xem còn 0
lần xuất hiện không, và dò cả các cụm **phải còn** (đề phòng cắt lẹm). Đây là cách
duy nhất bắt được chuyện *"cắt tám X xong còn ba tiêu cự 0.5x"*.

**2. Marker phải đối chiếu với CHỮ, không với phép cộng của mình.** Sau khi tính
frame, lấy transcript của bản đã dựng ra xem mốc đó rơi vào chữ nào. Lần đầu làm,
marker chương 8 rơi giữa câu — *"Pro nhỏ gọn nên mình cũng rất dễ…"* thay vì
*"Vì kích thước iPhone 17 Pro nhỏ gọn…"*.

**3. Dò khoảng lặng thì lấy khoảng lặng ĐẦU TIÊN, cửa sổ hẹp (~2 giây).** Lấy cái
CUỐI trong cửa sổ 3 giây làm bốn đoạn bị cắt lẹm cả cụm từ đầu câu — nặng nhất là
mất luôn *"âm thanh đi trực tiếp từ mic của mình"*. Sai này không lộ ra ở bất kỳ
readback nào, chỉ lộ khi soi marker và nghe lại chữ.

**Đừng render đi render lại rồi mới kiểm.** Tính xong danh sách cắt thì kiểm mốc
trước, dựng sau — một lần đo thay cho ba lần dựng lại timeline.

## Dựng lại thì lấy nguồn từ Notion, không từ sản phẩm phụ

Chốt 2026-09-04: *"không được dựa vào voice-edit đã làm trước đó mà dựa vào note
trên notion."* Trang Notion là **bản ghi đã duyệt**; file CSV/EDL/JSON tôi sinh ra
dọc đường thì không.

- Đọc bảng lọc trong chính trang Notion, rồi **giải mỗi dòng về mốc chính xác bằng
  cách tìm lại nguyên văn câu đó trong `transcript.json`**. Timecode hiển thị trên
  bảng chỉ chính xác tới **giây** — ở 30fps là ±30 frame, **không dùng làm điểm cắt
  được**.
- **Lấy Ý ĐỊNH từ trang, ĐO LẠI con số từ audio.** Một bảng viết trước khi sửa bug
  sẽ giữ nguyên con số cũ. Thực tế đã xảy ra: bảng "22 chỗ can thiệp" ghi 1,69s /
  1,90s / 0,52s / 2,21s trong khi callout ngay dưới ghi số đã sửa — trang tự mâu
  thuẫn. Dựng bằng cách đo lại thì miễn nhiễm; dựng bằng cách chép số thì tái sinh
  bug. **Phát hiện mâu thuẫn thì sửa luôn trang**, đừng để đó.
- **Bẫy đọc bảng Notion:** heading `### N. Tên` nằm **SAU** dòng cuối của chương
  trước trong cùng một khối text. Đổi tên chương trước khi đọc dòng đó thì **lệch
  một dòng ở MỌI ranh giới chương**. Đọc ô trước, đổi chương sau. Bắt được bằng
  cách đếm số dòng mỗi chương và so với bản dựng trước.

## Chapters cho phần mô tả YouTube

Xuất danh sách dán thẳng vào mô tả, dạng `0:00 Tên chương`. Luật YouTube:

- Chương đầu **bắt buộc** là `0:00`.
- Tối thiểu **3 chương**.
- Mỗi chương tối thiểu **10 giây**.

Không đủ điều kiện thì chapters sẽ không hiện — **báo người dùng**, đừng xuất danh
sách hỏng rồi coi như xong.

**Chương cuối hay dính luật 10 giây** — phần "cảm ơn, like và đăng ký" thường chỉ
4–5 giây. Nói rõ cách xử: bỏ dòng đó khỏi mô tả, hoặc gộp vào chương trước.

**Timecode chapters phải ĐO TRÊN BẢN ĐÃ CẮT, không phải trên bản thu thô.** Cộng dồn
độ dài thật của các đoạn giữ lại (kể cả khoảng hở chèn thêm), rồi đối chiếu với
transcript của bản dựng. Nếu trên trang Notion còn khối chapters tính theo bản thô
thì **gắn cảnh báo lên khối đó** — đừng để hai bảng số cạnh nhau mà không nói cái
nào dùng được.

## Cắt trên timeline từ media gốc — CÔNG THỨC ĐÃ CHẠY THẬT (2026-09-04)

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

Đây là cách hiện thực luật 1. Dựng 148 cú cắt từ một file thu 25 phút, một lệnh:

```
media_pool create_timeline_from_clips
  name: "<tên>"
  clip_infos: [ {clip_id, startFrame, endFrame, recordFrame}, ... ]
```

- `startFrame`/`endFrame` là **frame NGUỒN**, `recordFrame` là vị trí trên timeline
  (mặc định tính tương đối so với đầu timeline).
- `endFrame` **EXCLUSIVE** — cùng cái bẫy đã ghi ở trên. Clip dài N frame từ nguồn S
  thì truyền `S + N`.
- **ĐỌC FPS CỦA MEDIA POOL ITEM TRƯỚC.** `media_pool_item get_clip_property` với key
  `FPS` và `Duration`. Đo thật: file audio **ALAC 192kHz** vẫn được Resolve đếm ở
  **30fps** (`Duration` `00:25:20:20` = 45.620 frame) vì đó là nhịp project lúc
  import. Nên `frame_nguồn = round(giây × 30)`. **Đừng đoán** — với WAV thì nhịp bị
  đóng băng theo project lúc import và có thể lệch hẳn với timeline.
- Payload 148 clip đi lọt trong một lệnh, không cần chia nhỏ.

**Kiểm sau khi dựng — bắt buộc, và đừng tin `success: true`:**

1. `timeline get_current` → số frame tổng phải khớp con số tính trước khi dựng.
2. `timeline get_items_in_track` → **độ dài từng clip** phải khớp từng con số. Đây là
   chỗ lộ ra lỗi `end_frame` lệch 1 frame.
3. `timeline_item get_source_start_frame` / `get_source_end_frame` trên clip **đầu và
   cuối** → đọc ngược ra đúng mốc nguồn đã yêu cầu.

**Khoảng hở giữa các clip là CỐ Ý.** Cắt sát từ đầu tới từ cuối thì mất luôn quãng
ngắt hơi, câu sẽ dính vào nhau. Chèn lại **4 frame** giữa hai đoạn cùng chương và
**11 frame** giữa hai chương. Vì vậy `detect_gaps_overlaps` sẽ báo cả trăm gap trên
track audio — **bình thường**. Luật `gap_count: 0` chỉ áp cho **cut hình trên V1**.
Cái phải bằng 0 ở đây là `overlap_count`.

**Fade ở điểm cắt là việc tay.** API không đặt được fade handle cho clip audio. Điểm
cắt rơi vào chỗ ngắt hơi thì hiếm khi kêu cạch; nghe thấy thì bảo người dùng chọn
tất cả rồi thêm fade 2 frame.

**Sample rate của project không đọc được qua API** (nằm trong Fairlight settings).
Nếu người dùng quan tâm giữ nguyên chất lượng thì nhắc họ tự kiểm; 48kHz là chuẩn
giao video, không phải lỗi.

## Text động trên timeline — CÔNG THỨC ĐÃ CHỨNG MINH (2026-09-02)

### Vị trí chữ trên khung hình — biên an toàn theo nền tảng, TOẠ ĐỘ THEO TỪNG FRAME

**Biên dưới đây là RÀNG BUỘC CỨNG, không phải toạ độ để dán mù.** Icon/UI của nền
tảng luôn nằm cố định ở đó bất kể nội dung cảnh quay, nên phần trăm này không đổi.
Nhưng **vị trí thật bên trong biên đó phải chọn theo đúng frame đang lên hình tại
thời điểm đặt caption** — không phải cứ lower-third hay giữa khung là xong. Chỗ đó
trống ở caption này, nhưng ở caption khác có thể đúng ngay chỗ sản phẩm đang được
thao tác trên bàn.

Preset mặc định canh giữa khung hình — dùng được khi khung đó đang trống ở giữa,
**không dùng được khi giữa khung có sản phẩm/chủ thể đang được nói tới**. Che mất
đúng thứ caption đang gọi tên là hỏng nặng hơn cả đặt sai thời điểm.

**Video ngang (YouTube, 1920×1080 — mặc định của skill này):** không có icon nền
tảng đè lên khung khi xem; vùng nguy hiểm duy nhất là mép khung — **title-safe
area chuẩn broadcast: chừa 5% mỗi cạnh**. Lower-third truyền thống (~75–85%
chiều cao khung) là điểm khởi đầu hợp lý vì thường trống và không trùng vị trí
CC mặc định của YouTube khi người xem tự bật, **nhưng vẫn phải soi frame** — cảnh
quay tay/sản phẩm ở dưới khung thì lower-third che đúng chỗ đang nói, phải đẩy
chữ lên trên hoặc sang bên trống. Giữa khung ngang thường che mặt người nói nên
tránh trừ khi frame đó thật sự trống ở giữa.

**Video dọc (Reels/TikTok/Shorts, 1080×1920 — dùng khi người dùng đổi sang lệnh
`/video`):**

| Vùng | Chừa ra vì |
|---|---|
| ~15% bên phải | Cột icon like/comment/share/profile — cả ba nền tảng đều đặt ở đây |
| ~20–25% đáy khung | Caption/username của nền tảng, thanh tiến trình, nút CTA |
| ~8% đỉnh khung | Một số máy che bằng notch/status bar khi xem toàn màn hình |

Trong phần khung còn lại, soi frame thật trước rồi mới chọn toạ độ né sản phẩm.

**Cách làm, cả hai hướng:** `timeline_frame capture` tại đúng frame định đặt
caption **TRƯỚC KHI** set `Center`, nhìn xem sản phẩm/chủ thể nằm ở đâu, rồi chọn
toạ độ trong biên an toàn né được chỗ đó. Vị trí toàn khối chữ đổi qua input
`Center` (Point) trên tool `Template` — **`get_inputs` trước để xác nhận đúng tên
input cho preset đang dùng** (tên có thể đổi theo preset, cùng bẫy đã ghi ở mục
`Delay`). Toạ độ chuẩn Fusion: `(0,0)` góc dưới-trái, `(1,1)` góc trên-phải,
`(0.5,0.5)` là mặc định giữa khung.

**Bẫy định dạng — đã đo 2026-09-05:** `set_input` cho input kiểu `Point` bằng
dict `{"1": x, "2": y, "3": 0}` (đúng hệt định dạng `get_input` trả về) báo
`success: true` nhưng **không hề ghi** — đọc lại vẫn ra giá trị cũ. Phải truyền
**list `[x, y]`** thì mới thực sự set được. Luôn `get_input` đọc lại ngay sau khi
set để xác nhận giá trị đã đổi, rồi mới `timeline_frame capture` để xác nhận
bằng mắt — đọc lại rẻ hơn render, làm cả hai vì đọc lại chỉ xác nhận giá trị ghi
đúng, không xác nhận vị trí trên khung có thật sự né được sản phẩm hay không.
Hai caption liền nhau trong cùng một bài hoàn toàn có thể nằm ở hai toạ độ khác
nhau — đó là bình thường, không phải thiếu nhất quán.

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

### Tầng track khi có `text` — đo từ bản người dùng tự dựng lại (2026-09-04)

Tôi đặt text lên V2. Người dùng **dời lên V4** và chèn adjustment clip vào V3. Cấu
trúc họ dùng:

| Track | Nội dung |
|---|---|
| **V4** | Text |
| **V3** | Adjustment Clip (grade) |
| **V2** | Để trống — chừa chỗ cho b-roll / chèn về sau |
| **V1** | Cut |
| A3 | SFX |
| A2 | VO |
| A1 | Tiếng source |

**Lý do text phải nằm TRÊN adjustment clip:** adjustment clip grade mọi thứ bên dưới
nó. Text đặt ở V2 sẽ bị grade theo — chữ trắng thành ngả màu theo look của cảnh. Đặt
text ở track cao nhất là để nó nằm ngoài tầm với của lớp grade.

**Adjustment clip đặt thế nào** (đo trên cut 810 frame):

- **Hai clip, không phải một.** Cắt ở **frame 475** — đúng ranh giới đoạn nội dung
  (chuyển từ khối giới thiệu sang khối hướng dẫn). Hai đoạn có tông sáng khác nhau
  nên cần grade riêng.
- **Bắt đầu ở frame 136, không phải 0.** Hook được để nguyên, không nằm trong lớp
  grade. Kéo dài tới hết timeline.

Khi dựng có `text`, **tạo sẵn cấu trúc track này** — V2 để trống, V3 để trống chờ
adjustment, text lên V4. Đừng dồn text xuống V2 rồi để người dùng phải kéo lên.

### Adjustment clip: tạo được, nhưng KHÔNG đặt được lên track cần

Đo 2026-09-04. `timeline insert_generator("Adjustment Clip")` **chạy được** — ra một
adjustment clip 150 frame. Nhưng nó rơi vào **V1**, và V1 là chỗ để cut.

Cùng cái bẫy của `insert_title`: sáu lệnh `Insert*IntoTimeline` không nhận
`trackIndex`. Đã thử khoá V1 và V2 để ép nó rơi lên V3 → lệnh **thất bại**
(`Failed to insert generator`), không phải rơi lên track trên. Giống hệt kết quả đã
đo với title.

Đường vòng nested timeline **không dùng được ở đây**: lồng adjustment clip vào một
timeline con biến nó thành clip thường, mất hẳn tác dụng grade lớp dưới.

`MoveClips` chỉ dời clip giữa thư mục Media Pool, không dời item giữa track.

**Nên làm gì:** khi dựng có `text`, **tạo sẵn track V3 trống** và cắm hai marker ở
điểm bắt đầu và điểm cắt của lớp grade (đo trên cut 810 frame: **frame 136** và
**frame 475**). Người dùng kéo hai adjustment clip vào là xong trong mười giây.

**Nói thẳng trong báo cáo cuối** rằng adjustment clip là việc tay, kèm hai con số
frame. Đừng im lặng bỏ qua, cũng đừng hứa làm được.

**Dynamic Zoom cũng không đọc được.** `GetProperty("DynamicZoom")` trả `null` trên
cả clip media lẫn adjustment clip; `get_transform` báo `ZoomX 1, ZoomY 1` y như chưa
bật. Muốn biết zoom có chạy hay không thì **render hai frame ở hai thời điểm rồi so**
— đọc thông số là bế tắc.

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

ffmpeg ở đây gần như chỉ để **ĐỌC**. Không ghi đè source, và **không dùng để dựng
cut** — cắt là việc của timeline (xem luật 1).

**Ngoại lệ duy nhất được phép transcode: bản nén để upload đi bóc lời**, ghi vào
`<folder>/elevenlabs/`. Đó là file vứt đi, không phải sản phẩm.

Nếu lỡ dựng một bản render trung gian rồi mới nhớ ra luật: **đừng để nó nằm trên
timeline**. Dựng lại bằng clip cắt từ media gốc, và nói rõ trong báo cáo là file
render kia còn trên đĩa, người dùng tự xoá.

## Báo cáo cuối

Nêu rõ: project + timeline đã tạo, link Notion, file đã sinh, và **những gì KHÔNG
làm** (không grade / không text / không nhạc / không render) để không ai tưởng là
làm thiếu. Bước nào bị bỏ vì vướng thì nói thẳng lý do — đừng báo hoàn thành khi
mới xong một nửa.

Nếu có lọc/cắt bản thu, báo cáo thêm:

- **Đã kiểm chứng thế nào** — không chỉ nói "xong", mà nói đã bóc lời lại bản dựng
  và các cụm sai còn 0 lần xuất hiện.
- **Lỗi mình tự bắt được và đã sửa.** Người dùng cần biết chỗ nào từng suýt lọt, để
  họ biết nên nghe kỹ đoạn nào.
- **Cái gì cắt không cứu được** — liệt kê từng câu THU BÙ kèm đúng lời cần thu.
- **Việc tay còn lại**: fade điểm cắt, adjustment clip, sample rate project, và
  normalize (đưa số LUFS đo được, đừng tự normalize).
