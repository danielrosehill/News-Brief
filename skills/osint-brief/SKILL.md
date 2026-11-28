---
name: osint-brief
description: In-depth open-source (OSINT) analysis of a topic: news, Telegram, X, Reddit, official statements, contested claims cross-checked against the other side. States which platforms could not be read.
---

# OSINT brief

A deeper read than `topic-scan`: what happened, what each party claims, what the primary sources and social media show, and how confident we can be. Output in chat or as a PDF.

## Inputs

- **Topic or incident**, the **window**, and the **question** the reader needs answered (what happened? who is responsible? what next?).
- Known parties and their channels, if the user has them; otherwise from config `osint.telegram_channels` and `osint.x_accounts`, else find them.
- Output: chat, or PDF to Drive, email, print.

## Steps

1. Read `references/research-routes.md` (which routes work, verified 2026-11-28) and, for a PDF, `references/delivery.md`.
2. **Map the parties**: for each side, its official voices (government, army, police, spokespeople, courts, agencies) and where they publish (site, Telegram channel, X account).
3. **News layer**: as in `topic-scan` (news_search.py per language, WebSearch, Exa with the window in `objective`). Include the other side's media in its own language.
4. **Official statements**: fetch the primary statement each party issued. Link it; if only a report of it exists, say so.
5. **Social layer**, each platform recorded as read, partly read or not read:
   - **Telegram**: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/telegram_preview.py <channels...> --hours <N> [--q "<term>"]`. Name channels from step 2; there is no global Telegram search.
   - **X**: no search route works without a logged-in account. Read named accounts in a real browser (`x.com/<handle>`, recent posts only, open a post for its exact time), and use posts quoted by news outlets or archived on archive.ph. Say "X search not available" in the brief.
   - **Reddit**: blocked to scripts; the paid route is `social-feedback:reddit-discourse` (Apify). Ask before spending; otherwise list Reddit as not read.
6. **Cross-check every contested claim**: put the competing accounts side by side with attribution, look for a third source that settles it (court record, imagery, independent monitor, UN), and grade it: confirmed (independent sources agree), reported (one side or one outlet), disputed (accounts conflict), unverified (social media only).
7. Write:
   ```
   Bottom line: the answer to the reader's question, with likelihood words where judgement is involved.
   What happened: dated timeline, sourced.
   Claims and counter-claims: table or entries, claim | source | counter-account | status.
   Social media: what circulated, where, how it matched the record.
   Assessment: judgement, what would change it.
   Collection gaps: platforms not read, sources that failed, what is unknown.
   ```
   Separate what is reported, inferred and assumed (report-writing shared rules). Likelihood uses one scale (ICD 203).
8. PDF: brief JSON (`panels` for judgements, `table` for claims, `entries` for sources), render, inspect, deliver per `references/delivery.md`.

## Notes

- Social posts are claims, not facts, until matched to an independent source. Quote short; give the account, time and link.
- Do not reproduce graphic content or personal data of private individuals.
