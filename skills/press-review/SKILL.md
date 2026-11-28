---
name: press-review
description: Translated press review: scan one language's media (e.g. Hebrew, Arabic) on a topic over a window; per article outlet, date, original and translated headline, link, main points; how outlets differ; PDF to Drive.
---

# Press review

One entry per article from the target language's media, translated into English, plus a short read of how the outlets differ. Default output: PDF saved to Google Drive.

## Inputs

- **Topic**, in the user's words. Restate it neutrally; if the user's framing may be off (a "lawsuit" that is really an appeal), keep their wording for the search and correct it in the bottom line.
- **Language** of the media (`he`, `ar`, `ru`, `fr` ...) and the country edition (`IL` for Israeli Hebrew; config `press_review.regions` may set it).
- **Window**: past day, week (default) or month, as dates with timezone.
- **Delivery**: PDF to Drive by default; email or print only if asked.

## Steps

1. Read `references/research-routes.md` and `references/delivery.md` at the plugin root, and `<user-data>/config.json` and `notes.md` if present.
2. **Write 3-6 queries in the target language**: the place or institution, the people, the event or legal word, and one bare name with no topic words. Include common spellings and slang names.
3. **Search at the window first:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/news_search.py "<q1>" "<q2>" ... --lang he --region IL --days 7 --resolve
   ```
   Then 1-2 Exa searches with the window in `objective`. For Israeli Hebrew media, `israel-osint:media-scan` and `israel-agent-skills:israel-news-rss` are alternatives.
4. **Zero relevant hits at the window is a finding.** Say so in the bottom line, then widen (30 days) only to show the last coverage, and label the widened window everywhere.
5. **Read every article you list** (Exa fetch, WebFetch, curl). Drop off-topic hits (sports clubs, restaurants that share a name). If only the headline and standfirst load, say so in the entry. Respect paywalls.
6. **Check every link resolves** (HTTP 200 and the page title matches) on the day. Leave out articles whose page does not load, and name them under Method.
7. **Translate**: headline faithfully (keep the outlet's tone, slang and quotes); 1-4 bullets of main points in English, each one fact or claim, attributed. Mark the outlet's own claims as theirs.
8. **Compare outlets** (3-5 bullets): who had original reporting, who ran the press release near verbatim (shared phrases give it away), framing and sympathies, what only one outlet reported, whose response is missing.
9. Build the brief JSON: `bottom_line` (what happened, what the coverage shows, gaps), section "How coverage differs" (bullets), section "Articles" (`entries`: `tag` = "<DD Mon YYYY HH:MM> | <outlet in English>", `title` = translated headline, `original` = headline as published, `link`, `bullets`), section "Method" (`facts`: request, window, searches, exclusions, link check, translation note), `note` for background. Shape: `examples/press-review-mahane-yehuda.json`.
10. Render, inspect pages, deliver (`references/delivery.md`). Report the Drive link and each channel as delivered, skipped or failed.

## Worked example

Request (2026-11-28): "scan Hebrew media coverage over the past week of the Jerusalem Municipality suing the bar owners in the Mahane Yehuda market; translated press review with links and main points; PDF to my Drive".

- Seven-day Hebrew Google News queries (`"מחנה יהודה"`, `מחנה יהודה ברים`, `שוק מחנה יהודה עירייה`, `מחנה יהודה ערעור עליון`, `מחנה יהודה רעש`) returned only sports, food and unrelated items. Exa agreed. Finding: **no coverage in the window**.
- Widened to 30 days: nine Hebrew articles of 12-13 November 2026 on the city's **appeal to the Supreme Court** against the July ruling won by eight bar owners. The user's "suing" was really this appeal; the bottom line says so.
- Six of nine outlets restated the city's press release; Mynet Jerusalem had the original reporting; Channel 14 was the one critical frame; no outlet carried the bar owners' response.
- Result: `examples/press-review-mahane-yehuda.json`, a 4-page A4 PDF.

## Notes

- Network: Google News RSS (no key), Exa (paid, a few cents per call), article pages. Keep Exa to what the window needs.
- Never invent a headline, date or quote. A headline you could not read in full is labelled "headline only".
