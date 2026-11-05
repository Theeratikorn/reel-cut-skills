---
name: reel-cut
description: ตัดคลิปแนวตั้ง (สอน/อธิบาย/พูดหน้ากล้อง) ด้วย Claude Code — ตัวควบคุมหลัก อ่านโปรไฟล์ผู้ใช้ เลือกโหมด จัดลำดับงาน และกฎประหยัดโทเคน/พื้นที่ ใช้เมื่อผู้ใช้สั่ง "ตัดคลิปล่าสุดใน download" หรือระบุไฟล์ แล้วเรียก reel-edl → reel-visuals → reel-audio → reel-deliver ตามลำดับ
---

# reel-cut — ตัวควบคุม (Claude Code)

รันบน Mac ตรงๆ ด้วย Bash (ไม่ต้อง Desktop Commander/VM/device_bash/staging ไฟล์) สคริปต์ทั้งหมดอยู่ที่ `~/.claude/skills/reel-cut/scripts` (ติดตั้งส่วนตัว) หรือ `.claude/skills/reel-cut/scripts` (ในโปรเจกต์) เรียกว่า `$REEL` — `source "$(ls -d ~/.claude/skills/reel-cut .claude/skills/reel-cut 2>/dev/null | head -1)/scripts/env.sh"` ได้ `FF FP REEL REELWORK OUT_DIR`

## ขั้นที่ 0 — โปรไฟล์ผู้ใช้ (ทุกครั้งก่อนเริ่มงาน)
`python3 -I $REEL/scripts/reelprofile.py exists` — **ถ้าไม่มีโปรไฟล์** (ผู้ใช้ยังไม่เคยตั้งค่า) ให้เรียกสกิล `reel-setup` ไปสัมภาษณ์ก่อน อย่าเดาว่าผู้ใช้เป็นใคร; ถ้ามี ให้ `show` แล้วใช้ค่าตามนี้ทั้งชุดงาน:
- `style` สไตล์ภาพ (รหัสในคลัง `styles/README.md`) · `accent` สีเน้น · `wall` (light = ตัวอักษรเข้ม / dark = ตัวอักษรขาว) · `series`+`pill` ป้ายกลางจอ
- `cta_end` / `cta_handle` ข้อความท้ายคลิป/ช่องทางติดต่อ — ใช้เท่าที่ผู้ใช้ให้เท่านั้น ห้ามแต่งเพิ่ม
- `target_seconds` ความยาวเป้า · `music` (none = ไม่มี BGM, bgm = ทำ 2 ไฟล์, ask = ถามก่อน) · `out_dir` · `language` · `dislikes` (เช่น "ภาพรก" → ลดองค์ประกอบ)
- `subject_checks` ถ้าไม่ว่าง (เช่น physics) ต้องตรวจความถูกต้องของเนื้อหาวิชานั้นทุกครั้ง; ถ้าว่าง ไม่ต้องอ้างวิชาใด
- ผู้ใช้บอกอะไรขัดกับโปรไฟล์ในแชต → ทำตามที่เขาสั่งตอนนี้ แล้วถามว่าจะอัปเดตโปรไฟล์ไหม (`reelprofile.py save`)

## เลือกโหมด
- ค่าเริ่มต้น = **จัดเต็ม** (ตัด + ปรับแสงหน้า + Hook/อนิเมชัน HyperFrames + SFX + BGM)
- "แค่ text hook + sound" = **เรียบ**: ข้าม reel-visuals ส่วน HyperFrames/grade ใช้ ASS (ดู reel-visuals § โหมดเรียบ)

## ลำดับงาน (แต่ละขั้นเป็นสกิลแยก โหลดเฉพาะขั้นที่กำลังทำ)
1. `/reel-edl` — หาไฟล์ → ถอดเสียง → อ่านบรรทัดพูด → `seg.json`
2. `/reel-visuals` — `gen.py` (ใช้ hflib) → cut+grade ผ่านเดียว → lint/snapshot → render
3. `/reel-audio` — SFX numpy → mix (live/bgm) เป็น m4a
4. `/reel-deliver` — mux → ตรวจ → พรีวิว → รายงาน → **cleanup**

