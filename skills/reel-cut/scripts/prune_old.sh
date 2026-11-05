#!/bin/bash
# prune_old.sh  — แสดงโฟลเดอร์ ~/Downloads/*_work เก่า (ของระบบก่อนหน้า) พร้อมขนาด; ไม่ลบอะไรเอง
# ลบจริงให้ผู้ใช้สั่งเองรายโฟลเดอร์ (เช่น rm -rf ~/Downloads/VID_xxx_work) หลังเช็กว่าไม่ต้องใช้เป็นแม่แบบแล้ว
du -sh ~/Downloads/*_work 2>/dev/null | sort -h
echo; du -shc ~/Downloads/*_work 2>/dev/null | tail -1
