# DPDP basics for Nivaran (read 2026-11-19)

Not legal advice. Sources are law-firm and news summaries of the Digital Personal Data Protection Act 2023 and the DPDP Rules 2025 (notified 13-14 Nov 2025). I did **not** read the Gazette text itself. Dates differ by a day between sources.

## When it applies
- Rules notified Nov 2025, in phases. Board set-up: immediately. Consent Managers: about Nov 2026. **Core duties (notice, consent, security, breach, erasure, children): about 18 months later, around mid May 2027.**
- Our pilot (late Dec 2026) is before that date. We still build to the rules now, because real people's complaint data is involved and fixing it later is harder.

## Who we are under the law
Once real users type their name, phone number, email, order details or voice into Nivaran, we decide why and how that data is used. That makes us a **Data Fiduciary** (the one responsible). The user is the **Data Principal** (the person the data is about).

## What the rules ask, and what we do
| Rule (from summaries) | What Nivaran does | Plan day |
|---|---|---|
| Plain-language notice before collecting: what data, why. Purposes shown clearly | One consent screen in simple words and Hindi/Tamil: "we use your complaint details to write to the company and track the case" | C7, 22 Dec |
| Withdraw consent as easily as giving it | "Withdraw and delete" button | C7 |
| Reasonable security: encryption or masking, access control, logs kept 1 year, backups | Private fields already encrypted in design; redact logs; keep logs 12 months | C7 |
| Breach: tell affected people at once, tell the Board, detailed report within 72 hours | Write a one-page breach plan (who, how, what to say) before the pilot | C9 prep |
| Delete data after 1 year of inactivity, with 48 hours' warning | Scheduled cleanup job and an email warning | C7 |
| Under-18s need verifiable parent consent | Pilot is adults only; sign-up asks age and blocks under 18 | C7 |
| Publish contact of a responsible person; users can access, correct, delete | A "Contact / privacy" page with your email; export and delete buttons | C7 |
| Some data may need storage in India (categories to be named later) | Keep Supabase and files in an India or Singapore region where possible; avoid sending real data abroad without a reason | C7 |
| Penalties up to Rs 250 crore for a security failure, graded for small firms | Small scale, but treat it seriously | all |

## Things specific to our design
- **Free-tier AI (Gemini) may train on prompts.** Real users' data must not go there. Before the pilot we either use a paid or self-hosted route or use only the consenting volunteers' non-sensitive text. (Already in CLAUDE.md.)
- **Call recordings and transcripts are personal data.** Store only if needed, say so in the notice, delete on request.
- **Never store OTP, PIN or card data.** Already a hard block in code.
- Pilot volunteers sign a one-page written consent (C9, 26 Dec) that matches the notice.

## Still unknown
Exact text of the rules on grievance timelines and cross-border limits. Check the Gazette text or ask a lawyer before real users beyond the pilot.
