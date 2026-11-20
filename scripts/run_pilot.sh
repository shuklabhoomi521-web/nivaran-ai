#!/usr/bin/env bash
# Start the Nivaran backend on this laptop for the pilot, protected by a secret token.
#   bash scripts/run_pilot.sh
# Then, in a second Terminal window, start the app with the command this script prints.
# The phone and the laptop must be on the same Wi-Fi. Press Ctrl+C here to stop. Nothing is sent to the internet by this script.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .pilot_token ]; then
  python3 -c "import secrets; print(secrets.token_urlsafe(24))" > .pilot_token
  chmod 600 .pilot_token
  echo "Made a new secret token in .pilot_token (never share it, never commit it)."
fi
export NIVARAN_API_TOKEN="$(cat .pilot_token)"
export CORS_ORIGINS="${CORS_ORIGINS:-}"

IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
if [ -z "$IP" ]; then echo "Could not find this laptop's Wi-Fi address. Are you connected to Wi-Fi?"; exit 1; fi

[ -f .env ] || { echo "No .env file: copy .env.example to .env and add your keys first."; exit 1; }
for k in GROQ_API_KEY GEMINI_API_KEY SMTP_USER SMTP_PASSWORD; do
  grep -Eq "^${k}=.+" .env || echo "Warning: $k is empty in .env (only names are checked, values are never printed)."
done

echo
echo "Backend address on your Wi-Fi: http://$IP:8000"
echo "In a second Terminal window run:"
echo "  cd $(pwd)/mobile && EXPO_PUBLIC_API_URL=http://$IP:8000 npx expo start"
echo "Then open the Expo Go app on the phone and scan the code. The app asks for an access code on first start:"
echo "  - you (the owner): the text inside the file .pilot_token (open it yourself; it is not printed here)"
echo "  - each volunteer: their own code from  python scripts/pilot_users.py add \"Name\""
echo

cd backend
exec ../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
