# Using News Brief behind a voice assistant

The suggested way to use this plugin day to day is on demand by voice: "what's happening?", "give me the daily brief", "read me a sitrep". This page describes the integration pattern; it ships no voice code.

## Pattern

```
wake word / push-to-talk
  → speech-to-text
  → intent: breaking | daily | sitrep (+ optional package, window)
  → fetch_package.py --brief <type> [--package <id>] [--hours N]     (stdlib Python, ~2–5 s)
  → LLM writes the brief using references/<type>.md + references/voice-delivery.md
  → text-to-speech
```

- **Default intent is `breaking`.** "Any news?", "what's going on?", "what's happening in Israel?" all map to the Breaking News Brief; only "daily brief", "today's news", "catch me up on today" map to the Daily Brief.
- **Keep the fetcher outside the model.** Run `scripts/fetch_package.py` as a tool or subprocess and hand its JSON to the model. The model never needs web access, which keeps the brief inside the source whitelist.
- **Prompt.** System prompt = `references/shared-rules.md` + the format file + `references/voice-delivery.md`. User turn = the JSON bundle plus the spoken request.
- **Latency.** The fetch is parallel (8 workers, 15 s timeout per feed). Cache the JSON for ~5 minutes if the assistant gets repeat requests.
- **Follow-ups.** Keep the JSON in the conversation so "tell me more about the Hormuz story" can be answered from the same bundle, opening that story's links if needed.

## Wiring options

- **Claude Code / Agent SDK:** install the plugin; the `breaking-brief`, `daily-brief` and `sitrep` skills already handle a "voice" delivery request.
- **Any assistant with tool calling:** expose one tool, `news_brief(brief: "breaking"|"daily"|"sitrep", package?: string, hours?: number)`, that runs the fetcher and returns its JSON; put the reference files in the system prompt.
- **Home Assistant / scripted assistants:** call the fetcher from a shell command, send JSON + prompt to an LLM API, speak the reply through the assistant's TTS.
