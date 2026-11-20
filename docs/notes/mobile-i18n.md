# App languages, reminders and builds (sprint work, 2026-11-21)

## Hindi and Tamil text
`mobile/src/i18n.tsx` has 32 labels in English, Hindi and Tamil, used on the cases list, new case and case screens (titles, main buttons, consent checkboxes). The user picks the language on the cases list.
- **The Hindi and Tamil text is a first draft. A native speaker has not checked it.** Do not call it final.
- **Still English only:** the privacy notice from the server, letters, portal kits, error messages, the call screen, and the AI's replies in the understanding step (those already follow the user's language). The privacy notice should be translated and checked by a native speaker before real Hindi or Tamil users, because consent has to be understood.
- The chosen language is kept only while the app is open (no storage yet).
- Tests check that every key exists in all three languages, none is empty, and each uses the right script.

## Reminders
`mobile/src/reminderPlan.ts` and `reminders.ts`: when a case is opened, the phone schedules one local notification at 10:00 for each ladder step that is still ahead, and cancels them when the case is solved, closed or deleted. The text is generic ("A step is due on one of your cases: follow-up.") so nothing private shows on a lock screen. Notifications need the user's permission, are skipped in the browser preview, and a failure never breaks the case screen. Reminders only update when the app is opened (no server push yet).

## Android build
`mobile/app.json` (name Nivaran, id `app.nivaran.mobile`) and `mobile/eas.json` (preview profile builds an installable APK). To build, the builder logs in to a free Expo account: `cd mobile && npx eas-cli login && npx eas-cli build -p android --profile preview` after replacing `CHANGE-ME-LAPTOP-IP` in `eas.json` with the laptop's address. **Not built yet: it needs the builder's own Expo login.**
- **Security note:** an app built with `EXPO_PUBLIC_API_TOKEN` carries that token inside the file, so anyone who gets the APK can extract it. That is acceptable only for a small pilot on phones the builder gives out, with a backend reachable only on the builder's Wi-Fi. Real accounts and a login come before any public release.
- An iPhone build needs a paid Apple developer account and is not planned for v1.
