#!/usr/bin/env python3
"""DFMC boss art batch — pipeline-compliant.
gpt-image-2-2026-04-21 · t2i /images/generations only (new characters, no image input)
· 1024x1536 portrait (boss deviation, approved) · RAW art placed with bg (crop only
after approval, via remove.bg) · OpenAI reachable via curl subprocess ONLY.
Usage: OPENAI_API_KEY=sk-... python3 scripts/gen_bosses.py [BOSS-010 ...]"""
import csv, json, os, subprocess, sys, base64

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "codex", "bosses.csv")
IMG_DIR = os.path.join(ROOT, "codex", "images")
MODEL, SIZE = "gpt-image-2-2026-04-21", "1024x1536"

def gen(prompt):
    key = os.environ["OPENAI_API_KEY"]
    payload = json.dumps({"model": MODEL, "prompt": prompt, "size": SIZE, "quality": "high", "n": 1})
    out = subprocess.run(["curl", "-sS", "--max-time", "600",
        "https://api.openai.com/v1/images/generations",
        "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
        "-d", payload], capture_output=True, text=True)
    data = json.loads(out.stdout)
    if "error" in data: raise RuntimeError(data["error"]["message"])
    return base64.b64decode(data["data"][0]["b64_json"])

def main():
    only = set(sys.argv[1:])
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    for row in rows:
        bid = row["Boss_ID"]; out = os.path.join(IMG_DIR, f"{bid}.png")
        if only and bid not in only: continue
        if not only and os.path.exists(out): print(f"[skip] {bid}"); continue
        p = row["Image_Prompt"].lower()
        assert "chroma" not in p and "no floor" in p and "three-quarter angle" in p, f"{bid}: prompt gate failed"
        print(f"[gen ] {bid} — {row['Boss_Character']}")
        png = gen(row["Image_Prompt"])
        os.makedirs(IMG_DIR, exist_ok=True)
        open(out, "wb").write(png)
        row["Image_Path"] = f"codex/images/{bid}.png"
        print(f"[done] {bid} ({len(png)//1024} KB)")
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print("Image_Path fields updated — commit CSV + PNGs in the SAME commit.")

if __name__ == "__main__": main()
