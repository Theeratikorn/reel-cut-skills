---
name: reel-visuals
description: ขั้น 2 ของ reel-cut — สร้าง gen.py (hflib), cut+ปรับแสงหน้าผ่านเดียว, Hook/รายการ/ฉากโฟกัส/ช่วงขายคอร์สด้วย HyperFrames แล้ว lint/snapshot/render (มีโหมดเรียบ ASS) ใช้เมื่อมี seg.json แล้ว
---

# reel-visuals — ภาพ + ข้อความ + อนิเมชัน

## ขั้นตอน
```bash
source "$(ls -d ~/.claude/skills/reel-cut .claude/skills/reel-cut 2>/dev/null | head -1)/scripts/env.sh"      # W = โฟลเดอร์งานจาก reel-edl
cp $REEL/templates/gen_example.py $W/gen.py        # แก้เฉพาะ "เนื้อหา" (E, scene, grp, sfx) ; ต้องมี seg.json
(cd $W && REEL_SCRIPTS=$REEL/scripts python3 -I gen.py)   # -> cut_grade_filter.txt mask.geq hf/index.html sfx_sched.json events.json
bash $REEL/scripts/cut_grade.sh $W                 # ผ่านเดียว -> hf/cut3v.mp4 + voice.wav
(cd $W/hf && npx -y hyperframes lint)              # ต้อง 0 error (warning sub-composition ข้ามได้)
(cd $W/hf && npx -y hyperframes snapshot --at 2.5,10,20,40,55,62 -o snaps)   # แล้วดูเฉพาะ contact sheet ที่สร้าง
(cd $W/hf && npx -y hyperframes render -q delivery -o ../v_video.mp4 --quiet)  # ~4–5 นาที → run_in_background
```
- `hflib` มี: `m(t)`, `grp`, `scene`, `SV`/`marker`, `pop/fin/fout/wrap`, `open_root(theme)`/`close_root`, `js_open/js_close`, `write_filters/page/sfx` — **ห้าม** เขียน css/filter/helper ซ้ำ ผ่านเดียวคือไม่มี cutA.mov
- ธีม `light` = ตัวขาว+เงาดำ (ผนังมืด) / `dark` = `#161616` + เรืองขาว (ผนังขาว) — ใน SVG ของฉากโฟกัสบนธีม dark เปลี่ยน `#fff` เป็น `#161616`
- ระวัง `T`: ต้อง `S, T = init()` (ถ้า `init()` เฉยๆ T = 0)
- ความคืบหน้า `render` อย่าวน poll ใช้ run_in_background

