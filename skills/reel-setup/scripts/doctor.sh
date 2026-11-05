#!/bin/bash
# doctor.sh — ตรวจเครื่องว่าพร้อมตัดคลิปไหม (ไม่เปลี่ยนแปลงอะไร) ผลเป็นภาษาไทยง่ายๆ
RD=""; for c in "$HOME/.claude/skills/reel-cut" ".claude/skills/reel-cut"; do [ -f "$c/SKILL.md" ] && RD="$(cd "$c" && pwd)" && break; done
[ -n "$RD" ] && . "$RD/scripts/env.sh"
BAD=0
ok(){ echo "✅ $1"; }
no(){ echo "❌ $1"; [ -n "$2" ] && echo "   → $2"; BAD=$((BAD+1)); }

[ "$(uname -s)" = Darwin ] && ok "เครื่อง Mac" || no "ไม่ใช่เครื่อง Mac" "ชุดนี้ออกแบบสำหรับ Mac"
command -v brew >/dev/null && ok "Homebrew (ตัวติดตั้งโปรแกรม)" || no "ยังไม่มี Homebrew" "ต้องติดตั้งก่อน (ดู INSTALL.md ขั้นที่ 1)"
if [ -n "$RD" ] && [ -x "$FF" ] || command -v "$FF" >/dev/null 2>&1; then
  ok "ffmpeg (ตัดต่อวิดีโอ)"
  "$FF" -hide_banner -encoders 2>/dev/null | grep -q h264_videotoolbox && ok "เข้ารหัสวิดีโอด้วยการ์ดจอ Mac (VideoToolbox)" || no "ffmpeg ไม่มี VideoToolbox" "ติดตั้ง ffmpeg-full ใหม่: brew install ffmpeg-full"
  "$FF" -hide_banner -filters 2>/dev/null | grep -qE ' ass ' && ok "ffmpeg รองรับซับ/ข้อความ (libass)" || no "ffmpeg ไม่มี libass" "brew install ffmpeg-full"
else no "ยังไม่มี ffmpeg-full" "brew install ffmpeg-full"; fi
command -v npx >/dev/null && ok "Node.js (ใช้เรนเดอร์อนิเมชัน)" || no "ยังไม่มี Node.js" "brew install node"
python3 -c "import numpy" 2>/dev/null && ok "Python + numpy (ทำเสียงเอฟเฟกต์)" || no "ยังไม่มี Python numpy" "brew install numpy"
for f in "Kanit-Bold" "Kanit-SemiBold" "NotoSansThai" "Caveat"; do
  ls "$HOME"/Library/Fonts/${f}*.ttf >/dev/null 2>&1 && ok "ฟอนต์ $f" || no "ยังไม่มีฟอนต์ $f" "รัน install.sh อีกครั้ง"
done
[ -n "$ELEVENLABS_API_KEY" ] && ok "มีรหัส ElevenLabs (ถอดเสียง)" || no "ยังไม่ได้ตั้งรหัส ElevenLabs" "ต้องมีบัญชี ElevenLabs แล้วบอก Claude ให้บันทึกรหัสให้"
[ -n "$RD" ] && python3 -I "$RD/scripts/reelprofile.py" exists && ok "มีโปรไฟล์ของคุณแล้ว (สี/สไตล์/ข้อความท้ายคลิป)" || no "ยังไม่ได้ตั้งค่าโปรไฟล์ของคุณ" "บอก Claude ว่า \"ตั้งค่าสกิลตัดคลิปให้หน่อย\" เพื่อให้สัมภาษณ์"
for s in reel-cut reel-edl reel-visuals reel-audio reel-deliver reel-setup; do
  [ -f "$HOME/.claude/skills/$s/SKILL.md" ] || [ -f ".claude/skills/$s/SKILL.md" ] && ok "สกิล $s ติดตั้งแล้ว" || no "ยังไม่มีสกิล $s" "รัน install.sh"
done
echo; [ $BAD -eq 0 ] && echo "🎉 พร้อมใช้งาน" || echo "⚠️ ยังไม่พร้อม: $BAD รายการ"
exit $BAD
