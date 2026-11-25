#!/usr/bin/env bash
# Waits for an EAS Android build to finish, then downloads the APK to ~/Desktop/Nivaran_APK so the link can never expire for you.
#   bash scripts/wait_for_apk.sh <build-id>
# Checks every 2 minutes for up to 12 hours. Needs `npx eas-cli login` to have been done once.
set -uo pipefail
ID="${1:?give the build id}"
OUT="$HOME/Desktop/Nivaran_APK"; mkdir -p "$OUT"
cd "$(dirname "$0")/../mobile"
for i in $(seq 1 360); do
  J="$(npx --yes eas-cli build:view "$ID" --json 2>/dev/null || true)"
  ST="$(printf '%s' "$J" | python3 -c "import sys,json;print(json.load(sys.stdin).get('status',''))" 2>/dev/null || true)"
  echo "$(date '+%F %T') status=${ST:-unknown}"
  if [ "$ST" = "FINISHED" ]; then
    URL="$(printf '%s' "$J" | python3 -c "import sys,json;d=json.load(sys.stdin);print((d.get('artifacts') or {}).get('applicationArchiveUrl') or d.get('applicationArchiveUrl') or '')")"
    if [ -n "$URL" ]; then
      curl -L -s -o "$OUT/Nivaran_$(date +%Y%m%d).apk" "$URL" && echo "DOWNLOADED to $OUT/Nivaran_$(date +%Y%m%d).apk" && osascript -e 'display notification "The Nivaran APK is downloaded to Desktop/Nivaran_APK" with title "Nivaran"' 2>/dev/null
      exit 0
    fi
  fi
  if [ "$ST" = "ERRORED" ] || [ "$ST" = "CANCELED" ]; then echo "BUILD FAILED or CANCELED: open the build page for the log"; osascript -e 'display notification "The Nivaran build failed. Ask Claude to read the log." with title "Nivaran"' 2>/dev/null; exit 1; fi
  sleep 120
done
echo "Gave up after 12 hours."
