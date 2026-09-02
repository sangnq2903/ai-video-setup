#!/usr/bin/env python3
"""
Dựng VO tiếng Anh bằng voice clone "Sáng" mà KHÔNG bị trôi sang accent Ấn.

Cách hoạt động: clone "Sáng" chỉ dựng từ 17 giây audio nên nó giữ được giọng
khoảng 1-2 giây rồi trôi. Đọc cả đoạn một lần là hỏng. Script này đọc TỪNG CÂU
NGẮN riêng, rồi ghép lại bằng ffmpeg.

Đo ngày 2026-09-02: câu 1.0-1.9s giữ được giọng, đoạn dài 9s thì trôi.

Dùng:
    python3 en-vo.py kichban.txt -o /duong/dan/ra
    python3 en-vo.py kichban.txt -o out --gap 0.25

File kịch bản: MỖI DÒNG MỘT CÂU NGẮN. Dòng trống bị bỏ qua.
Dòng bắt đầu bằng # là ghi chú, không đọc.
"""
from __future__ import annotations   # python3 hệ thống là 3.9, cần cái này cho "dict | None"
import argparse, json, os, re, subprocess, sys, tempfile, urllib.request, uuid

VOICE_ID = "xYGgUqVrkXAXMWJZtqgF"          # "Sáng"

# Mặc định = cấu hình E2, người dùng chốt 2026-09-02 sau khi nghe 13 bản.
# Thay cho cấu hình turbo_v2 cũ: turbo_v2 sạch accent nhưng KHÔNG có cảm xúc.
# eleven_v3 mở ra hai thứ turbo_v2 không có: language_code (ghim phoneme tiếng
# Anh) và audio tag (lấy cảm xúc). Đổi lại v3 đọc chậm hơn ~20%.
# ĐƯỜNG MẶC ĐỊNH = STS ("S1"), người dùng chốt 2026-09-02.
# Một giọng Anh-Anh bản xứ đọc câu với cảm xúc, rồi convert sang giọng "Sáng".
# Cảm xúc + nhịp lấy từ bản diễn nguồn; timbre lấy từ clone. Model STS là
# English-only nên không có phoneme Việt để mượn -> hết accent Ấn.
#
# Vì sao không phải TTS thẳng: eleven_turbo_v2 có can_use_style=False và
# can_use_speaker_boost=False (đo qua /v1/models) -> KHÔNG có knob cảm xúc nào.
# eleven_v3 có tag cảm xúc nhưng không tất định và đọc chậm hơn ~20%.
VIA_VOICE = "JBFqnCBsd6RMkjVDRZzb"          # George, premade, british male
VIA_MODEL = "eleven_turbo_v2"
VIA_SETTINGS = {"stability": 0.4, "similarity_boost": 0.75}
STS_MODEL = "eleven_english_sts_v2"
STS_SETTINGS = {                            # cấu hình S1
    "stability": 0.5,
    "similarity_boost": 0.35,
    "style": 0.0,
    "use_speaker_boost": False,
}

# Đường TTS thẳng, chỉ dùng khi chạy với --no-via.
MODEL_ID = "eleven_v3"
LANGUAGE = "en"                             # v3 CHỈ nhận "en"; "en-GB" bị API từ chối
SETTINGS = {
    "stability": 0.5,                       # v3 chỉ nhận 0.0 / 0.5 / 1.0
    "similarity_boost": 0.20,
}

# Cấu hình cũ, giữ lại để so sánh: --model eleven_turbo_v2 --stability 0.55
# --similarity 0.35 (turbo_v2 KHÔNG nhận language_code, script tự bỏ).
TAG_RE = re.compile(r"\[[^\]]*\]")           # audio tag [curious] — không tính vào giới hạn từ
MCP_JSON = "/Volumes/Data/davinci-resolve-mcp/.mcp.json"
WORD_LIMIT = 12   # dài hơn là vào vùng trôi giọng


def api_key() -> str:
    with open(MCP_JSON) as f:
        return json.load(f)["mcpServers"]["elevenlabs"]["env"]["ELEVENLABS_API_KEY"]


def read_lines(path: str) -> list[str]:
    out = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            if s and not s.startswith("#"):
                out.append(s)
    if not out:
        sys.exit(f"Không có câu nào đọc được trong {path}")
    return out


def tts(text: str, key: str, dest: str, model: str = MODEL_ID,
        settings: dict | None = None, language: str | None = LANGUAGE,
        voice: str = VOICE_ID) -> None:
    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": settings if settings is not None else SETTINGS,
    }
    # turbo_v2 là model English-only, nó không nhận language_code
    if language and model.startswith("eleven_v3"):
        payload["language_code"] = language
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
        data=body,
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as out:
        out.write(r.read())


