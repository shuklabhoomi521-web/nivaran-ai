# Security audit of the full git history (2026-10-28)

Scope: all 68 commits on all branches and tags, before making anything public. Method: `git grep` over every commit, plus a check of every file name ever tracked and the biggest stored files.

| Check | Result |
|---|---|
| `.env` files ever committed | **None.** Only `.env.example` (placeholders; no real keys). |
| API keys: Google `AIza…`, Groq `gsk_…`, `sk-…`, GitHub tokens, private keys, Twilio `AC…`/`SK…` IDs | **None found** in any commit. |
| The real values in the local `.env` (3 API keys, Twilio SID and token, the allowed and the caller phone numbers) searched for in history | **None found.** |
| Personal phone numbers | **None found.** The only numbers are public company helplines in the directory, and Twilio's published test number in a unit test. |
| Audio / recordings / archives (wav, mp3, m4a, aac, zip, …) in any commit | **None.** Biggest stored file is the 300 KB demo GIF. File hashes of the purged recordings are mentioned in text only. |
| `speech_test/holdout/*.json` | Text transcripts and sentences of practice clips, no personal data. Audio is git-ignored. |
| Encrypted call transcripts, `.transcript_key`, `.sarvam_credits.json`, usage files | Git-ignored; never committed. |
| Email addresses | Public company grievance emails from the directory, plus the commit author (below). |

## Found and fixed in this commit
- `speech_test/README.md` contained the founder's local folder path (`/Users/…`): replaced with relative paths.
- `docs/archive/github-support-request.md` (internal note with the old repo name and hashes of purged files) removed from the tree.

## Still true after the fix (needs a founder decision)
1. **Old commits still contain** the two items above and an old review brief with the private repo name. They are harmless (no secrets), but they stay in the history unless the public repo starts from a single fresh commit.
2. **All 68 commits are authored with the founder's personal Gmail address.** On a public repo this address is visible to everyone. Fix: use GitHub's `…@users.noreply.github.com` address, which means the history is rewritten (or squashed) before publishing.
3. **The author name** on the commits (`Bhoomi Shukla`) differs from the name in the local folder paths. Check this is the name you want public.

Not checked: GitHub's own cache of the OLD private repo (not reachable by anyone else while it is private).
