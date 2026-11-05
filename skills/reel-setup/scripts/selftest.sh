#!/bin/bash
# selftest.sh — ลองตัดคลิปทดสอบ 5 วินาทีที่สร้างเอง (ไม่ใช้ไฟล์ของผู้ใช้ ไม่ใช้เน็ต/เครดิต) เพื่อเช็กว่าทุกขั้นทำงาน
set -e
RD=""; for c in "$HOME/.claude/skills/reel-cut" ".claude/skills/reel-cut"; do [ -f "$c/SKILL.md" ] && RD="$(cd "$c" && pwd)" && break; done
[ -n "$RD" ] || { echo "❌ ไม่พบสกิล reel-cut"; exit 1; }
. "$RD/scripts/env.sh"
W="$REELWORK/_selftest"; rm -rf "$W"; mkdir -p "$W/hf"; cd "$W"
echo "▶ สร้างคลิปทดสอบ..."
"$FF" -y -v error -f lavfi -i "gradients=s=1080x1920:r=30:d=6:c0=0xf4f1ea:c1=0xd2cdc2:speed=0.0001" -f lavfi -i sine=f=220:d=6 -c:v libx264 -preset ultrafast -pix_fmt yuv420p -c:a aac src.mp4
echo "$W/src.mp4" > source.path; echo '[[0.2,2.5],[3.0,5.5]]' > seg.json
python3 -I - <<PY
import sys; sys.path.insert(0,"$RD/scripts")
from hflib import *
S,T=init(); write_filters(face_y=1140); write_sfx([("pop",0.5,-10),("whoosh",T-1.5,-8)])
PY
echo "▶ ตัดต่อ + ปรับแสง..."; bash "$RD/scripts/cut_grade.sh" "$W" "$W/src.mp4" >/dev/null
echo "▶ ทำเสียงเอฟเฟกต์ + มิกซ์..."; python3 -I "$RD/scripts/sfx.py" "$W" >/dev/null; bash "$RD/scripts/mix.sh" "$W" live >/dev/null
for f in hf/cut3v.mp4 voice.wav sfx.wav mix_live.m4a; do [ -s "$f" ] || { echo "❌ ไม่ได้ไฟล์ $f"; exit 1; }; done
D=$("$FP" -v error -show_entries format=duration -of csv=p=0 hf/cut3v.mp4)
echo "✅ ทดสอบผ่าน: ได้วิดีโอยาว ${D%.*} วินาที + เสียงมิกซ์"
cd /; rm -rf "$W"
