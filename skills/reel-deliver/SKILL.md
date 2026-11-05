---
name: reel-deliver
description: ขั้น 4 ของ reel-cut — mux เสียงเข้าวิดีโอ ตรวจ ffprobe/LUFS ทำพรีวิว รายงานผล แล้วล้างไฟล์กลางทาง (cleanup) ใช้เมื่อมี v_video.mp4 และ mix_*.m4a แล้ว
---

# reel-deliver — ส่งงาน + ล้างพื้นที่

```bash
source "$(ls -d ~/.claude/skills/reel-cut .claude/skills/reel-cut 2>/dev/null | head -1)/scripts/env.sh"        # W, OUT_DIR = โฟลเดอร์ CapCut เดิมถ้ามี ไม่งั้น ~/Movies/ReelCut
N="<series>_<หัวข้อ>"                                # series จากโปรไฟล์ (ถ้ามี) เช่น ซีรีส์_3ข้อที่ต้องทำ
bash $REEL/scripts/mux.sh $W live "$N"               # -> ${N}_เสียงสด.mp4   (ไม่เขียนทับ; ชนกันให้ใช้ _v2/_สั้น)
bash $REEL/scripts/mux.sh $W bgm  "$N"               # -> ${N}_BGM.mp4
bash $REEL/scripts/check.sh "$OUT_DIR/${N}_BGM.mp4"  # ต้อง 1080x1920, ความยาว, I ≈ −14 LUFS
bash $REEL/scripts/contact.sh "$OUT_DIR/${N}_BGM.mp4" $W/final.jpg    # สุ่มเฟรม 1 ใบ (Read ใบเดียว)
```
พรีวิวเล็ก (ถ้าต้องส่งในแชต ≤30MB): `$FF -i <final> -vf scale=720:-2 -b:v 2400k $W/preview.mp4`

## รายงานให้ ผู้ใช้
ความยาวก่อน/หลัง · เทค/ประโยคที่ตัด (บอกจุดต่อ 2 เทค) · เนื้อหาบนจอแต่ละข้อ · ข้อความที่เติมเอง · ผลเช็กฟิสิกส์ · path ไฟล์เต็ม

## ล้างพื้นที่ (ทำหลังรายงาน และหลัง ผู้ใช้ รับงานแล้ว)
```bash
bash $REEL/scripts/cleanup.sh $W            # แสดงรายการ + ขนาด (dry-run)
bash $REEL/scripts/cleanup.sh $W --yes      # ลบเฉพาะไฟล์กลางทางที่สร้างซ้ำได้
```
- ล้างแล้วยังเหลือ transcript/seg/gen.py/events/sfx_sched/hf/index.html (<1MB) → แก้เนื้อหาแล้วรัน gen.py + cut_grade.sh + render ใหม่ได้
- ถ้า ผู้ใช้ ยังอาจขอปรับเพลง/เสียง ให้เลื่อน cleanup ไปก่อน
- โฟลเดอร์ `~/Downloads/*_work` เก่าจากระบบเดิม: `bash $REEL/scripts/prune_old.sh` แสดงขนาด **แต่ไม่ลบ** — แจ้ง ผู้ใช้ ให้ลบเอง (หรือรอ ผู้ใช้ สั่งชัดเจนเป็นรายโฟลเดอร์)