## กฎประหยัด (หัวใจของเวอร์ชันนี้)
**พื้นที่ดิสก์** (เดิม ~300–700MB/คลิป สะสมเป็น 14GB ใน Downloads)
- โฟลเดอร์งานอยู่ที่ `$REELWORK/<ชื่อคลิป>/` = `~/.cache/reelcut/…` ไม่ใช่ `~/Downloads` และไม่ก๊อปวิดีโอต้นฉบับ (จำ path ใน `source.path`)
- **ไม่มี `cutA.mov`**: ตัด+ปรับแสงเป็น filter เดียว อ่านต้นฉบับครั้งเดียว → `hf/cut3v.mp4` + `voice.wav`
- **ไม่มี `audio.mp3`**: ส่งเสียงเข้า ElevenLabs ผ่าน pipe; `transcript.json` ถูกใช้ซ้ำ (ไม่ถอดซ้ำ ไม่เสียเครดิต)
- mix ออกเป็น `.m4a` ตรงๆ ไม่มี `mix_*.wav` 12MB สองไฟล์; mux แบบ `-c copy`
- เฟรมตรวจ = contact sheet ใบเดียวในโฟลเดอร์งาน (ไม่มี `zz_*.jpg` ใน ~/Movies)
- จบงานรัน `cleanup.sh` (ลบกลางทาง เหลือ "สูตร" <1MB: transcript/seg/gen.py/events/sfx_sched/hf/index.html) → รันคลิปเดิมซ้ำ/แก้เพลงได้โดยเรนเดอร์ภาพใหม่เท่านั้นเมื่อภาพเปลี่ยน
- แม่แบบ/SFX/BGM อยู่ใน `$REEL/{templates,assets}` ไม่ต้องพึ่งโฟลเดอร์ VID_xxx_work เก่า → ลบของเก่าได้ (`prune_old.sh` แสดงขนาด; **ผู้ใช้เป็นคนสั่งลบเอง**)

**โทเคน**
- อ่านทรานสคริปต์ครั้งเดียวผ่าน `lines.py` (บรรทัดละประโยค) ไม่ cat JSON
- `gen.py` ของคลิปใหม่ = คัดลอก `$REEL/templates/gen_example.py` แก้เฉพาะเนื้อหา (ไม่เขียน css/filter/helper ซ้ำ)
- ใช้ `ph.py` หาเวลาวลี แทนเดาเวลาจาก JSON
- render/ffmpeg ยาว ให้ `run_in_background` แล้วรอแจ้งเอง ห้าม poll วน
- ไม่ต้องสร้างคอนเทนต์เพลงใหม่ถ้าคลิป ≤ 79s (ใช้ `$REEL/assets/bgm.mp3`; ElevenLabs Music เสียเครดิต)
- อย่าโหลดสกิลหลายขั้นพร้อมกัน

## กฎความปลอดภัย
- ElevenLabs key มาจาก env `ELEVENLABS_API_KEY` หรือที่ ผู้ใช้ ส่งในแชตเท่านั้น (ขึ้นต้น `sk_`) ห้ามดึงจากไฟล์สคริปต์เก่า ห้ามพิมพ์ key ออกมา
- ไฟล์ปลายทางอย่าเขียนทับ (mux.sh ปฏิเสธเอง ใช้ `_v2/_สั้น`)
- ห้ามลบไฟล์ใน Downloads/Movies; `cleanup.sh` แตะเฉพาะ `~/.cache/reelcut/*` และเฉพาะไฟล์กลางทางที่สร้างซ้ำได้

## ถ้าขอ CapCut Draft
ถ้ามีสกิล `capcut-draft-automation` ในเครื่อง ให้ใช้สกิลนั้น (ไม่ได้อยู่ในชุดนี้)
