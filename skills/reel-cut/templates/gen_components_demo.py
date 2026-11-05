"""ตัวอย่างใช้คอมโพเนนต์ฟิสิกส์ (2D โพรเจกไทล์ + 3D สนามแม่เหล็ก) — ต้องมี seg.json
รัน: cd $WORK && REEL_SCRIPTS=$REEL/scripts python3 -I gen_components_demo.py
"""
import os, sys
sys.path.insert(0, os.environ["REEL_SCRIPTS"])
from hflib import *

S, T = init()
W = {1: (1.0, 6.0), 2: (6.4, 11.4)}            # เวลาช่วงของแต่ละฉาก (หลังตัด)

p_html, p_js = projectile(W, 1, "โพรเจกไทล์", launch=1.8, dur=2.4,
                          caps=[('แนวราบ <span class="m">v คงที่</span>', 3.0, None),
                                ('แนวดิ่ง <span class="m">a = g</span>', 4.4, None)])
m_html, m_js, m_mod = magnetic3d(W, 2, "สนามแม่เหล็ก",
                                 caps=[('<span class="m">I</span> ขึ้น · <span class="m">B</span> วนรอบ', 7.4, None)])

body = (open_root("light")
        + '      <div id="list" class="clip layer" data-start="0" data-duration="%s" data-track-index="2"></div>\n' % T
        + p_html + m_html + close_root() + m_mod)
js = js_open() + wrap(1, *W[1]) + p_js + wrap(2, *W[2], last=True) + m_js + js_close()
write_page(body, js)
write_filters(face_y=1140)
