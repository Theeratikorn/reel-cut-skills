#!/bin/bash
# contact.sh <video> <out.jpg> [fps=1/6]  -> contact sheet ใบเดียว (4 คอลัมน์, ครอปบน 1100px) แทนดูทีละเฟรม
source "$(dirname "$0")/env.sh"
$FF -y -v error -i "$1" -vf "fps=${3:-1/6},crop=1080:1100:0:0,scale=270:-2,tile=4x3" -frames:v 1 -q:v 4 "$2"
echo "$2"
