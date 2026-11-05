"""sfx.py <WORK> : sfx_sched.json -> sfx.wav (numpy, 48k stereo) ; ใช้ assets/sfx ของ skill"""
import json, os, shutil, subprocess, sys, numpy as np, wave
W = sys.argv[1]; REEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = os.environ.get("FF") or shutil.which("ffmpeg")
d = json.load(open(f"{W}/sfx_sched.json")); T = d["T"]; SR = 48000
out = np.zeros((int((T + 2) * SR), 2), dtype=np.float32); cache = {}
for name, t, db in d["sched"]:
    if name not in cache:
        raw = subprocess.run([FF, "-v", "error", "-i", f"{REEL}/assets/sfx/{name}.mp3", "-f", "f32le",
                              "-ar", str(SR), "-ac", "2", "-"], capture_output=True, check=True).stdout
        cache[name] = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    s = cache[name] * (10 ** (db / 20)); i = int(max(t, 0) * SR); e = min(i + len(s), len(out))
    out[i:e] += s[: e - i]
pcm = (np.clip(out, -1, 1) * 32767).astype("<i2")
with wave.open(f"{W}/sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("sfx.wav", len(d["sched"]), "events")
