"""hflib — ตัวช่วยสร้าง filter / HyperFrames html / SFX schedule สำหรับ reel-cut

ใช้จาก gen.py ของแต่ละคลิป (รันใน WORK dir ที่มี seg.json):
    import sys; sys.path.insert(0, "<REEL>/scripts"); from hflib import *
    S, T = init()                # อ่าน seg.json (ต้องรับ T คืนเอง ไม่งั้น T=0)
    ...นิยามเนื้อหา (E, W, scene/grp)...
    write_filters(face_y=1140)   # cut_grade_filter.txt (ผ่านเดียว: ตัด+ปรับแสง)
    write_page(body, js)         # hf/index.html
    write_sfx(sched)             # sfx_sched.json
คลิปใหม่เขียนแค่ "เนื้อหา" ประมาณ 40–80 บรรทัด ไม่ต้องก๊อป css/filter/helper ซ้ำ
"""
import json

S = []
T = 0.0
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from reelprofile import load as _load_profile, hex_to_int as _hex_to_int, darken as _darken
PROFILE = _load_profile()          # โปรไฟล์ผู้ใช้ (สีเน้น ธีม ข้อความท้ายคลิป ฯลฯ) — ดู reelprofile.py
ACCENT = PROFILE["accent"]


def init(seg="seg.json"):
    global S, T
    S = [tuple(x) for x in json.load(open(seg))]
    T = round(sum(b - a for a, b in S), 2)
    return S, T


def m(t):
    """เวลาต้นฉบับ -> เวลาหลังตัด"""
    o = 0
    for a, b in S:
        if a - 0.001 <= t <= b + 0.001:
            return round(o + t - a, 2)
        o += b - a
    o = 0
    for a, b in S:
        if t < a:
            return round(o, 2)
        o += b - a
    return round(o, 2)


# ---------------------------------------------------------------- filters
def cut_filter(zoom_y=90, zoom_min_gap=None):
    """trim/zoom/concat -> [cv] (วิดีโอ) และ [a] (เสียงผ่าน highpass+afftdn)
    ซูม 1.1 สลับทุกท่อน (zoom_min_gap=None, ค่าเดิม) หรือสลับเฉพาะจุดที่ตัดช่วงยาวกว่า zoom_min_gap วินาที"""
    p = []
    z = False
    prev_end = None
    for i, (a, b) in enumerate(S):
        if i > 0 and (zoom_min_gap is None or a - prev_end > zoom_min_gap):
            z = not z
        prev_end = b
        p.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30"
                 + (f",scale=1188:2112,crop=1080:1920:54:{zoom_y}" if z else "") + f",setsar=1[v{i}]")
        p.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.025,"
                 f"afade=t=out:st={b - a - 0.035:.3f}:d=0.035[a{i}]")
    n = len(S)
    p.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ac]")
    p.append("[ac]highpass=f=80,afftdn=nf=-28[a]")
    return ";\n".join(p)


def grade_filter(src="cv"):
    """ยกแสงหน้า (RGB เท่านั้น) — ต้องมี input 1 = mask.png (-loop 1)"""
    G = "curves=master='0/0 0.25/0.285 0.5/0.545 0.75/0.785 1/0.99'"
    F = ("curves=master='0/0 0.2/0.26 0.4/0.5 0.6/0.68 0.8/0.86 1/1'"
         ":r='0/0 0.5/0.515 1/1':b='0/0 0.5/0.49 1/1'")
    SM = "format=yuv444p,smartblur=lr=1.5:ls=0.35:lt=-3,format=gbrp"
    return (f"[{src}]format=gbrp,{G},split=2[base][f0];[f0]{F},{SM},format=rgba[face];"
            "[1:v]format=gray,scale=1080:1920[mk];[face][mk]alphamerge=shortest=1[fa];"
            "[base]format=rgba[b2];[b2][fa]overlay=format=rgb:shortest=1,format=yuv420p[v]")


