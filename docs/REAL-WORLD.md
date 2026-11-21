# Nivaran in the real world: what works, what does not (22 Nov 2026)

Plain status for v1.0. Details sit in `docs/notes/`.

## Works today (tested, on a laptop)
- Verified official contacts for 49+ companies, each with its source page and exact quote.
- Case ladder (day 0, 3, 7, 15) from first contact to regulator.
- Grievance letter from the user's own facts, template only, sent after approval to directory addresses only.
- Read-only reply tracking, portal kits (helpline portal, RBI, IRDAI/AirSewa) with ready complaint text.
- English, Hindi, Tamil screens (Hindi and Tamil are a first draft, not checked by a native speaker).
- Privacy: encrypted storage, consent, 18+ confirm, delete my data, personal access tokens, owner-only access.

## Not proven yet
- Real phone use of the app (only a web preview was checked), real microphone, real iOS 26 glass.
- Any phone call. Provider access is blocked (FreJun account help pending; Twilio could not reach our server through the tunnel).
- Pilot with real volunteers (kit ready in `docs/pilot/`, zero cases run).
- Portal steps for AirSewa and e-Jagriti are unverified.

## Phone route decision
Phone is an optional channel, not part of the v1.0 promise. If FreJun unlocks a sandbox, we test a call to the builder's own number only. Real calls to companies stay off: TRAI's A2P rules treat software-started calls as A2P, so a verified provider and declaration are needed first.

## Hosting decision
Azure for Students has no cheap VM size available (South India). The pilot runs on the builder's laptop with `scripts/run_pilot.sh`; revisit after exams.

## Honest limits
Nivaran is not legal advice and not "TRAI compliant". It never reads OTPs, cards or PINs. It does not contact any company without the user's approval.
