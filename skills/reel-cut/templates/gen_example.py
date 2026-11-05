"""ตัวอย่าง gen.py (คลิปแนว "3 ข้อที่ต้องทำ" + ช่วงชวนสมัคร/ติดตามท้ายคลิป) ที่ใช้ hflib
เวลาใน E เป็นของคลิปตัวอย่าง — ต้องหาเวลาใหม่จากทรานสคริปต์ของคลิปคุณ (ph.py) และแก้ข้อความทุกจุดให้ตรงกับที่พูดจริง
คัดลอกเป็น $WORK/gen.py แล้วแก้เฉพาะ "เนื้อหา": เวลาใน E (ใช้ m(เวลาต้นฉบับ)), ข้อความ, SVG, sfx
รัน:  cd $WORK && python3 -I gen.py        (ต้องมี seg.json ในโฟลเดอร์)
ผลลัพธ์: cut_grade_filter.txt, mask.geq, hf/index.html, sfx_sched.json, events.json
"""
import sys, os, json
sys.path.insert(0, os.environ.get("REEL_SCRIPTS", os.path.expanduser("~")))  # ตั้ง REEL_SCRIPTS=<REEL>/scripts
from hflib import *

S, T = init()   # ต้องรับ T คืนเสมอ (from hflib import * คัดลอก T ตอน import = 0.0)
# ---- 1) เวลาเหตุการณ์ (เวลาต้นฉบับ -> หลังตัดด้วย m()) -----------------------------------
E = dict(tip1=m(4.82), tip2=m(28.12), tip3=m(43.54), listStart=m(4.72), listEnd=round(m(69.42) - 0.02, 2),
         sum1=m(10.8), mem=m(14.74), und=m(16.76),
         many=m(29.32), more=m(38.48), better=m(40.16),
         key=m(44.42), right=m(65.08), fast=m(66.04), wrong=m(67.18), fix=m(68.28),
         k1=m(71.34), k1b=m(73.88), k2=m(81.22), k2b=m(83.18), k3=m(98.12), k3b=m(98.96),
         k5=m(124.34), k5b=m(126.96), k5c=m(133.66), k7=m(135.34), k6=m(140.12), k6b=m(141.02), k6c=m(142.96))
W = {1: (round(E['tip1'] + 1.2, 2), round(E['tip2'] - 0.08, 2)),
     2: (round(E['tip2'] + 1.0, 2), round(E['tip3'] - 0.08, 2)),
     3: (round(E['tip3'] + 0.9, 2), E['listEnd'])}
print(T, E, W)
json.dump({"T": T, "E": E, "W": W}, open('events.json', 'w'))
sc = lambda nn, title, inner: scene(W, nn, title, inner)

# ---- 2) ฉากโฟกัสต่อข้อ (SVG ขาวเรียบ + ข้อความ 1 บรรทัด) ----------------------------------
lines = "".join(f'<rect class="ln" x="215" y="{70 + i * 36}" width="{[150, 120, 160, 100, 140][i]}" height="10" rx="5" fill="#fff"/>' for i in range(5))
s1 = sc(1, "ข้อที่หนึ่ง", f'''        {SV}
          <rect x="170" y="30" width="220" height="240" rx="14" fill="none" stroke="#fff" stroke-width="8"/>
          <line x1="200" y1="30" x2="200" y2="270" stroke="{ACCENT}" stroke-width="5"/>
          {lines}
        </svg>
        <div class="t c" id="e1a" style="top:650px;font-size:80px;opacity:0;"><span class="m">จำ</span>ได้มากขึ้น</div>
        <div class="t c" id="e1b" style="top:650px;font-size:80px;opacity:0;"><span class="m">เข้าใจ</span>สูตรมากขึ้น</div>
''')
bars = "".join(f'<rect class="bar" x="{120 + i * 90}" y="{250 - h}" width="60" height="{h}" rx="8" fill="#fff"/>' for i, h in enumerate([50, 90, 140, 200]))
s2 = sc(2, "ข้อที่สอง", f'''        {SV}
          {marker("ahw")}
          <line x1="90" y1="252" x2="490" y2="252" stroke="#fff" stroke-width="5" opacity="0.6"/>
          {bars}
          <g id="up" opacity="0"><line x1="130" y1="200" x2="440" y2="20" stroke="{ACCENT}" stroke-width="10" stroke-linecap="round" marker-end="url(#ahw)"/></g>
        </svg>
        <div class="t c" id="e2a" style="top:650px;font-size:80px;opacity:0;">ทำมาก = <span class="m">เก่งมาก</span></div>
''')
s3 = sc(3, "ข้อที่สาม", '''        <div class="t" id="ck" style="left:250px;top:360px;font-size:170px;opacity:0;">✓</div>
        <div class="t m" id="cx" style="left:660px;top:360px;font-size:170px;opacity:0;">✗</div>
        <div class="t c" id="e3a" style="top:650px;font-size:76px;opacity:0;">ดูทั้งข้อ<span class="m">ถูก</span>และข้อ<span class="m">ผิด</span></div>
        <div class="t c" id="e3b" style="top:650px;font-size:76px;opacity:0;">ข้อถูก → <span class="m">มีวิธีเร็วกว่าไหม?</span></div>
        <div class="t c" id="e3c" style="top:650px;font-size:76px;opacity:0;">ข้อผิด → <span class="m">ทำยังไงให้ถูก?</span></div>
''')