def write_filters(face_y=1140, zoom_y=90, grade=True, zoom_min_gap=None):
    """เขียน cut_grade_filter.txt + mask.geq (ผ่านเดียว ไม่มี cutA.mov กลางทาง)
    grade=False -> ไม่ปรับแสง (output [v] = [cv])"""
    f = cut_filter(zoom_y, zoom_min_gap)
    f += ";\n" + (grade_filter() if grade else "[cv]null[v]")
    open("cut_grade_filter.txt", "w").write(f)
    open("mask.geq", "w").write(
        f"format=gray,geq=lum='255*clip(1.6-1.6*sqrt(pow((X-540)/430,2)+pow((Y-{face_y})/560,2)),0,1)'")


# ---------------------------------------------------------------- html
FONTS = '''      @font-face { font-family: "KanitHF"; src: url("Kanit-Bold.ttf") format("truetype"); font-weight: 700; }
      @font-face { font-family: "KanitHF"; src: url("Kanit-SemiBold.ttf") format("truetype"); font-weight: 600; }'''

_CSS = '''      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
      #root { position: relative; width: 1080px; height: 1920px; font-family: "KanitHF", sans-serif; }
      #footage { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }
      .layer { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; pointer-events: none; }
      %SHADOW%
      .t { position: absolute; color: %FG%; font-weight: 700; line-height: 1.15; white-space: nowrap; }
      .c { left: 0; width: 1080px; text-align: center; }
      .m { color: %ACC%; }
      .row { position: absolute; left: 80px; font-size: 70px; font-weight: 700; white-space: nowrap; color: %FG%; }
      .num { color: %ACC%; display: inline-block; width: 68px; }
      .txt { display: inline-block; }
      sub, sup { font-size: .55em; }
      .cav { font-family: Caveat, cursive; font-weight: 600; }
      #barbg { position: absolute; left: 0; top: 0; width: 1080px; height: 10px; background: rgba(255,255,255,.25); }
      #bar { position: absolute; left: 0; top: 0; width: 1080px; height: 10px; background: %ACC%; transform-origin: 0 50%; transform: scaleX(0); }'''

THEMES = {
    # ผนังเทา/มืด -> ตัวขาว เงาดำ
    "light": ("#fff", ".t, .row, .sh { text-shadow: 0 0 3px rgba(0,0,0,.75), 0 4px 14px rgba(0,0,0,.6), 0 10px 40px rgba(0,0,0,.35); }"),
    # ผนังขาว -> ตัวดำ เรืองขาว
    # สเก็ตช์ปกชีท: ตัวกรมท่าบนพื้นสว่าง เรืองขาว
    "sketch": ("#1d3557", ".t, .row, .sh { text-shadow: 0 0 2px rgba(255,255,255,.95), 0 0 12px rgba(255,255,255,.8), 0 4px 18px rgba(255,255,255,.6); }"),
    "dark": ("#161616", ".t, .row, .sh { text-shadow: 0 0 2px rgba(255,255,255,.95), 0 0 12px rgba(255,255,255,.8), 0 4px 18px rgba(255,255,255,.6); }"),
}
FG = "#fff"


def _extra_fonts():
    """ฟอนต์เสริมของสไตล์สเก็ตช์ปกชีท: ใส่ @font-face เมื่อมีไฟล์ใน hf/ (setup_work.sh คัดลอกให้)"""
    import os
    out = ""
    if os.path.exists("hf/Caveat.ttf"):
        out += '\n      @font-face { font-family: "Caveat"; src: url("Caveat.ttf") format("truetype"); font-weight: 400 700; }'
    if os.path.exists("hf/NotoSansThai.ttf"):
        out += '\n      @font-face { font-family: "NotoSansThaiHF"; src: url("NotoSansThai.ttf") format("truetype"); font-weight: 100 900; }'
    return out


def css(theme="light"):
    global FG
    FG, shadow = THEMES[theme]
    return FONTS + _extra_fonts() + "\n" + _CSS.replace("%SHADOW%", shadow).replace("%FG%", FG).replace("%ACC%", ACCENT)


def open_root(theme="light", head=""):
    return f'''<!doctype html>
<html lang="th" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
{head}    <style>
{css(theme)}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1080" data-height="1920">
      <video id="footage" class="clip" src="cut3v.mp4" data-start="0" data-duration="{T}" data-track-index="0" muted playsinline></video>
      <div id="progress" class="clip layer" data-start="0" data-duration="{T}" data-track-index="5"><div id="barbg"></div><div id="bar"></div></div>
'''


