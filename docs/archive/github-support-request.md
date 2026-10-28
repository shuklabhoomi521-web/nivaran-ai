# Draft message to GitHub Support (for the founder to send)

Where to send: https://support.github.com/contact  (choose "Account or repository" -> "Removing sensitive data" if offered).
GitHub's own help page on this topic: "Removing sensitive data from a repository". Send it from the GitHub account that owns the repo (shuklabhoomi521-web).
Do not create a new repository: this request asks GitHub to clean the existing one.

---

**Subject:** Please run garbage collection and clear cached views for private repository shuklabhoomi521-web/nivaran (personal voice recordings committed by mistake)

Hello GitHub Support,

I own the private repository **shuklabhoomi521-web/nivaran**. On 2026-10-19 I accidentally committed 10 audio files containing my own voice
(personal voice recordings) in commit 9dec69a. I have since rewritten the repository history to remove them (git filter-repo) and
force-pushed `main`. The branch `main` now points to **355c4a63478bdd14378af543f1abf458a9e12f19** and no longer contains the files.

The old commits and files can still be retrieved through the API by their exact IDs. For example
`GET /repos/shuklabhoomi521-web/nivaran/git/commits/9dec69a08db6ff02b640b216f6b257ed1b3714ac` and `GET /repos/shuklabhoomi521-web/nivaran/git/blobs/e2772adb2952679f8a41de281563f4b472fc28a3`
both still answer. The repository is private, has no forks and has no pull requests.

Could you please:
1. run garbage collection on the repository so that the unreachable objects listed below are permanently deleted, and
2. clear any cached views and other cached copies of those commits and files.

**Old commit IDs that are now unreachable (the first one contains the files; the others descend from it):**
- 9dec69a08db6ff02b640b216f6b257ed1b3714ac
- e839520720b107ea48525012a503029ff26a9e64
- 297af5443fad69e81a6c0c51e034c177d87ba5bf
- ad96e54bf054f63e4ff8b52d4979e29411b50a77
- 03f0e2e7e0ea37b3b980aad65e48805c0f171d99
- de618bee3ee02b81ffa184c1eb0839309799b6c9
- 9112c643cd445ae721d2cf08c1175ea255f4bd9d

**Blob IDs of the files to delete (10 audio files, plus a small JSON file that was in the same folder):**
- e2772adb2952679f8a41de281563f4b472fc28a3  (clip01_hinglish.aac)
- 9692b7482f0d304d729aae43b8e27390321b1770  (clip02_hinglish.aac)
- 6270c8776367d8f4646ef24f9612040061b68c26  (clip03_hinglish.aac)
- fbae2f9a161ea039f4525e17815784a70d7a3fe0  (clip04_hinglish.aac)
- e72d201da70217cc9999d3d35fbfb7a7d773a205  (clip05_hinglish_noisy.aac)
- fcb5659a4b20a64a4f63ac1147fbf63ecda42252  (clip06_en_in.aac)
- 10b79a5bc5471ef38243feda652cf08e0c0d6ecc  (clip07_en_in.aac)
- a69a2f34221f600182af008a0c4be924035bd1e6  (clip08_en_in.aac)
- 678af73b0cd4a93f4aab52c28910338e4343634f  (clip09_en_in.aac)
- e1e94d523bc8db100a2930c89f3a2bedf47d2e47  (clip10_en_in_noisy.aac)
- 36c9bbb0180da4962a249a54743b37f8646e858b  (sentences.json)

Current state, for reference: `main` = 355c4a63478bdd14378af543f1abf458a9e12f19; the tags `phase-0-done`, `phase-1-done` and `phase-2-done` are unchanged.

Please tell me if you need anything else from me. Thank you.

{your name}
GitHub username: shuklabhoomi521-web