# ---- 3) ช่วงท้ายคลิป (ชวนทำต่อ/ติดตาม/สมัคร): กลุ่มข้อความต่อจังหวะพูด ----------------------
# ข้อความในวงเล็บเหลี่ยม = ที่ว่างให้ใส่ "สิ่งที่ผู้พูดพูดจริง" ห้ามแต่งข้อเท็จจริงเพิ่ม (ราคา วัน จำนวนที่นั่ง ฯลฯ)
K = E
order = ["k1", "k2", "k3", "k5", "k7", "k6"]
end = lambda k: K[order[order.index(k) + 1]] if k != "k6" else T
H = PROFILE["cta_handle"] or "@ชื่อช่อง"
groups = ""
groups += grp("k1", K['k1'], end("k1"), [("k1a", "", 410, 74, "[ประโยคชวน/คำถามนำ]", ""), ("k1c", "", 530, 80, '[ชื่อสิ่งที่เสนอ] <span class="m">[จุดเด่น]</span>', "")])
groups += grp("k2", K['k2'], end("k2"), [("k2a", "", 430, 88, '[ประโยคที่ 2] <span class="m">[คำเน้น]</span>', ""), ("k2c", "", 560, 72, "[คำอธิบายสั้น]", "font-weight:600;")])
groups += grp("k3", K['k3'], end("k3"), [("k3a", "", 450, 72, "[ประโยคที่ 3]", ""), ("k3c", "", 560, 96, '[คำเน้น] <span class="m">[คำเน้นสี]</span>', "")])
groups += grp("k5", K['k5'], end("k5"), [("k5a", "", 400, 80, "[วัน/เวลา ถ้าพูด]", ""), ("k5b", "", 515, 80, "[รายละเอียด]", ""), ("k5c", "m", 640, 100, "[วันเริ่ม]", "")])
groups += grp("k7", K['k7'], end("k7"), [("k7a", "", 430, 84, "[นำ]", ""), ("k7b", "m", 545, 130, "[ตัวเลข/คำสำคัญ]", "")])
groups += grp("k6", K['k6'], end("k6"), [("k6a", "", 410, 76, "ติดตามได้ที่", ""), ("k6b", "m", 520, 104, H, ""), ("k6c", "", 660, 72, PROFILE["cta_end"], "font-weight:600;")])

# ---- 4) html: hook + รายการ + ฉาก + กลุ่ม --------------------------------------------------
body = open_root("sketch" if PROFILE["wall"] == "light" else "light") + f'''      <div id="hook" class="clip layer" data-start="0" data-duration="{E['listStart']}" data-track-index="1">
        <div class="t c m" id="h1x" style="top:370px;font-size:96px;">{PROFILE["series"] or "ชื่อซีรีส์"}</div>
        <div class="t c" id="h2x" style="top:485px;font-size:124px;">หัวเรื่องคลิป</div>
        <div class="t c" id="h3x" style="top:650px;font-size:62px;font-weight:600;">ต้องทำ <span class="m">3 อย่างนี้!</span></div>
      </div>
      <div id="list" class="clip layer" data-start="{E['listStart']}" data-duration="{round(E['listEnd'] - E['listStart'], 2)}" data-track-index="2">
        <div class="row" id="r1" style="top:300px;"><span class="num">1.</span><span class="txt" id="x1">ข้อที่หนึ่ง</span></div>
        <div class="row" id="r2" style="top:410px;"><span class="num">2.</span><span class="txt" id="x2">ข้อที่สอง</span></div>
        <div class="row" id="r3" style="top:520px;"><span class="num">3.</span><span class="txt" id="x3">ข้อที่สาม</span></div>
      </div>
{s1}{s2}{s3}{groups}''' + close_root()