## คลังสไตล์อนิเมชัน
**ค่าเริ่มต้น = "Split Screen · สเก็ตช์ปกชีท"** (สเปก `$REEL/styles/sketch-sheet.md`, พรีวิว `sketch_sheet_preview.html`): บนขาว 1080×960 แผงอนิเมชัน / ล่างวิดีโอครอป y=660, แถบม่วงแดง 10px + ป้ายเม็ดยา, กรมท่า/ม่วงแดง/ส้ม, Noto Sans Thai + Caveat, เส้นดุ๊กดิ๊ก ~7 ครั้ง/วิ (ตัวหนังสือไม่สั่น), เศษส่วนซ้อน
คลังสไตล์อื่นอีก 10 แบบ + ที่ค้นเพิ่ม อยู่ใน `$REEL/styles/README.md` (ใช้เมื่อ ผู้ใช้ สั่งชื่อ/เลข เช่น #4 ลายมือบนกระดาน, #1 โล่งเดิม)
**ยังไม่เคยเรนเดอร์ใน HyperFrames และยังไม่เป็นพรีเซ็ตใน hflib** — ฉากแรกของคลิปจริงให้ทดลอง lint/snapshot ก่อน; ต้องครอปวิดีโอครึ่งล่างด้วย ffmpeg ตอนตัด (ยังไม่มีสคริปต์), boiling line ต้องคุม seed ด้วยเวลา timeline (`floor(t*7)`), Caveat ต้องดาวน์โหลดเข้า `hf/`

## คอมโพเนนต์ฟิสิกส์ (ใช้เมื่อเนื้อหาเป็นวิทยาศาสตร์; ใน hflib — ทดสอบเรนเดอร์ใน HyperFrames แล้ว)
ตัวอย่างใช้งาน: `$REEL/templates/gen_components_demo.py` · ภาพตัวอย่างสไตล์: `$REEL/styles/insert_demos.html`
- `projectile(W, nn, title, launch, dur, caps, fg)` → `(html, js)` — **2D โพรเจกไทล์** ตำแหน่งคำนวณจากสมการ (ไม่ใช่ easing เดา) เส้นทางวาดจาก t โดยตรง seek ได้; `caps=[(html, เวลาเข้า, เวลาออก|None)]` ไม่ระบุเวลาออก = ออกก่อนข้อความถัดไปเข้า; พารามิเตอร์ `vx vy g` ปรับได้
- `magnetic3d(W, nn, title, caps)` → `(html, js, module_script)` — **3D สนามแม่เหล็กรอบเส้นลวด** (Three.js เรนเดอร์ตาม `hf-seek` ไม่ใช้ wall-clock; กฎมือขวา I ขึ้น → B ทวนเข็มเมื่อมองจากบน) ต่อ `module_script` ท้าย body **หลัง** `close_root()`
- `incline(W, nn, title, start, dur, theta, fps, caps, palette)` → `(html, js)` — **2D พื้นเอียง สไตล์ "เฟรมต่อเฟรม on threes" (#12)** ตำแหน่งบอล s=½at² ค้างทีละ 1/fps วินาที (fps=10) เส้นสั่นด้วย hash(หมายเลขเฟรม) **ไม่ใช้ SVG filter/นาฬิกาเบราว์เซอร์** (ทดสอบใน HyperFrames: ภายในสเต็ปเดียวกันภาพเกือบเหมือนกัน PSNR ~65 dB, ข้ามสเต็ป ~24 dB) ใช้ธีม `open_root("sketch")` (ตัวกรมท่า เรืองขาว) + ต้องมีฟอนต์ Caveat (`.cav`) ใน `hf/`; ตัวช่วย `hfRough(pts, frame, seed, close)` ใช้วาดรูปอื่นแบบเดียวกันได้; พาเลต `SKETCH` ใน hflib; ตัวอย่าง `templates/gen_incline_demo.py`
- ทุกตัว: เรียก `wrap(nn, A, B)` เองเพื่อเข้า/ออกฉาก และใส่ `js` ของคอมโพเนนต์หลัง `wrap`
- 3D โหลด three จาก CDN ตอนเรนเดอร์ (ต้องออนไลน์) และเรนเดอร์ช้ากว่า 2D — ใช้เมื่อ 3 มิติช่วยจริงเท่านั้น
- เพิ่มคอมโพเนนต์ใหม่ (คาน ชน วงจร คลื่น ฯลฯ) ตามแพตเทิร์นเดียวกัน: คืน `(html, js)` ผูกทุก element กับ id ที่มีเลขฉาก และคำนวณสถานะจาก t เท่านั้น (ห้ามสะสมสถานะข้าม onUpdate)

## สไตล์ (Kanit Bold, ม่วงแดง `#DB2777`)
- ข้อความอยู่เหนือหัว (บนสุด ~y 720–760 ดูจากเฟรม) ไม่ทับหน้า; ความกว้างไทย 70–80px ต่อ ~18 ตัว เกินให้ลดขนาด
- **Hook**: บรรทัดเล็กม่วงแดง (ชื่อซีรีส์/หมวดจาก profile.series, 96px) + หัวเรื่องขาวใหญ่ (120–138px) + บรรทัด 3 (56–64px) ขึ้นตามคำพูด
- **รายการข้อ** ชิดซ้าย 68–80px เลขม่วงแดงรอไว้ ข้อความเด้งตอนพูด ข้อเก่า opacity 0.4
- **ฉากโฟกัสต่อข้อ (แบบโล่ง — ผู้ใช้ ชอบ แบบรกไม่เอา)**: รายการหาย เหลือหัวเล็ก `n · ชื่อข้อ` (60px top ~230–250) + รูป SVG ขาวล้วนเรียบๆ ตรงกลาง (616x300–330 top ~320–350) + ช่องข้อความ/สมการ 1 บรรทัดใต้รูป (top 640–690) เปลี่ยนตามคำพูด; ม่วงแดงเฉพาะจุดสำคัญจุดเดียว; ไม่ใส่ป้ายเกินจำเป็น; จบฉากรายการกลับมา
- ตัวอย่างฉากที่เคยทำ: กล่อง+แรงซ้ายขวา (ΣF=0), คาน 2F·d = F·2d (ΣM=0), ลูกบอลในรางพาราโบลา (Ek+Ep=คงตัว), ชนยืดหยุ่น/ไม่ยืดหยุ่น, โพรเจกไทล์ (x linear, y power1.out/in), วงกลม, ลำโพง+คลื่น, ประจุ +/− + F = k q₁q₂/r², วงจร+กระแสสามัญจากขั้วบวก (dash offset), สมุดจด, กราฟแท่ง, ✓/✗, "v = 3 ✗ → m/s", "50 cm → 0.5 m", สูตรลัดถูกขีดฆ่า
- **ช่วงท้ายคลิป (ชวนทำต่อ/ติดตาม/สมัคร)**: กลุ่มข้อความ 1–3 บรรทัดต่อจังหวะพูด (ชื่อสิ่งที่เสนอ, จุดเด่น, วัน/เวลาถ้าพูด, ตัวเลขสำคัญ, ช่องทางติดต่อจาก `profile.cta_handle` เมื่อพูดถึง) **ห้ามเติมข้อเท็จจริงที่ไม่ได้พูด** (ราคา วัน จำนวนที่นั่ง ฯลฯ) ถ้าเติมต้องแจ้ง
- แถบความคืบหน้าม่วงแดง 10px ขอบบน (อยู่ใน hflib แล้ว)
- เศษส่วนใช้แบบซ้อน (`.frac` flex column + `.fbar` div สูง 7px — border-bottom ไม่ขึ้น)
- **ตรวจความถูกต้องเฉพาะวิชา** เมื่อ `profile.subject_checks` ไม่ว่าง (เช่น physics): ตรวจทุกรูป/สูตร/หน่วย/ทิศทางที่ขึ้นจอ และเทียบกับหลักสูตรที่ผู้ใช้ระบุถ้าพูดถึงบทเรียน; ถ้าว่าง ไม่ต้องตรวจเนื้อหาวิชา แต่ยังห้ามเติมข้อเท็จจริงเอง

## HyperFrames gotchas
- video ใน composition `muted` (เสียงมิกซ์แยก mux ทีหลัง); root/video data-duration = T
- GSAP timeline paused เดียว `window.__timelines["main"]` ปิดด้วย `tl.set({}, {}, T)`
- element ที่ GSAP animate transform ห้ามมี CSS `transform` (lint error) → ใช้ `fromTo`
- SVG marker id ต้องไม่ซ้ำข้ามฉาก (ahw, ahw3) ไม่งั้นหัวลูกศรหาย; SVG transform ใช้ `svgOrigin`; clip ทุกตัวต้องมี data-start/duration
- ปรับแสงทำใน RGB (`format=gbrp`) เท่านั้น (yuv ทำสีเพี้ยนเขียว)

## โหมดเรียบ ("แค่ text hook + sound + ตัด dead air")
ไม่ zoom ไม่ grade ไม่ progress bar ไม่อนิเมชัน: `write_filters(grade=False)` แล้ว `ass=hook.ass` หลัง concat; Hook 2 บรรทัด pop (`\fscx60→106→100`, `\fad`) Kanit 130/78 คลิปจอแยก (กระดานบน/กล้องล่าง): วาง Hook บนที่ว่างของกระดานด้วยตัวอักษรเข้ม `&H00141414` ขอบขาว; SFX whoosh+pop ตอน Hook เท่านั้น loudnorm ~−14 → ข้ามการ render HyperFrames (ประหยัด 4–5 นาที + ~120MB)
