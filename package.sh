#!/bin/sh
# Build a standalone Pac-Man binary that can be uploaded to Itch.io.
#
# The result is dist/pacman/ containing the executable, the default
# configuration and a short README for the players.
set -e

NAME="pacman"
OUT="dist/${NAME}"

echo "==> installing the build dependencies"
python3 -m pip install --upgrade pyinstaller >/dev/null

echo "==> building the executable"
python3 -m PyInstaller \
	--noconfirm \
	--clean \
	--onefile \
	--windowed \
	--name "${NAME}" \
	--hidden-import mazegenerator \
	pac-man.py

echo "==> assembling the package"
mkdir -p "${OUT}"
mv "dist/${NAME}" "${OUT}/${NAME}" 2>/dev/null || true
cp config.json "${OUT}/config.json"
cp packaging/README.txt "${OUT}/README.txt"

echo "==> done: ${OUT}"
echo "    upload ${OUT} to Itch.io as a free, unlisted build."
