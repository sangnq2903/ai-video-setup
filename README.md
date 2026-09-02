# AI video setup

Bộ cấu hình biến một file thu âm giọng nói thành bản dựng trong DaVinci Resolve.
Dựng và đo trên **DaVinci Resolve 20.3.3**, macOS.

Toàn bộ những gì ở đây vốn nằm rải rác trong `~/.claude/` — gom lại để version được.

## Có gì

| Đường dẫn | Là gì |
|---|---|
| `commands/video.md` | Lệnh `/video` — dựng short-form dọc cho TikTok/Reels, kèm bản tiếng Anh cho Instagram |
| `skills/youtube-long/` | Dựng YouTube ngang, có chapters và SEO, chỉ tiếng Việt |
| `skills/voice-timecode/` | Bóc lời thành bảng timecode + kịch bản vào Notion. Là bước B1+B2 tách riêng |
| `scripts/en-vo.py` | Dựng VO tiếng Anh bằng voice clone mà không bị trôi accent |
| `patches/` | Hai bản vá cho `davinci-resolve-mcp` + test đi kèm |

## Cài

```bash
cp commands/video.md            ~/.claude/commands/
cp -r skills/youtube-long       ~/.claude/skills/
cp -r skills/voice-timecode     ~/.claude/skills/
cp scripts/en-vo.py             ~/.claude/scripts/
```

Khởi động lại phiên Claude Code để nạp.

## Vá MCP server

Hai bản vá cho `davinci-resolve-mcp` (upstream: `samuelgursky/davinci-resolve-mcp`):

1. **`gallery_stills` đọc được PowerGrade album** — thêm `album_type` và `album_name`.
   Trước đó mọi action chỉ tra `GetGalleryStillAlbums()`, nên album PowerGrade trả
   `Album index out of range` dù `get_power_grade_albums()` liệt kê đủ.
2. **`timeline_frame capture` nhận `out_path`** — giữ lại frame đã render thay vì chỉ
   trả ảnh inline. Cần khi phải *đo* frame chứ không phải *nhìn* nó.

```bash
cd /duong/dan/toi/davinci-resolve-mcp
git apply /duong/dan/toi/patches/davinci-resolve-mcp.patch
cp patches/test_*.py tests/
python -m unittest discover -s tests -t .
```

## Không có khoá nào ở đây

Không file nào chứa API key. `en-vo.py` đọc key lúc chạy từ
`.mcp.json` của repo davinci-resolve-mcp — đường dẫn hardcode ở đầu file, sửa lại
cho đúng máy bạn.

## Vài điều đã đo, đừng đo lại

- **Voice clone đọc tiếng Anh phải dùng `eleven_turbo_v2`**, không phải
  `eleven_multilingual_v2`. Model đa ngữ mượn phoneme tiếng Việt và cho ra giọng
  Nam Á. `eleven_v3` còn tệ hơn.
- **Phải đọc từng câu ngắn rồi ghép.** Clone dựng từ 17 giây audio chỉ giữ được giọng
  1–2 giây rồi trôi. Câu quá 12 từ là vào vùng hỏng.
- **Có cờ `text` không có nghĩa là rải chữ suốt bài.** Caption chỉ đặt ở đoạn gọi tên
  sản phẩm, đọc thông số, hoặc là điểm nhấn (hook, CTA). Đoạn kể chuyện thì bỏ trống —
  đặt chữ vào chỉ là chép lại lời thoại lên màn hình. Khoảng 3–5 caption cho Reel
  25–30 giây.
- **ElevenLabs MCP không trả timestamp** — nó vứt `start`/`end` của từng từ. Mốc thời
  gian phải suy từ `ffmpeg silencedetect`, sai số khoảng ±0,5 giây.
- **Đừng dùng `insert_title` của Resolve** — nó ripple insert trên V1 và đẩy lệch cả
  cut, rồi vẫn báo thành công. Dùng nested timeline.
- **Resolve API không đọc/ghi được giá trị primary grade.** Chỉ có CDL, DRX và LUT.

## Bộ nhớ — phần KHÔNG tự đi theo bạn

`memory/` là 13 file ghi lại những gì đã học: gu nhạc, luật opt-in, thông số
timeline, và các cái bẫy đã đo được.

Skill và lệnh nằm ở cấp user nên chạy ở thư mục nào cũng có. **Bộ nhớ thì không** —
nó khoá theo đường dẫn thư mục làm việc:

```
~/.claude/projects/<duong-dan-doi-dau-gach>/memory/
```

Đổi sang thư mục khác là bắt đầu lại từ số không. Muốn giữ, chép sang:

```bash
# vd thu muc moi la /Volumes/Data/my-video-repo
TARGET=~/.claude/projects/-Volumes-Data-my-video-repo/memory
mkdir -p "$TARGET" && cp memory/*.md "$TARGET/"
```

Tên thư mục = đường dẫn tuyệt đối, thay mọi `/` bằng `-`.

`MEMORY.md` là mục lục nạp vào mỗi phiên — chép cả nó, thiếu là các file kia thành
vô hình.
