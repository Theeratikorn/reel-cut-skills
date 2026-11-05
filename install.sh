#!/bin/bash
# ติดตั้ง/อัปเดตชุดสกิลตัดคลิป — รันซ้ำได้ ปลอดภัย ไม่ลบงานเก่า
# ใช้: bash install.sh            (ติดตั้ง/อัปเดต)
#      REELCUT_SRC=/path bash install.sh   (ติดตั้งจากโฟลเดอร์ในเครื่อง ใช้ตอนทดสอบ)
set -u
REPO_URL="${REELCUT_REPO:-https://github.com/Theeratikorn/reel-cut-skills.git}"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CACHE="$HOME/.cache/reelcut-src"
FONTDIR="$HOME/Library/Fonts"
say(){ echo "▶ $*"; }
good(){ echo "✅ $*"; }
die(){ echo "❌ $*"; exit 1; }

[ "$(uname -s)" = Darwin ] || die "ชุดนี้ใช้กับเครื่อง Mac เท่านั้น"
command -v git >/dev/null || die "ยังไม่มี git — เปิด Terminal พิมพ์ git --version แล้วกดติดตั้งตามที่ macOS ถาม จากนั้นรันใหม่"
command -v brew >/dev/null || { echo "❌ ยังไม่มี Homebrew (ตัวติดตั้งโปรแกรม)"; echo "   เปิดแอป Terminal แล้วทำตามขั้นตอนที่หน้า https://brew.sh (ต้องใส่รหัสผ่านเครื่อง) จากนั้นรัน install.sh ใหม่"; exit 2; }

# 1) โปรแกรม
for f in ffmpeg-full node; do
  if brew list --versions "$f" >/dev/null 2>&1; then good "$f มีแล้ว"; else say "ติดตั้ง $f (อาจใช้เวลาหลายนาที)..."; brew install "$f" || die "ติดตั้ง $f ไม่สำเร็จ"; fi
done
python3 -c "import numpy" 2>/dev/null && good "numpy มีแล้ว" || { say "ติดตั้ง numpy..."; brew install numpy || die "ติดตั้ง numpy ไม่สำเร็จ"; }

# 2) ฟอนต์ (ดาวน์โหลดจาก GitHub ของ Google Fonts ถ้ายังไม่มี)
mkdir -p "$FONTDIR"
FP1="https://cdn.jsdelivr.net/gh/google/fonts@main/ofl"      # ลองตัวนี้ก่อน (เสถียรกว่า)
FP2="https://github.com/google/fonts/raw/main/ofl"           # สำรอง
font(){ # pattern  path-ใน-ofl  ชื่อไฟล์ที่เก็บ
  ls "$FONTDIR"/$1 >/dev/null 2>&1 && { good "ฟอนต์ $3 มีแล้ว"; return; }
  say "ดาวน์โหลดฟอนต์ $3..."
  for base in "$FP1" "$FP2"; do
    for try in 1 2 3; do
      curl -fsSL --max-time 60 -o "$FONTDIR/$3.part" "$base/$2" 2>/dev/null && [ "$(stat -f%z "$FONTDIR/$3.part" 2>/dev/null || echo 0)" -gt 50000 ] && { mv "$FONTDIR/$3.part" "$FONTDIR/$3"; good "ฟอนต์ $3"; return; }
      sleep 2
    done
  done
  rm -f "$FONTDIR/$3.part"; echo "⚠️ ดาวน์โหลดฟอนต์ $3 ไม่สำเร็จ (อินเทอร์เน็ตอาจช้า) — รัน install.sh ซ้ำอีกครั้งได้"; }
font "Kanit-Bold.ttf" "kanit/Kanit-Bold.ttf" "Kanit-Bold.ttf"
font "Kanit-SemiBold.ttf" "kanit/Kanit-SemiBold.ttf" "Kanit-SemiBold.ttf"
font "NotoSansThai*.ttf" "notosansthai/NotoSansThai%5Bwdth%2Cwght%5D.ttf" "NotoSansThai-Variable.ttf"
font "Caveat*.ttf" "caveat/Caveat%5Bwght%5D.ttf" "Caveat-Variable.ttf"

# 3) สกิล
if [ -n "${REELCUT_SRC:-}" ]; then SRC="$REELCUT_SRC"; say "ใช้ไฟล์จาก $SRC"
elif [ -d "$(dirname "$0")/skills" ] && [ -f "$(dirname "$0")/skills/reel-cut/SKILL.md" ]; then SRC="$(cd "$(dirname "$0")" && pwd)"
else
  if [ -d "$CACHE/.git" ]; then say "อัปเดตสกิลจาก GitHub..."; git -C "$CACHE" pull --ff-only -q || die "อัปเดตไม่สำเร็จ"
  else say "ดาวน์โหลดสกิลจาก GitHub..."; mkdir -p "$(dirname "$CACHE")"; git clone --depth 1 -q "$REPO_URL" "$CACHE" || die "ดาวน์โหลดไม่สำเร็จ ตรวจอินเทอร์เน็ตและลิงก์ $REPO_URL"; fi
  SRC="$CACHE"
fi
mkdir -p "$DEST"
for d in "$SRC"/skills/reel-*; do n="$(basename "$d")"; rm -rf "$DEST/$n"; cp -R "$d" "$DEST/$n"; good "ติดตั้งสกิล $n"; done
chmod +x "$DEST"/reel-*/scripts/*.sh 2>/dev/null

echo; say "ตรวจความพร้อม..."
bash "$DEST/reel-setup/scripts/doctor.sh"; R=$?
echo; echo "ขั้นต่อไป: ปิดแล้วเปิด Claude Code ใหม่ 1 ครั้ง แล้วพิมพ์ \"ตัดคลิปล่าสุดใน Downloads ให้หน่อย\""
exit 0
