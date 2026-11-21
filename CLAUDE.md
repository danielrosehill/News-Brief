# News-Brief — maintainer notes

- Release tier: **small** (`v1.0`, `v1.1`, …). Keep `.claude-plugin/plugin.json` `version` in step.
- Shipped packages live in `packages/`; only `israel-breaking` ships. Users' packages go in their user-data dir, never here.
- Every feed URL in a shipped package must be verified before commit (items returned, newest item recent); bump the package's `verified` date.
- `scripts/fetch_package.py` stays stdlib-only.
- Known feed quirks are documented in `README.md` → "Feed notes".
