#!/bin/bash
# cleanup.sh <WORK> [--yes]  ลบเฉพาะไฟล์กลางทางที่สร้างซ้ำได้ (ค่าเริ่มต้น = แสดงรายการเฉยๆ)
# เก็บ "สูตร" ไว้ (transcript.json seg.json gen.py events.json sfx_sched.json hf/index.html) < 1MB
# ไม่แตะ: ไฟล์ต้นฉบับ, ไฟล์ปลายทางใน OUT_DIR, อะไรนอก WORK
W="$1"; [ -d "$W" ] || { echo "usage: cleanup.sh <WORK> [--yes]"; exit 1; }
case "$W" in */.cache/reelcut/*) ;; *) echo "ปฏิเสธ: WORK ต้องอยู่ใต้ ~/.cache/reelcut/"; exit 1;; esac
LIST=$(cd "$W" && ls -d voice.wav sfx.wav mask.png mix_*.m4a v_video.mp4 hf/cut3v.mp4 hf/snaps hf/.hyperframes hf/render.log hf/node_modules 2>/dev/null)
[ -z "$LIST" ] && { echo "ไม่มีอะไรให้ล้าง"; exit 0; }
(cd "$W" && du -sh $LIST)
if [ "$2" = "--yes" ]; then (cd "$W" && rm -rf $LIST) && echo "ล้างแล้ว"; else echo "(dry-run) เติม --yes เพื่อลบ"; fi