# ---- 5) อนิเมชัน GSAP ---------------------------------------------------------------------
A1, B1 = W[1]; A2, B2 = W[2]; A3, B3 = W[3]
js = js_open()
js += pop("h1x", 0.05) + pop("h2x", 0.4) + pop("h3x", m(2.52))
js += f'      tl.fromTo(".num", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, stagger: 0.06 }}, {E["listStart"]});\n'
js += f'      popL("#x1", {E["tip1"]}); popL("#x2", {E["tip2"]}); tl.to("#r1", {{ opacity: 0.4, duration: 0.25 }}, {E["tip2"]}); popL("#x3", {E["tip3"]}); tl.to("#r2", {{ opacity: 0.4, duration: 0.25 }}, {E["tip3"]});\n'
js += wrap(1, A1, B1)
js += f'      tl.fromTo("#d1 svg", {{ opacity: 0, scale: 0.8, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }}, {A1});\n'
js += f'      tl.fromTo(".ln", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.35, stagger: 0.35, ease: "power1.out" }}, {round(E["sum1"] - 0.6, 2)});\n'
js += fin("e1a", E['mem']) + fout("e1a", E['und'] - 0.12) + fin("e1b", E['und'])
js += wrap(2, A2, B2)
js += f'      tl.fromTo(".bar", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.45, stagger: 0.5, ease: "back.out(1.6)" }}, {round(A2 + 0.2, 2)});\n'
js += f'      tl.fromTo("#up", {{ opacity: 0, scale: 0.3, svgOrigin: "130 200" }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "power2.out" }}, {E["better"]});\n'
js += fin("e2a", E['more'])
js += wrap(3, A3, B3, last=True)
js += fin("ck", A3 + 0.05) + fin("cx", A3 + 0.3) + fin("e3a", A3 + 0.5) + fout("e3a", E['right'] - 0.12) + fin("e3b", E['right']) + fout("e3b", E['wrong'] - 0.12) + fin("e3c", E['wrong'])
js += f'      tl.to("#cx", {{ opacity: 0.35, duration: 0.2 }}, {E["right"]});\n      tl.to("#cx", {{ opacity: 1, duration: 0.2 }}, {E["wrong"]});\n      tl.to("#ck", {{ opacity: 0.35, duration: 0.2 }}, {E["wrong"]});\n'
js += pop("k1a", K['k1']) + pop("k1c", K['k1b']) + pop("k2a", K['k2']) + pop("k2c", K['k2b']) + pop("k3a", K['k3']) + pop("k3c", K['k3b'])
js += pop("k5a", K['k5']) + pop("k5b", K['k5b']) + pop("k5c", K['k5c']) + pop("k7a", K['k7']) + pop("k7b", round(K['k7'] + 0.3, 2))
js += pop("k6a", K['k6']) + pop("k6b", K['k6b']) + pop("k6c", K['k6c'])
js += js_close()

# ---- 6) เขียนไฟล์ ------------------------------------------------------------------------
write_page(body, js)
write_filters(face_y=1140)          # ดู y หน้าจากเฟรม (≈1140–1180)
k7b = round(K['k7'] + 0.3, 2)
write_sfx([("whoosh", 0.0, -6), ("pop", m(2.52), -10), ("pop", E['tip1'], -10), ("pop", E['mem'], -11), ("pop", E['tip2'], -10),
           ("ding", E['better'], -10), ("pop", E['tip3'], -10), ("pop", E['right'], -11), ("boing", E['wrong'], -10),
           ("whoosh", K['k1'], -8), ("ding", K['k1b'], -10), ("pop", K['k2'], -10), ("pop", K['k3b'], -10), ("pop", K['k5'], -10),
           ("ding", K['k5c'], -10), ("impact", round(k7b - 0.26, 2), -8), ("ping", K['k6b'], -8), ("whoosh", K['k6c'], -9)])
