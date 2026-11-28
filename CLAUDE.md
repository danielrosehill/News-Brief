# News-Brief — maintainer notes

- Release tier: **small** (`v1.0`, `v1.1`, …). Keep `.claude-plugin/plugin.json` `version` in step.
- Shipped packages live in `packages/`: `israel-breaking`, `jns-toi`. Users' packages go in their user-data dir, never here.
- Every feed URL in a shipped package must be verified before commit (items returned, newest item recent); bump the package's `verified` date.
- All `scripts/*.py` stay stdlib-only (fetch_package, news_search, telegram_preview).
- `references/research-routes.md` holds the dated status of every search and social route (X, Telegram, Reddit). Re-test and re-date it when a route changes; never ship a "works" claim you did not run.
- No personal details in this repo: user email, Drive folders and hosts live in the user's `<user-data>/config.json` and `notes.md`.
- Known feed quirks are documented in `README.md` → "Feed notes".
