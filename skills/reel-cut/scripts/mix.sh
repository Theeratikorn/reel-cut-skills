#!/bin/bash
# mix.sh <WORK> live|bgm   -> WORK/mix_<mode>.m4a (AAC ตรงๆ ไม่ผ่าน wav 12MB)
# เสียง: voice.wav + sfx.wav [+ bgm]  loudnorm เป้า ~-14 LUFS ; BGM -21dB + sidechain + fade out 1.5s
set -e
source "$(dirname "$0")/env.sh"
W="$1"; MODE="$2"; BGM="${3:-$REEL/assets/bgm.mp3}"; cd "$W"
T=$(python3 -c "import json;print(json.load(open('sfx_sched.json'))['T'])")
FO=$(python3 -c "print(round($T-1.5,2))")
N="aformat=sample_rates=48000:channel_layouts=stereo"
if [ "$MODE" = live ]; then
  $FF -y -v error -i voice.wav -i sfx.wav -filter_complex "[0:a]$N[v];[1:a]$N[s];[v][s]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-11.5:TP=-1.5:LRA=11[out]" \
    -map "[out]" -t $T -ar 48000 -c:a aac -b:a 192k mix_live.m4a
else
  BL=$($FP -v error -show_entries format=duration -of csv=p=0 "$BGM")
  python3 -c "import sys; sys.exit(0 if $BL >= $T else 1)" || echo "คำเตือน: BGM สั้นกว่าคลิป ($BL < $T) ต้องสร้างเพลงใหม่"
  $FF -y -v error -i voice.wav -i sfx.wav -i "$BGM" -filter_complex "[0:a]$N,asplit=2[v][vsc];[1:a]$N[s];[2:a]$N,atrim=0:$T,volume=-21dB,afade=t=out:st=$FO:d=1.5[bg];[bg][vsc]sidechaincompress=threshold=0.02:ratio=6:attack=10:release=400:makeup=1[bgd];[v][s][bgd]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-11.5:TP=-1.5:LRA=11[out]" \
    -map "[out]" -t $T -ar 48000 -c:a aac -b:a 192k mix_bgm.m4a
fi
ls -l mix_$MODE.m4a