def close_root():
    return "    </div>\n"


def grp(gid, start, end, items, track=3):
    """กลุ่มข้อความ: items=(id, class, top, size, html, extra_style)"""
    s = f'      <div id="{gid}" class="clip layer" data-start="{start}" data-duration="{round(end - start, 2)}" data-track-index="{track}">\n'
    for iid, cls, top, size, html, extra in items:
        s += f'        <div class="t c {cls}" id="{iid}" style="top:{top}px;font-size:{size}px;{extra}">{html}</div>\n'
    return s + '      </div>\n'


def scene(W, nn, title, inner):
    """ฉากโฟกัสต่อข้อ: หัวเล็ก + inner (svg/ข้อความ) ; W={n:(เริ่ม,จบ)}"""
    A, B = W[nn]
    return f'''      <div id="h{nn}" class="clip layer" data-start="{A}" data-duration="{round(B - A, 2)}" data-track-index="6"><div class="t c" id="h{nn}t" style="top:240px;font-size:60px;"><span class="m">{nn}</span> · {title}</div></div>
      <div id="d{nn}" class="clip layer" data-start="{A}" data-duration="{round(B - A, 2)}" data-track-index="7">
{inner}      </div>
'''


# รูป SVG กลางจอ 616x300 + marker ลูกศร (id ต้องไม่ซ้ำข้ามฉาก: ahw, ahw3, ...)
SV = '<svg width="616" height="300" viewBox="0 0 560 272" style="position:absolute;left:232px;top:320px;overflow:visible;filter:drop-shadow(0 4px 10px rgba(0,0,0,.5));">'


