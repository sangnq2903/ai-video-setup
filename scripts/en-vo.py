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
import argparse, json, os, subprocess, sys, tempfile, urllib.request

VOICE_ID = "xYGgUqVrkXAXMWJZtqgF"          # "Sáng"
MODEL_ID = "eleven_turbo_v2"                # English-only. KHÔNG dùng multilingual.
SETTINGS = {                                # cấu hình B, chốt 2026-09-02
    "stability": 0.55,
    "similarity_boost": 0.35,
    "style": 0.0,
    "use_speaker_boost": False,
    "speed": 1.0,
}
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


def tts(text: str, key: str, dest: str) -> None:
    body = json.dumps({
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": SETTINGS,
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128",
        data=body,
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as out:
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
    a = ap.parse_args()

    lines = read_lines(a.script)
    chars = sum(len(x) for x in lines)

    long = [(i, l) for i, l in enumerate(lines, 1) if len(l.split()) > WORD_LIMIT]
    if long:
        print(f"CẢNH BÁO: {len(long)} câu dài hơn {WORD_LIMIT} từ — vùng trôi giọng.")
        for i, l in long:
            print(f"  dòng {i} ({len(l.split())} từ): {l[:64]}...")
        print("  Nên cắt ngắn rồi chạy lại.\n")

    print(f"{len(lines)} câu, {chars} ký tự sẽ tính vào quota ElevenLabs.")
    if a.dry_run:
        return

    os.makedirs(a.out, exist_ok=True)
    key = api_key()
    segs = []
    for i, line in enumerate(lines, 1):
        p = os.path.join(a.out, f"seg{i:02d}.mp3")
        tts(line, key, p)
        segs.append(p)
        print(f"  seg{i:02d}  {duration(p):5.2f}s  {line[:56]}")

    dest = os.path.join(a.out, a.name)
    concat(segs, a.gap, dest)
    print(f"\nXong: {dest}  ({duration(dest):.2f}s)")


if __name__ == "__main__":
    main()
