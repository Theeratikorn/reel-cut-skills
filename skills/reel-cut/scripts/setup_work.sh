#!/bin/bash
# setup_work.sh <video> [ชื่อคลิป]  -> สร้าง $REELWORK/<ชื่อ>/ พร้อม hf scaffold (ไม่เรียก npx init, ไม่ก๊อปไฟล์ใหญ่)
set -e
source "$(dirname "$0")/env.sh"
V="$1"; [ -f "$V" ] || { echo "usage: setup_work.sh <video> [name]"; exit 1; }
N="${2:-$(basename "${V%.*}")}"
W="$REELWORK/$N"; mkdir -p "$W/hf"
echo "$V" > "$W/source.path"            # จำ path ต้นฉบับ (ไม่ก๊อปวิดีโอ)
cd "$W/hf"
cp "$HOME/Library/Fonts/Kanit-Bold.ttf" "$HOME/Library/Fonts/Kanit-SemiBold.ttf" . 2>/dev/null || echo "คำเตือน: ไม่พบฟอนต์ Kanit (รัน reel-setup)"
for f in "$HOME"/Library/Fonts/Caveat*.ttf; do [ -f "$f" ] && cp "$f" Caveat.ttf && break; done
for f in "$HOME"/Library/Fonts/NotoSansThai*.ttf; do [ -f "$f" ] && cp "$f" NotoSansThai.ttf && break; done
echo '{"id":"hf","name":"hf"}' > meta.json
cat > hyperframes.json <<'J'
{"$schema":"https://hyperframes.heygen.com/schema/hyperframes.json","registry":"https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry","paths":{"blocks":"compositions","components":"compositions/components","assets":"assets"},"media":{"autoProxy":true}}
J
cat > package.json <<'J'
{"name":"hf","private":true,"type":"module","scripts":{"render":"npx --yes hyperframes@0.8.137 render"}}
J
echo "$W"
