#!/bin/bash
# transcribe.sh <video> <WORK>  -> WORK/transcript.json (ไม่เก็บ audio.mp3: ไหลผ่าน pipe เข้า curl)
set -e
source "$(dirname "$0")/env.sh"
V="$1"; W="$2"
[ -n "$ELEVENLABS_API_KEY" ] || { echo "ต้อง export ELEVENLABS_API_KEY (ขึ้นต้น sk_)"; exit 1; }
[ -s "$W/transcript.json" ] && { echo "มี transcript.json แล้ว — ข้าม (ไม่เสียเครดิตซ้ำ)"; exit 0; }
$FF -v error -i "$V" -vn -ac 1 -ar 16000 -b:a 64k -f mp3 - | \
 curl -sS -X POST https://api.elevenlabs.io/v1/speech-to-text \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F model_id=scribe_v2 -F language_code=tha -F timestamps_granularity=word -F tag_audio_events=false \
  -F "file=@-;filename=a.mp3;type=audio/mpeg" -o "$W/transcript.json"
python3 -I "$(dirname "$0")/lines.py" "$W/transcript.json" | head -3
