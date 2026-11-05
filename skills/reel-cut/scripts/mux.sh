#!/bin/bash
# mux.sh <WORK> live|bgm <ชื่อไฟล์ไม่รวมนามสกุล>  -> $OUT_DIR/<ชื่อ>_เสียงสด|_BGM.mp4 (ไม่เขียนทับของเดิม)
set -e
source "$(dirname "$0")/env.sh"
W="$1"; MODE="$2"; N="$3"; SUF=$([ "$MODE" = live ] && echo "เสียงสด" || echo "BGM")
mkdir -p "$OUT_DIR"; DST="$OUT_DIR/${N}_${SUF}.mp4"
[ -e "$DST" ] && { echo "มีไฟล์ $DST แล้ว — ใช้ชื่อ _v2/_สั้น"; exit 1; }
$FF -y -v error -i "$W/v_video.mp4" -i "$W/mix_$MODE.m4a" -map 0:v -map 1:a -c:v copy -c:a copy -shortest -movflags +faststart "$DST"
echo "$DST"
