# Gemini free tier: model choice and limits (checked 2026-10-15)

## Official facts (Google pricing page)
Models with a free tier (free input and output): `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`,
`gemini-3.1-flash-lite`, `gemini-3-flash-preview` (preview, legacy), `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`.
- Google's docs do **not** publish per-model free numbers. They say limits depend on your project and are shown in AI Studio: https://aistudio.google.com/rate-limit
- Free-tier prompts and answers **may be used to improve Google's products**. Paid tier does not. So: test data only.

## Unofficial numbers (third-party blogs, conflicting, verify in AI Studio)
- One Sept 2026 guide: 3.8 / 3.7 / 3.6 / 3.5 Flash about **20 requests per day**; 3.5 Flash-Lite and 3.1 Flash-Lite about **500 per day**.
- A June 2026 guide (older models): 2.5 Flash 10 per minute, 500 per day; 2.5 Pro 5 per minute, 25 per day.
- Pro models reportedly left the free tier in spring 2026 (unconfirmed).

## Choice
Default `gemini-3.5-flash-lite`: stable, free, built for high volume, and the biggest daily allowance in the numbers above.
Our 30-problem run needs at least 30 calls per day, which 20-per-day Flash models cannot do in one day.
Trade-off: Flash-Lite may be weaker on Tamil and Hinglish than `gemini-3.8-flash`. The baseline run will show it.
If your AI Studio page shows a daily limit of 30 or more for `gemini-3.8-flash`, set `GEMINI_MODEL=gemini-3.8-flash` and compare.
The run saves its progress, so a 20-per-day model can still finish across two days.

## Our slow-down
`GEMINI_RPM` (default 5) spaces calls; `GEMINI_RPD` (default 0 = off) stops before a daily cap. Set both to your AI Studio numbers.
A 429 from Google is retried after the delay Google suggests; a "per day" 429 stops the run cleanly.
