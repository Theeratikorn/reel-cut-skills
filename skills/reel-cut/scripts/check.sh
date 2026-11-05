#!/bin/bash
# check.sh <mp4> : ขนาดภาพ, ความยาว, LUFS
source "$(dirname "$0")/env.sh"
$FP -v error -show_entries stream=width,height:format=duration,size -of default=nw=1 "$1"
$FF -hide_banner -i "$1" -af ebur128=framelog=quiet -vn -f null - 2>&1 | grep -E "^\s+I:" | head -1
