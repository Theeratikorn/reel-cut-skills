# source scripts/env.sh  — ตั้งค่ากลาง (ไม่พิมพ์ key)
export REEL="${REEL:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)}"
# key ElevenLabs (ถ้ามี) เก็บในไฟล์ส่วนตัวของผู้ใช้ ไม่อยู่ใน repo
[ -f "$HOME/.config/reelcut/env" ] && . "$HOME/.config/reelcut/env"
# หา ffmpeg-full (Apple Silicon / Intel / Homebrew prefix)
FFDIR=""
for c in "$(brew --prefix ffmpeg-full 2>/dev/null)/bin" /opt/homebrew/opt/ffmpeg-full/bin /usr/local/opt/ffmpeg-full/bin; do
  [ -x "$c/ffmpeg" ] && FFDIR="$c" && break
done
export FF="${FFDIR:+$FFDIR/}ffmpeg"
export FP="${FFDIR:+$FFDIR/}ffprobe"
# โฟลเดอร์งานหนัก: อยู่ใน cache (ไม่ใช่ Downloads) ลบทีเดียวได้ และ Spotlight/Time Machine ไม่ต้องไล่
export REELWORK="${REELWORK:-$HOME/.cache/reelcut}"
# ปลายทางไฟล์สำเร็จ: ใช้โฟลเดอร์ CapCut เดิมถ้ามี ไม่งั้น ~/Movies/ReelCut
_CAP="$HOME/Movies/CapCut/ตัดเสร็จแล้ว/คลิปเสร็จสมบูรณ์_MP4"
[ -z "$OUT_DIR" ] && OUT_DIR="$(python3 -I "$REEL/scripts/reelprofile.py" get out_dir 2>/dev/null)"
if [ -z "$OUT_DIR" ]; then if [ -d "$_CAP" ]; then OUT_DIR="$_CAP"; else OUT_DIR="$HOME/Movies/ReelCut"; fi; fi
export OUT_DIR
