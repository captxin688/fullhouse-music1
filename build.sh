#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# ติดตั้ง FFmpeg แบบ Static Build
if [ ! -d ffmpeg ]; then
  echo "Downloading ffmpeg..."
  mkdir ffmpeg
  wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
  tar -xvf ffmpeg-release-amd64-static.tar.xz -C ffmpeg --strip-components=1
fi

# เพิ่ม path ให้ระบบมองเห็น ffmpeg
export PATH=$PATH:$(pwd)/ffmpeg