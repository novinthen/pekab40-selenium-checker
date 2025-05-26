#!/usr/bin/env bash
set -o errexit

echo "🔧 Installing Google Chrome for Render..."

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x google-chrome-stable_current_amd64.deb .
  chmod +x opt/google/chrome/google-chrome
  cd $HOME/project/src
else
  echo "✅ Chrome already cached"
fi
