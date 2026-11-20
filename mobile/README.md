# Nivaran mobile app (Expo, TypeScript)

First version (sprint day 7 work): list your cases, start a new case, and run a case step by step. It talks to the backend over HTTP and holds no secrets.

## Run it
1. Start the backend on your laptop: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Find the laptop's address on your Wi-Fi (for example `192.168.1.20`). The phone and laptop must be on the same network.
3. `cd mobile && EXPO_PUBLIC_API_URL=http://192.168.1.20:8000 npx expo start` and open it in the Expo Go app (or press `i` for the iOS simulator).

## Screens
- **My cases:** every case with its state (not sent yet, waiting, escalated, solved, closed).
- **New case:** type the problem once; the server removes card, PIN and OTP text, the AI shows what it understood, you confirm the company and your name.
- **Case:** the ladder (first message, follow-up, grievance officer, appellate authority, regulator), the next step with the verified contact and the official quote, the letter (edit, approve, then send, each a separate tap), the portal filing kit (official steps with quotes, our checklist, complaint text to copy, docket number), inbox check for replies, mark solved or stop, delete my data.

## Design: liquid glass
Frosted, translucent panes over a soft colour backdrop (`src/glass.tsx`, `src/surface.ts`).
- iPhone with iOS 26 or newer: Apple's real liquid glass (`expo-glass-effect`).
- Other phones: a frosted blur (`expo-blur`). Browser preview: a CSS backdrop blur.
- If the person turns on **Reduce Transparency** (an accessibility setting), every pane becomes opaque and high contrast.
- Text stays dark on light glass; the primary button is a blue-tinted pane with white text.
Checked in a browser preview only. The real iOS 26 glass has not been seen on a device (this Mac has no full Xcode).

## Rules the app follows
- Nothing is sent without the user approving the exact text and tapping Send, then confirming.
- The app never types a password, OTP, PIN or card detail anywhere.
- The list screen shows only company and state, not the facts.

## Checks
`npm test` (27 unit tests for the API client and formatting), `npm run typecheck`, and CI runs both. `npx expo export --platform ios` builds the bundle.

Known: `npm audit` reports 3 moderate issues in `minimatch` inside Expo's own build tools (not shipped in the app); the suggested fix would downgrade Expo to an old major version, so it is left alone.
Not yet: voice input, push reminders, login, an installable Android build.

## Voice input (new)
On the New case screen, "Speak instead of typing" records up to one minute, sends it to the backend (`POST /speech/transcribe`), and puts the text in the box for the user to check and fix. The backend uses the speech-to-text with automatic fallback, removes spoken card numbers and PINs (strict mode), and never stores the audio. The microphone is asked for only when the button is tapped.
Checked: the endpoint and helper functions have tests; the app bundle builds. **Not tested with a real microphone or on a phone yet.**
