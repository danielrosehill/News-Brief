# Situation Report (SITREP)

A conventional intelligence-style situation report: header, BLUF, sections by theatre or topic, assessment. Fetch with `--brief sitrep` (24 hours by default; `--hours` sets the reporting period).

## Structure

```
SITREP <package name> — <DD MMM YYYY> <HHMM><zone letter or tz>
Period covered: <from> to <to>
Classification: UNCLASSIFIED // OPEN SOURCE
Sources: <n> open-source outlets (<list of outlets that contributed>)

1. BLUF
   3–5 numbered points. Each self-contained, most significant first.
   Definitive where corroborated; qualified where single-source.

2. SITUATION
   2a. <Theatre / topic, e.g. Gaza>   — opens with a one-sentence summary, then detail.
   2b. <Lebanon / northern front>
   2c. <Iran and the wider region>
   2d. <Domestic: politics, government, legal>
   2e. <Diplomacy>
   2f. <Economy / infrastructure / civil>
   (Use only the theatres the period's reporting supports.)

3. KEY EVENTS (chronological)
   <DD HHMM> — <event> (<source>)

4. ASSESSMENT
   Analyst judgement on trajectory. Use estimative language (below).
   Separate clearly from reporting.

5. INDICATORS TO WATCH
   2–4 things that would signal escalation, de-escalation or a change.

6. SOURCE NOTES
   Feed gaps; single-source claims; conflicting accounts.
```

## Conventions

- **Sentence pattern:** timeframe → actor → action → object → source. "On 21 Nov, the IDF struck … according to the IDF spokesperson."
- **Dates:** `DD MMM YYYY` in the header (`21 NOV 2026`); 24-hour times; state the zone.
- **Numbers as numerals.** Distinguish confirmed from reported figures ("at least 4 killed, per Al-Monitor").
- **Attribution:** every non-obvious claim names its outlet; claims that the outlet itself attributes ("officials said") keep that attribution.
- **Estimative language** (section 4 only): almost certainly (~95%), very likely (~80%), likely / probably (~65%), roughly even chance (~50%), unlikely (~30%), very unlikely (~15%), almost no chance (~5%). Never in section 1–3 as a substitute for reporting.
- **Neutral register.** Report each party's claims as claims. No adjectives that take sides.
- Length: 600–1,200 words. Voice delivery reads only sections 1 and 4, then offers the rest.
