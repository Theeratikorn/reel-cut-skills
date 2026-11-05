import json, sys
d = json.load(open(sys.argv[1]))
if "words" not in d:
    sys.exit("transcript error: " + json.dumps(d, ensure_ascii=False)[:300])
cur = []; out = []
def flush():
    if cur: out.append(f"{cur[0]['start']:.2f}-{cur[-1]['end']:.2f} | " + "".join(w['text'] for w in cur).strip())
prev = None
for w in d["words"]:
    if w.get("type") != "word":
        continue
    if prev is not None and w["start"] - prev > 0.4:
        flush(); cur = []
    cur.append(w); prev = w["end"]
flush()
print("\n".join(out))
