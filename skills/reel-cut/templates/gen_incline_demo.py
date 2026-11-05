"""ตัวอย่างคอมโพเนนต์ incline (สไตล์เฟรมต่อเฟรม on threes) — ต้องมี seg.json
รัน: cd $WORK && REEL_SCRIPTS=$REEL/scripts python3 -I gen_incline_demo.py
ฟอนต์ลายมือ Caveat: ใส่ไฟล์ใน hf/ แล้วเพิ่ม @font-face (ที่นี่ใช้ลิงก์ Google Fonts เพื่อทดสอบ)
"""
import os, sys
sys.path.insert(0, os.environ["REEL_SCRIPTS"])
from hflib import *

S, T = init()
W = {1: (0.8, 7.8)}
html, js = incline(W, 1, "พื้นเอียง", start=1.6, dur=4.0, theta=30, fps=10,
                   caps=[('<span class="m">a</span> = g sin θ', 3.2, None)])
HEAD = '    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@600&display=swap" rel="stylesheet">\n'
body = (open_root("sketch", head=HEAD)
        + '      <div id="list" class="clip layer" data-start="0" data-duration="%s" data-track-index="2"></div>\n' % T
        + html + close_root())
write_page(body, js_open() + wrap(1, *W[1], last=True) + js + js_close())
write_filters(face_y=1140)
