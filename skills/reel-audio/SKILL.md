---
name: reel-audio
description: ขั้น 3 ของ reel-cut — สร้าง SFX track ด้วย numpy, mix เสียงสด/เสียง+BGM (sidechain, loudnorm ~-14 LUFS) เป็น m4a ใช้เมื่อมี voice.wav และ sfx_sched.json แล้ว
---

# reel-audio — SFX + mix

```bash
source "$(ls -d ~/.claude/skills/reel-cut .claude/skills/reel-cut 2>/dev/null | head -1)/scripts/env.sh"        # W = โฟลเดอร์งาน (มี voice.wav, sfx_sched.json)
python3 -I $REEL/scripts/sfx.py $W                   # -> sfx.wav (numpy, ห้ามใช้ ffmpeg amix+adelay หลายสิบ input: ค้าง)
bash $REEL/scripts/mix.sh $W live                    # -> mix_live.m4a
bash $REEL/scripts/mix.sh $W bgm                     # -> mix_bgm.m4a (BGM = $REEL/assets/bgm.mp3 79s หรือส่ง path ที่ 3)
```
- ระดับ SFX (ตั้งใน `write_sfx` ของ gen.py): whoosh −6/−8 (เปิด, เข้าช่วงท้ายคลิป), pop −10/−11 (ข้อความขึ้น), ding −9/−11 (แถม/วันเริ่ม), boing −8/−10 (จุดผิด), impact −8 (เริ่ม k−0.26 ให้ hit ตรงคำเน้นสำคัญ), ping −8 (ตอนพูดช่องทางติดต่อ) ไม่ใส่ทุกข้อความ
- live = voice+sfx → loudnorm `I=-11.5:TP=-1.5:LRA=11` (ได้ ~−13 ถึง −14.6 LUFS)
- BGM: `volume=-21dB` (−14dB ดังไป) + `sidechaincompress=threshold=0.02:ratio=6:attack=10:release=400:makeup=1` + fade out 1.5s → loudnorm เดียวกัน
- คลิปยาวเกิน 79s → mix.sh เตือน ต้องสร้างเพลงใหม่ด้วย ElevenLabs Music (`POST /v1/music` {prompt, music_length_ms, force_instrumental:true}, แพ็กเกจเสียเงิน — ถามก่อน)
- แก้ระดับเพลงทีหลัง = รัน `mix.sh bgm` + `mux.sh` ใหม่ ไม่ต้องเรนเดอร์ภาพ (ต้องยังไม่ cleanup `voice.wav`/`sfx.wav`/`v_video.mp4`)
