# Next steps, saved 26 Nov 2026 (the day-by-day list)

Rule of the days: Tue 24 Nov, Sun 29 Nov, Thu 3 Dec are rest days in the sprint plan; exams on 25 Nov, 30 Nov, 1 Dec, 4 Dec. "You" = Bhoomi, "Claude" = me.

## Running by itself now
- DONE 26 Nov 02:45: the Android app is built and downloaded to ~/Desktop/Nivaran_APK/Nivaran_20261126.apk (75 MB, valid). Expo link expires 9 Dec 2026: share the file itself.

## Fri 27 Nov (tomorrow)
1. Claude: check the APK is in `Nivaran_APK` (if the build failed, read the log and fix).
2. You: install it on your phone; run `bash scripts/run_pilot.sh`; type the server address and access code; Claude and you test one full case (do NOT press Send on a real company).
3. Claude: send 8 follow-up emails (12 are due now; 34 in total are still to go).
4. Claude: check Gmail for replies and for LinkedIn "accepted your invitation" emails (tell Claude: "check replies").
5. You: send the first LinkedIn requests (the pack is in `LinkedIn_Outreach_Pack.zip`); decide the three friends.

## Sat 28 Nov
- Claude: send 8 more follow-ups (18 more companies become due today). Check replies and LinkedIn acceptances; prepare the follow-up message for each accepted person (you paste it and attach the tailored resume PDF).
- Claude: write the one-page checklist for each friend's test; make their access codes when you give the names.

## Sun 29 Nov (rest), Mon 30 Nov and Tue 1 Dec (exams)
- Claude: keep sending 8 follow-ups a day while you rest or study (the laptop must be on).

## Wed 2 Dec
- Claude: last follow-ups (4 more become due: Operonn, Stance Health, smallcase, WebEngage). Print the consent forms list. Decide where friends will test (same Wi-Fi, your hotspot, or a tunnel).

## Thu 3 Dec (friends start)
- You: friends install the app, sign the consent form (`docs/pilot/CONSENT.md`), each uses their own access code, tries ONE real complaint with a company from the 58. Laptop on and running `run_pilot.sh`.
- You: write each result in `docs/pilot/RESULTS.md` the same day, failures too.

## Fri 4 Dec (exam), evening: start the real server
- Claude: test the Azure student credit in West India and a US region (you click in the portal); write the setup script (Python, secure address, systemd restart); a database; hourly backups (`scripts/backup_data.sh` exists). Needs: your Azure portal clicks.

## Sat 5 to Mon 7 Dec: finish v1.0
- Claude: fix the top problems from the pilot; update README with the demo video and the real pilot results; run all tests; tag v1.0 and push.
- You: upload the demo video if you want it public.

## After v1.0
1. Real accounts (Supabase Auth) instead of access codes, then a proper database.
2. A native speaker checks the Hindi and Tamil text.
3. A paid or self-hosted AI model before real public users (free AI tiers are for test data only).
4. Court-ready summary from the case timeline (for e-Jagriti); per-company response times; RBI and Rail Madad kits.
5. Phone calls: FreJun account help, a verified provider, the TRAI declaration. Real company calls stay OFF until you say so.
6. Play Store: $25 fee (check Google's page), a closed test with 12 testers for 14 days, privacy policy, data-safety form, a live server first. About 4 to 6 weeks after the server is live.

## Always
- Emails: only publicly posted hiring addresses; one follow-up per company; 8 a day at most; never guess an address.
- LinkedIn: you send requests and messages by hand (no API; automation breaks its rules). Claude only reads the notification emails to see who accepted.
- Never press Send on a letter to a real company during tests.