def sts(src: str, key: str, dest: str, settings: dict) -> None:
    """Convert bản diễn nguồn sang giọng đích. Giữ NGUYÊN nhịp của bản nguồn."""
    boundary = "----" + uuid.uuid4().hex
    parts = []
    for k, v in (("model_id", STS_MODEL),
                 ("voice_settings", json.dumps(settings)),
                 ("remove_background_noise", "true")):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; '
                 f'name="audio"; filename="{os.path.basename(src)}"\r\n'
                 f'Content-Type: audio/mpeg\r\n\r\n'.encode())
    parts.append(open(src, "rb").read() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/speech-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
        data=b"".join(parts),
        headers={"xi-api-key": key,
                 "Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as out:
        out.write(r.read())


def duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def concat(segs: list[str], gap: float, dest: str) -> None:
    """Ghép các đoạn, chèn khoảng lặng `gap` giây ở giữa."""
    inputs, labels = [], []
    for i, s in enumerate(segs):
        inputs += ["-i", s]
        labels.append(f"[{i}:a]")
    filt = ""
    if gap > 0 and len(segs) > 1:
        for i in range(len(segs) - 1):
            filt += f"aevalsrc=0:d={gap}:s=44100:c=mono[g{i}];"
        chain = labels[0]
        for i in range(1, len(segs)):
            chain += f"[g{i-1}]" + labels[i]
        n = len(segs) * 2 - 1
    else:
        chain, n = "".join(labels), len(segs)
    filt += f"{chain}concat=n={n}:v=0:a=1[out]"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs,
         "-filter_complex", filt, "-map", "[out]",
         "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "44100", "-ac", "1", dest],
        check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="VO tiếng Anh theo từng câu ngắn rồi ghép")
    ap.add_argument("script", help="file .txt, mỗi dòng một câu ngắn")
    ap.add_argument("-o", "--out", required=True, help="thư mục xuất")
    ap.add_argument("--gap", type=float, default=0.18, help="khoảng lặng giữa câu, giây")
    ap.add_argument("--name", default="VO-en.mp3", help="tên file ghép")
    ap.add_argument("--dry-run", action="store_true", help="chỉ kiểm tra, không gọi API")
    ap.add_argument("--model", default=MODEL_ID, help=f"mặc định {MODEL_ID}")
    ap.add_argument("--stability", type=float, default=SETTINGS["stability"])
    ap.add_argument("--similarity", type=float, default=SETTINGS["similarity_boost"])
    ap.add_argument("--language", default=LANGUAGE, help='chỉ có tác dụng với eleven_v3; v3 chỉ nhận "en"')
    ap.add_argument("--via", default=VIA_VOICE,
                    help="voice_id đọc bản diễn nguồn rồi convert sang giọng đích (mặc định: George)")
    ap.add_argument("--no-via", action="store_true",
                    help="bỏ đường STS, gọi TTS thẳng bằng --model")
    ap.add_argument("--style", type=float, default=STS_SETTINGS["style"], help="chỉ dùng cho STS")
    a = ap.parse_args()
    settings = {"stability": a.stability, "similarity_boost": a.similarity}
    sts_settings = dict(STS_SETTINGS, style=a.style)

    lines = read_lines(a.script)
    chars = sum(len(x) for x in lines)

    # đếm từ SAU khi bỏ audio tag — tag không phải lời đọc
    long = [(i, l) for i, l in enumerate(lines, 1)
            if len(TAG_RE.sub("", l).split()) > WORD_LIMIT]
    if long:
        print(f"CẢNH BÁO: {len(long)} câu dài hơn {WORD_LIMIT} từ — vùng trôi giọng.")
        for i, l in long:
            print(f"  dòng {i} ({len(l.split())} từ): {l[:64]}...")
        print("  Nên cắt ngắn rồi chạy lại.\n")

    print(f"{len(lines)} câu, {chars} ký tự sẽ tính vào quota ElevenLabs.")
    if a.no_via:
        print(f"TTS thẳng: model={a.model} stability={a.stability} "
              f"similarity={a.similarity} "
              f"language={a.language if a.model.startswith('eleven_v3') else '(bỏ qua)'}")
    else:
        print(f"STS: {a.via} ({VIA_MODEL}) -> {VOICE_ID} ({STS_MODEL}), "
              f"style={sts_settings['style']} similarity={sts_settings['similarity_boost']}")
        print("     nhịp và độ dài do bản diễn nguồn quyết định, STS không co giãn.")
    if a.dry_run:
        return

    os.makedirs(a.out, exist_ok=True)
    key = api_key()
    segs = []
    for i, line in enumerate(lines, 1):
        p = os.path.join(a.out, f"seg{i:02d}.mp3")
        if a.no_via:
            tts(line, key, p, model=a.model, settings=settings, language=a.language)
        else:
            src = os.path.join(a.out, f"src{i:02d}.mp3")
            tts(line, key, src, model=VIA_MODEL, settings=VIA_SETTINGS,
                language=None, voice=a.via)
            sts(src, key, p, sts_settings)
        segs.append(p)
        print(f"  seg{i:02d}  {duration(p):5.2f}s  {line[:56]}")

    dest = os.path.join(a.out, a.name)
    concat(segs, a.gap, dest)
    print(f"\nXong: {dest}  ({duration(dest):.2f}s)")


if __name__ == "__main__":
    main()