def marker(mid="ahw"):
    return (f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#fff"/></marker></defs>')


# ---------------------------------------------------------------- gsap js
def js_open():
    return f'''    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const popL = (s, at) => tl.fromTo(s, {{ opacity: 0, x: -40, scale: 0.85, transformOrigin: "0% 50%" }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.3, ease: "back.out(2)" }}, at);
      tl.fromTo("#bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {T}, ease: "none" }}, 0);
'''


def js_close():
    return f'''      tl.set({{}}, {{}}, {T});
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''


def pop(tid, at):
    return f'      tl.fromTo("#{tid}", {{ opacity: 0, scale: 0.6, y: 24, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.32, ease: "back.out(2)" }}, {at});\n'


def fin(tid, at):
    return f'      tl.fromTo("#{tid}", {{ opacity: 0, scale: 0.7, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {at});\n'


def fout(tid, at):
    return f'      tl.to("#{tid}", {{ opacity: 0, duration: 0.12 }}, {round(at, 2)});\n'


def wrap(nn, A, B, last=False):
    """เข้า/ออกฉากโฟกัส: รายการหาย -> หัวขึ้น -> ... -> ฉากหาย -> รายการกลับ"""
    j = f'      tl.to("#list", {{ opacity: 0, duration: 0.2 }}, {round(A - 0.05, 2)});\n'
    j += f'      tl.fromTo("#h{nn}t", {{ opacity: 0, y: -16 }}, {{ opacity: 1, y: 0, duration: 0.25 }}, {A});\n'
    j += f'      tl.to(["#d{nn}", "#h{nn}"], {{ opacity: 0, duration: 0.2 }}, {round(B - 0.2, 2)});\n'
    if not last:
        j += f'      tl.to("#list", {{ opacity: 1, duration: 0.2 }}, {round(B - 0.1, 2)});\n'
    return j


def write_page(body, js, theme_unused=None, path="hf/index.html"):
    open(path, "w").write(body + js)


def write_sfx(sched, path="sfx_sched.json"):
    """sched = [(ชื่อ sfx, เวลา, dB), ...]  ชื่อ: whoosh pop boing ding impact ping"""
    json.dump({"sched": sched, "T": T}, open(path, "w"))


# ================================================================ คอมโพเนนต์ฉากฟิสิกส์
# แต่ละตัวคืน (html, js[, module_script]) — เรียก wrap(nn, A, B) เองเพื่อเข้า/ออกฉาก
# ตำแหน่งในจอ: หัวเรื่องเล็ก top≈240, รูปกลางจอ ≈ top 300–700, ข้อความ 1 บรรทัด top≈700–760 (เหนือหัว)
def _caps(nn, caps, top, size=70):
    """caps=[(html, เวลาเข้า, เวลาออก|None)] -> (html, js)"""
    h = js = ""
    for i, (txt, tin, tout) in enumerate(caps):
        cid = f"c{nn}_{i}"
        h += f'        <div class="t c" id="{cid}" style="top:{top}px;font-size:{size}px;opacity:0;">{txt}</div>\n'
        js += fin(cid, tin)
        if tout is None and i + 1 < len(caps):      # ไม่ระบุเวลาออก = ออกก่อนข้อความถัดไปเข้า (กันทับกัน)
            tout = caps[i + 1][1] - 0.12
        if tout is not None:
            js += fout(cid, tout)
    return h, js


_ARROW_JS = """function hfArrow(x1,y1,x2,y2,h){h=h||24;var dx=x2-x1,dy=y2-y1,l=Math.hypot(dx,dy);if(l<8)return'';var ux=dx/l,uy=dy/l;
  return 'M'+x1+' '+y1+'L'+x2+' '+y2+'M'+(x2-ux*h+uy*h*.55)+' '+(y2-uy*h-ux*h*.55)+'L'+x2+' '+y2+'L'+(x2-ux*h-uy*h*.55)+' '+(y2-uy*h+ux*h*.55);}"""

_PJ_JS = """
      var pj%NN% = {t:0}, PJ%NN% = {x0:60,y0:490,vx:%VX%,vy:%VY%,g:%G%,T:%TT%};
      %ARROW%
      function pjUpd%NN%(){var P=PJ%NN%,t=pj%NN%.t,x=P.x0+P.vx*t,y=P.y0-(P.vy*t-.5*P.g*t*t);
        var n=Math.max(2,Math.ceil(t/P.T*60)),d='M'+P.x0+' '+P.y0,i,tt;
        for(i=1;i<=n;i++){tt=t*i/n;d+='L'+(P.x0+P.vx*tt)+' '+(P.y0-(P.vy*tt-.5*P.g*tt*tt));}
        document.getElementById('pjt%NN%').setAttribute('d',d);
        var b=document.getElementById('pjb%NN%');b.setAttribute('cx',x);b.setAttribute('cy',y);
        document.getElementById('pjx%NN%').setAttribute('d',hfArrow(x,y,x+120,y));
        document.getElementById('pjy%NN%').setAttribute('d',hfArrow(x,y,x,y-(P.vy-P.g*t)*.16));}
      tl.fromTo("#pjs%NN%", { opacity: 0 }, { opacity: 1, duration: 0.3 }, %A%);
      tl.to(pj%NN%, { t: PJ%NN%.T, duration: %DUR%, ease: "none", onUpdate: pjUpd%NN% }, %LAUNCH%);
      pjUpd%NN%();
"""


def projectile(W, nn, title, launch, dur=2.2, caps=(), fg="#fff", vx=560, vy=640, g=1000):
    """ฉากโพรเจกไทล์ (2D) — ตำแหน่งคำนวณจากสมการ x=vₓt, y=v_y t−½gt² ไม่ใช่ easing เดา
    เส้นทางวาดจาก t โดยตรง (seek ได้ ไม่สะสมสถานะ) · ลูกศร vₓ คงที่ (ขาว), v_y เปลี่ยนตามเวลา (ม่วงแดง)
    launch = เวลา (หลังตัด) ที่เริ่มปล่อย ; dur = ความยาวช่วงบิน (slow-mo ได้) ; caps=[(html,เข้า,ออก|None)]
    คืน (html, js)"""
    A, B = W[nn]
    TT = round(2 * vy / g, 4)
    svg = (f'<svg id="pjs{nn}" width="760" height="280" viewBox="20 220 840 310" '
           f'style="position:absolute;left:160px;top:330px;overflow:visible;filter:drop-shadow(0 4px 10px rgba(0,0,0,.5));">'
           f'<line x1="20" y1="490" x2="860" y2="490" stroke="{fg}" stroke-width="8" stroke-linecap="round" opacity="0.6"/>'
           f'<path id="pjt{nn}" d="" fill="none" stroke="{ACCENT}" stroke-width="10" stroke-linecap="round" stroke-dasharray="2 20"/>'
           f'<path id="pjx{nn}" d="" fill="none" stroke="{fg}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<path id="pjy{nn}" d="" fill="none" stroke="{ACCENT}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<circle id="pjb{nn}" cx="60" cy="490" r="26" fill="{fg}"/></svg>\n')
    ch, cj = _caps(nn, caps, 700)
    html = scene(W, nn, title, "        " + svg + ch)
    js = (_PJ_JS.replace("%NN%", str(nn)).replace("%VX%", str(vx)).replace("%VY%", str(vy)).replace("%G%", str(g))
          .replace("%TT%", str(TT)).replace("%ARROW%", _ARROW_JS).replace("%A%", str(A))
          .replace("%DUR%", str(dur)).replace("%LAUNCH%", str(launch)))
    return html, js + cj


_M3_MODULE = """    <script type="module">
      import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.181.2/+esm";
      const A0 = %A%, CW = %CW%, CH = %CH%;
      const canvas = document.getElementById("m3c%NN%");
      const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
      renderer.setPixelRatio(1); renderer.setSize(CW, CH, false);
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(42, CW / CH, 0.1, 50);
      scene.add(new THREE.AmbientLight(0xffffff, 1.0));
      const dl = new THREE.DirectionalLight(0xffffff, 1.5); dl.position.set(3, 5, 4); scene.add(dl);
      const wire = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 3, 24), new THREE.MeshStandardMaterial({ color: 0xdddddd, metalness: 0.4, roughness: 0.4 }));
      wire.position.y = 1.2; scene.add(wire);
      const mag = new THREE.MeshStandardMaterial({ color: %ACC0X%, emissive: %ACCDARK% });
      const wht = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x333333 });
      const I = [0, 1, 2].map(() => { const c = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.4, 20), mag); scene.add(c); return c; });
      const ys = [0.4, 1.2, 2.0], rad = [0.8, 1.0, 0.8], cones = [];
      ys.forEach((y, i) => {
        const ring = new THREE.Mesh(new THREE.TorusGeometry(rad[i], 0.012, 8, 80), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.35 }));
        ring.rotation.x = Math.PI / 2; ring.position.y = y; scene.add(ring);
        for (let k = 0; k < 6; k++) { const c = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.24, 16), wht); scene.add(c); cones.push({ c, y, R: rad[i], th0: k * Math.PI / 3 }); }
      });
      const up = new THREE.Vector3(0, 1, 0), tan = new THREE.Vector3();
      function renderAt(time) {
        const t = Math.max(0, time - A0);
        const a = 0.35 + t * 0.45;
        camera.position.set(Math.cos(a) * 3.5, 2.3, Math.sin(a) * 3.5); camera.lookAt(0, 1.2, 0);
        I.forEach((c, i) => { const p = (t * 0.5 + i / 3) %% 1; c.position.set(0, -0.2 + p * 3.2, 0); c.scale.setScalar(Math.sin(Math.PI * p) * 0.9 + 0.1); });
        cones.forEach(o => { const th = o.th0 + t * 0.7; o.c.position.set(o.R * Math.cos(th), o.y, -o.R * Math.sin(th));
          tan.set(-Math.sin(th), 0, -Math.cos(th)); o.c.quaternion.setFromUnitVectors(up, tan); });
        renderer.render(scene, camera);
      }
      window.addEventListener("hf-seek", (e) => renderAt(e.detail.time));
      renderAt(window.__hfThreeTime || 0);
    </script>
"""


def magnetic3d(W, nn, title, caps=(), w=700, h=520):
    """ฉาก 3 มิติ: สนามแม่เหล็กรอบเส้นลวดตรง (กฎมือขวา: I ขึ้น → B หมุนทวนเข็มเมื่อมองจากด้านบน)
    Three.js เรนเดอร์ตามเวลา hf-seek (ไม่ใช้ wall-clock) · กล้องหมุนรอบเส้นลวดตามเวลา
    คืน (html, js, module_script) — ต่อ module_script ท้าย body (หลัง close_root()) ก่อน js"""
    A, B = W[nn]
    canvas = (f'<canvas id="m3c{nn}" width="{w}" height="{h}" '
              f'style="position:absolute;left:{(1080 - w) // 2}px;top:345px;width:{w}px;height:{h}px;"></canvas>\n')
    ch, cj = _caps(nn, caps, 850)
    html = scene(W, nn, title, "        " + canvas + ch)
    mod = _M3_MODULE.replace("%ACC0X%", "0x%06X" % _hex_to_int(ACCENT)).replace("%ACCDARK%", "0x%06X" % _darken(ACCENT)).replace("%A%", str(A)).replace("%CW%", str(w)).replace("%CH%", str(h)).replace("%NN%", str(nn)).replace("%%", "%")
    return html, cj, mod


# ================================================================ พาเลต/คอมโพเนนต์สไตล์ "สเก็ตช์ปกชีท" (+ เฟรมต่อเฟรม on threes)
SKETCH = dict(ink="#1d3557", accent=ACCENT, orange="#e07b24", peach="#fbe3cf", peach2="#f6d2b5", gray="#5b6577")

_ROUGH_JS = """function hfH(a,b){var x=Math.sin(a*127.1+b*311.7)*43758.5453;return x-Math.floor(x)-.5;}
      function hfRough(pts,fi,seed,close,J){J=J||3.2;var d='',k=0;
        function seg(a,b){var len=Math.hypot(b[0]-a[0],b[1]-a[1]),m=Math.max(1,Math.ceil(len/60)),i,x,y;
          for(i=0;i<=m;i++){x=a[0]+(b[0]-a[0])*i/m+hfH(fi+seed,k)*2*J;y=a[1]+(b[1]-a[1])*i/m+hfH(fi+seed,k+99)*2*J;d+=(d?'L':'M')+x.toFixed(1)+' '+y.toFixed(1);k++;}}
        for(var i=0;i<pts.length-1;i++)seg(pts[i],pts[i+1]);if(close)seg(pts[pts.length-1],pts[0]);return d;}"""

_INC_JS = """
      %ROUGH%
      var inc%NN% = {t:0}, INC%NN% = {th:%TH%,fps:%FPS%,dur:%DUR%};
      function incDraw%NN%(){var I=INC%NN%,fi=Math.floor(inc%NN%.t*I.fps+1e-6),tq=fi/I.fps,r=Math.PI/180,
          u=[Math.cos(I.th*r),Math.sin(I.th*r)],nn=[Math.sin(I.th*r),-Math.cos(I.th*r)],R=46,
          Q0=[60,40],run=600,Q1=[60+run,40+run*Math.tan(I.th*r)],Q2=[60,Q1[1]],Lh=run/Math.cos(I.th*r),
          smax=Lh-80,a=2*smax/(I.dur*I.dur),s=Math.min(.5*a*tq*tq+40,smax+40),
          c=[Q0[0]+u[0]*s+nn[0]*R,Q0[1]+u[1]*s+nn[1]*R],e=[c[0]+u[0]*150,c[1]+u[1]*150],h=30,ang=Math.atan2(u[1],u[0]),
          hd=function(da){return [e[0]-Math.cos(ang+da)*h,e[1]-Math.sin(ang+da)*h];},i,ring=[],hh=[];
        document.getElementById('insT%NN%').setAttribute('d',hfRough([Q0,Q1,Q2],fi,1,true));
        document.getElementById('insG%NN%').setAttribute('d',hfRough([[0,Q1[1]+6],[760,Q1[1]+6]],fi,5));
        for(i=0;i<10;i++){hh.push('M'+(20+i*76)+' '+(Q1[1]+30)+'L'+(20+i*76-30)+' '+(Q1[1]+64));}
        document.getElementById('insH%NN%').setAttribute('d',hh.join(''));
        for(i=0;i<14;i++){var q=i/14*2*Math.PI,rr=R+hfH(fi+7,i)*6;ring.push((c[0]+Math.cos(q)*rr).toFixed(1)+' '+(c[1]+Math.sin(q)*rr).toFixed(1));}
        document.getElementById('insB%NN%').setAttribute('d','M'+ring.join('L')+'Z');
        document.getElementById('insA%NN%').setAttribute('d',hfRough([c,e],fi,11)+'M'+hd(.45).join(' ')+'L'+e.join(' ')+'L'+hd(-.45).join(' '));
        var L=document.getElementById('insL%NN%');L.style.left=(%SL%+(e[0]+14)*%K%)+'px';L.style.top=(%ST%+(e[1]-34)*%K%)+'px';
        var T=document.getElementById('insTh%NN%');T.style.left=(%SL%+(Q1[0]-110)*%K%)+'px';T.style.top=(%ST%+(Q1[1]-70)*%K%)+'px';}
      tl.fromTo("#ins%NN%", { opacity: 0 }, { opacity: 1, duration: 0.3 }, %A%);
      tl.to(inc%NN%, { t: %DUR%, duration: %DUR%, ease: "none", onUpdate: incDraw%NN% }, %START%);
      incDraw%NN%();
"""


def incline(W, nn, title, start, dur=3.6, theta=30, fps=10, caps=(), palette=None, label="mg sin θ"):
    """บอลไถลพื้นเอียง (2D) สไตล์ "เฟรมต่อเฟรม on threes": ทุกอย่างคำนวณจากเวลา t ล้วนๆ (seek ได้)
    - ตำแหน่ง s=½at² ค้างทีละ 1/fps วินาที (fps=10 ≈ on threes ที่ 30fps) ; เส้นสั่นด้วย hash(หมายเลขเฟรม) ไม่ใช้ SVG filter
    - ลูกศรสีเน้น = องค์ประกอบของ mg ตามแนวพื้นเอียง (mg sinθ) ยาวคงที่ ; ป้ายลายมือใช้คลาส .cav (ต้องมีฟอนต์ Caveat)
    start = เวลาเริ่มไถล (หลังตัด) ; dur = ระยะเวลาไถล ; คืน (html, js) — เรียก wrap(nn,A,B) เอง"""
    A, B = W[nn]
    pal = dict(SKETCH, **(palette or {}))
    k = 646 / 760.0
    sl, st_ = (1080 - 646) // 2, 350
    svg = (f'<svg id="ins{nn}" width="646" height="442" viewBox="0 0 760 520" style="position:absolute;left:{sl}px;top:{st_}px;overflow:visible;">'
           f'<path id="insT{nn}" d="" fill="{pal["peach"]}" stroke="{pal["ink"]}" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>'
           f'<path id="insH{nn}" d="" fill="none" stroke="{pal["ink"]}" stroke-width="4" opacity="0.5" stroke-linecap="round"/>'
           f'<path id="insG{nn}" d="" fill="none" stroke="#b9c0cc" stroke-width="7" stroke-linecap="round"/>'
           f'<path id="insB{nn}" d="" fill="#fff" stroke="{pal["ink"]}" stroke-width="9" stroke-linejoin="round"/>'
           f'<path id="insA{nn}" d="" fill="none" stroke="{pal["accent"]}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg>\n')
    lab = (f'        <div class="t cav" id="insL{nn}" style="left:0;top:0;font-size:60px;color:{pal["accent"]};">{label}</div>\n'
           f'        <div class="t cav" id="insTh{nn}" style="left:0;top:0;font-size:60px;color:{pal["orange"]};">θ</div>\n')
    ch, cj = _caps(nn, caps, 810)
    html = scene(W, nn, title, "        " + svg + lab + ch)
    js = (_INC_JS.replace("%ROUGH%", _ROUGH_JS).replace("%NN%", str(nn)).replace("%TH%", str(theta)).replace("%FPS%", str(fps))
          .replace("%DUR%", str(dur)).replace("%A%", str(A)).replace("%START%", str(start))
          .replace("%SL%", str(sl)).replace("%ST%", str(st_)).replace("%K%", str(round(k, 4))))
    return html, js + cj
