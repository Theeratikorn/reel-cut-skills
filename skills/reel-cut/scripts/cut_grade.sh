#!/bin/bash
# cut_grade.sh <WORK> [src_video]  (ต้องมี WORK/cut_grade_filter.txt + mask.geq จาก hflib.write_filters)
# ผ่านเดียว: อ่านต้นฉบับครั้งเดียว -> hf/cut3v.mp4 (วิดีโอตัด+ปรับแสง, ไม่มีเสียง) + voice.wav (เสียงตัดแล้ว)
# แทนของเดิมที่เขียน cutA.mov(~140MB) แล้วอ่านซ้ำอีกรอบ
set -e
source "$(dirname "$0")/env.sh"
W="$1"; V="${2:-$(cat "$W/source.path")}"; cd "$W"
[ -s mask.png ] || $FF -y -v error -f lavfi -i color=black:s=1080x1920 -frames:v 1 -vf "$(cat mask.geq)" -pix_fmt gray mask.png
$FF -y -v error -i "$V" -loop 1 -i mask.png -filter_complex_script cut_grade_filter.txt \
  -map "[v]" -c:v h264_videotoolbox -b:v 14M -an hf/cut3v.mp4 \
  -map "[a]" -c:a pcm_s16le -ar 48000 -ac 2 voice.wav
ls -l hf/cut3v.mp4 voice.wav
