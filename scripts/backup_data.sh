#!/usr/bin/env bash
# Copies Nivaran's encrypted data files into a dated folder, and keeps only the newest 30 copies.
#   bash scripts/backup_data.sh            (run it yourself, or let cron/launchd run it every hour)
# The files are already encrypted. The KEY (.data_key) is NOT copied here on purpose: a backup next to its key is not private.
# Keep the key somewhere separate and safe (a password manager). Without the key the backups cannot be read.
set -euo pipefail
cd "$(dirname "$0")/.."
DEST="${NIVARAN_BACKUP_DIR:-$HOME/Documents/NivaranBackups}"
STAMP="$(date +%Y-%m-%d_%H%M%S)"
mkdir -p "$DEST/$STAMP"
n=0
for f in .cases.json .drafts.json .profiles.json .pilot_users.json backend/.cases.json backend/.drafts.json backend/.profiles.json; do
  if [ -f "$f" ]; then cp -p "$f" "$DEST/$STAMP/$(echo "$f" | tr '/' '_')"; n=$((n+1)); fi
done
chmod -R go-rwx "$DEST/$STAMP"
if [ "$n" -eq 0 ]; then rmdir "$DEST/$STAMP"; echo "Nothing to back up yet (no data files found)."; exit 0; fi
ls -1d "$DEST"/20* 2>/dev/null | sort -r | tail -n +31 | while read -r old; do rm -rf "$old"; done || true
echo "Backed up $n file(s) to $DEST/$STAMP"
[ -f .data_key ] && echo "Reminder: also keep a copy of .data_key somewhere safe and separate (without it, backups cannot be read)."
