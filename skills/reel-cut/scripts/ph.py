"""หาเวลาวลี: python3 ph.py <transcript.json> "วลี@เวลาเริ่มค้น" ..."""
import json, sys
d = json.load(open(sys.argv[1]))
s = ""; mp = []
for w in d["words"]:
    if w["type"] != "word": continue
    for ch in w["text"]:
        s += ch; mp.append((w["start"], w["end"]))
def find(p, after=0):
    i = 0
    while True:
        i = s.find(p, i)
        if i < 0: return None
        if mp[i][0] >= after: return (mp[i][0], mp[i + len(p) - 1][1])
        i += 1
for q in sys.argv[2:]:
    p, a = q.split("@") if "@" in q else (q, 0)
    print(q, find(p, float(a)))
