---
name: reel-edl
description: ขั้น 1 ของ reel-cut — เตรียมคลิป ถอดเสียง ElevenLabs Scribe อ่านบรรทัดพูด แล้วทำ EDL (seg.json) ตัด dead air/เทคผิด/ประโยคซ้ำ ใช้ต่อจาก reel-cut หรือเมื่อ ผู้ใช้ ขอแค่ตัด/ถอดเสียงคลิป
---

# reel-edl — ถอดเสียง + ตัดต่อ (EDL)

## 1. เตรียม
```bash
source "$(ls -d ~/.claude/skills/reel-cut .claude/skills/reel-cut 2>/dev/null | head -1)/scripts/env.sh"
ls -t ~/Downloads | grep -iE '\.(mp4|mov)$' | head -3        # คลิปล่าสุด (หรือไฟล์ที่ ผู้ใช้ ระบุ)
W=$(bash $REEL/scripts/setup_work.sh "<path/video>")          # -> ~/.cache/reelcut/<ชื่อ>/ (+ hf scaffold)
bash $REEL/scripts/contact.sh "<video>" $W/look.jpg 1/20      # 1 ใบ: ดูฉาก สีผนัง ตำแหน่งหน้า (Read ใบเดียวพอ)
```
- สีผนังเทา/มืด → ธีม `light` (ตัวขาว); ผนังขาว → ธีม `dark` (ตัวดำ) — จดไว้ให้ reel-visuals
- y ของหน้า (≈1140–1180) จดไว้ใช้ใน `write_filters(face_y=…)`
- มือถือมี rotation metadata (ffprobe 1920x1080) ffmpeg หมุนเป็น 1080x1920 เอง ไม่ต้อง crop

## 2. ถอดเสียง
```bash
bash $REEL/scripts/transcribe.sh "<video>" $W      # ต้องมี ELEVENLABS_API_KEY; มี transcript.json แล้วจะข้าม
python3 -I $REEL/scripts/lines.py $W/transcript.json    # อ่านทั้งคลิป 1 ครั้ง: start-end | ข้อความ
```
หาเวลาวลีเพิ่ม: `python3 -I $REEL/scripts/ph.py $W/transcript.json "วลี@เวลาเริ่มค้น"`

## 3. EDL → `$W/seg.json` (`[[start,end],…]` เวลาต้นฉบับ)
- เก็บบรรทัดพูด pad −0.1 / +0.18 รวมช่วงทับกัน ตัด dead air ทั้งหมด
- เทคผิด ("เอาใหม่", "สามสองหนึ่ง", "เอ้ย", พูดค้าง): เก็บเทคสุดท้ายที่ครบ — **แต่เช็กความหมาย** ถ้าเทคหลังพูดผิดคำสำคัญ (เช่น "จำแต่สูตรลัด" แทน "อย่าจำ") ให้ต่อประโยคเปิดจากเทคที่ถูก + ท่อนหลังจากเทคหลัง แล้วแจ้ง ผู้ใช้ ให้ฟังจุดต่อ
- ตัดประโยคพูดซ้ำความเดิม และคำเติม ("ครับ" ต้นประโยค, "เนาะ", "มันก็ไม่ถูกเนาะ", "สามสองหนึ่ง" นำหน้า) ตัดตรง spacing token ถ้าทำได้; จดจุดตัดกลางประโยคไว้รายงาน
- ความยาวเป้า ~60–65s (คลิปสอน 60–124s ทำผลงานดี ไม่ต้องแยกคลิป แค่ตัดซ้ำ) และ ≤ 79s เพื่อใช้ BGM สำเร็จรูป
- ส่งต่อให้ `/reel-visuals`: `$W`, ธีม, face_y, เวลาเหตุการณ์ที่อยากให้ขึ้นจอ (หา m(t) ด้วย ph.py)
