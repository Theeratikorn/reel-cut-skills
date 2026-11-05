"""reelprofile — โปรไฟล์ผู้ใช้ของชุดสกิล reel-* (ได้จากการสัมภาษณ์ตอนติดตั้ง)
ไฟล์: ~/.config/reelcut/profile.json  (หรือ env REELCUT_PROFILE)
CLI:  python3 -I reelprofile.py show | get <key> | path | exists | save   (save อ่าน JSON จาก stdin แล้วรวมกับค่าเดิม)
ใช้ใน Python: from reelprofile import load; P = load()   (มีค่า default ครบเสมอ)
"""
import json, os, re, sys

PATH = os.environ.get("REELCUT_PROFILE") or os.path.expanduser("~/.config/reelcut/profile.json")

DEFAULTS = {
    "name": "",             # ชื่อที่ให้เรียกผู้ใช้
    "brand": "",            # ชื่อช่อง/แบรนด์ (ใช้ในป้าย/ท้ายคลิปเมื่อผู้ใช้ต้องการ)
    "niche": "",            # เนื้อหา เช่น ติววิชา / รีวิวสินค้า / ท่องเที่ยว
    "audience": "",         # กลุ่มผู้ชม
    "language": "th",       # ภาษาในคลิป th / en
    "clip_types": [],       # เช่น ["พูดหน้ากล้อง", "สอนหน้ากระดาน"]
    "target_seconds": 60,   # ความยาวเป้าหมายหลังตัด
    "style": "sketch-sheet",  # รหัสสไตล์ในคลัง (styles/README.md)
    "accent": "#DB2777",    # สีเน้นจุดเดียวต่อฉาก
    "wall": "light",        # ฉาก/ผนังหลัง: light=สว่าง(ตัวอักษรเข้ม) dark=มืด(ตัวอักษรขาว)
    "series": "",           # ชื่อซีรีส์/หมวด ใช้ในป้ายเม็ดยา
    "pill": "{series} · {topic}",  # รูปแบบป้ายกลางจอ
    "cta_end": "กดเซฟ · แชร์ให้เพื่อน",  # ข้อความท้ายคลิป (ห้ามแต่งเองเกินที่ผู้ใช้ให้)
    "cta_handle": "",       # ช่องทางติดต่อ เช่น @ชื่อ (ว่าง = ไม่แสดง)
    "music": "ask",         # none / bgm / ask
    "out_dir": "",          # โฟลเดอร์ไฟล์สำเร็จ (ว่าง = ค่าเริ่มต้นของระบบ)
    "dislikes": [],         # สิ่งที่ไม่ชอบ เช่น "ภาพรก"
    "subject_checks": "",   # ตรวจความถูกต้องเฉพาะวิชา เช่น "physics" (ว่าง = ไม่ตรวจ)
}
_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def load():
    d = dict(DEFAULTS)
    try:
        d.update(json.load(open(PATH)))
    except (OSError, ValueError):
        pass
    if not _HEX.match(str(d.get("accent", ""))):
        d["accent"] = DEFAULTS["accent"]
    if d.get("wall") not in ("light", "dark"):
        d["wall"] = "light"
    return d


def validate(d):
    errs = []
    unknown = set(d) - set(DEFAULTS)
    if unknown: errs.append("คีย์ที่ไม่รู้จัก: " + ", ".join(sorted(unknown)))
    if "accent" in d and not _HEX.match(str(d["accent"])): errs.append("accent ต้องเป็นรหัสสี #RRGGBB")
    if "wall" in d and d["wall"] not in ("light", "dark"): errs.append("wall ต้องเป็น light หรือ dark")
    if "music" in d and d["music"] not in ("none", "bgm", "ask"): errs.append("music ต้องเป็น none/bgm/ask")
    if "target_seconds" in d and not (isinstance(d["target_seconds"], int) and 15 <= d["target_seconds"] <= 180):
        errs.append("target_seconds ต้องเป็นจำนวนเต็ม 15–180")
    for k in ("clip_types", "dislikes"):
        if k in d and not isinstance(d[k], list): errs.append(k + " ต้องเป็นรายการ")
    return errs


def save(new):
    errs = validate(new)
    if errs: raise ValueError("; ".join(errs))
    cur = {}
    try: cur = json.load(open(PATH))
    except (OSError, ValueError): pass
    cur.update(new)
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w") as f: json.dump(cur, f, ensure_ascii=False, indent=2)
    os.chmod(PATH, 0o600)
    return cur


def hex_to_int(h): return int(h.lstrip("#"), 16)
def darken(h, k=0.45):
    r, g, b = (int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return int(r * k) << 16 | int(g * k) << 8 | int(b * k)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "path": print(PATH)
    elif cmd == "exists": sys.exit(0 if os.path.exists(PATH) else 1)
    elif cmd == "show": print(json.dumps(load(), ensure_ascii=False, indent=2))
    elif cmd == "get":
        v = load().get(sys.argv[2], ""); print(v if not isinstance(v, (list, dict)) else json.dumps(v, ensure_ascii=False))
    elif cmd == "save":
        try: save(json.load(sys.stdin)); print("บันทึกแล้ว:", PATH)
        except Exception as e: sys.exit("บันทึกไม่สำเร็จ: %s" % e)
    else: sys.exit("usage: show|get <key>|path|exists|save")
