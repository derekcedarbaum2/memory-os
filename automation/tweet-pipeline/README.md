# tweet-pipeline — turn your Slack tweet-shares into a topic-routed research corpus

A weekly cron that finds new x.com URLs shared anywhere in your Slack workspace, scrapes each tweet's full body using a logged-in browser session, classifies it into a topic, and appends to topic-tagged Markdown files in your vault.

Same shape as [`../auto-distill-readwise.sh`](../auto-distill-readwise.sh) — external source → vault topic files. The difference is the auth path: X actively blocks Playwright-launched logins, so this script lifts cookies from your real browser (Chrome / Safari / Brave / Firefox) where you're already logged in. Zero ongoing cost.

## Why this exists

Sharing a tweet to a Slack channel is a habit most people already have. Without this pipeline, those shares get buried in 90 days and the value goes to zero. With it, the same behavior auto-builds a permanent, searchable, topic-organized research corpus. You don't change what you do; you change what accrues.

Practical impact: when you're writing a positioning doc 3 months from now and need to cite "what the consensus was on X this spring," you grep your own vault for cited sources you already vetted, instead of starting research from scratch.

## What it does, per run

1. **Slack search** — hits Slack's `search.modules` directly with browser-session tokens (`xoxc` + `xoxd`). No bot token needed; no Slack app to install. Returns every message containing `x.com` from the last 8 days.
2. **Diff** — compares against `state.json` (URLs already processed). First run seeds from your existing master file's `.bak` so historical shares aren't re-processed.
3. **Scrape** — launches headless Chromium with the cookies in `storage_state.json`, opens each tweet URL, extracts main post + thread continuation via DOM querying.
4. **Classify** — keyword routing into one of 7 topics (configurable in `pull.py`'s `TOPICS` list).
5. **Append** — finds the right `tweets-<topic>.md` file in your vault, inserts the new entry under the correct channel heading (newest-first).
6. **State save + vault log** — updates `state.json`, appends a canonical pipe-separated line to `Vault/log.md`.

## Setup

```bash
cd ~/projects/memory-os/automation/tweet-pipeline

# Create venv + install pinned deps
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium

# Configure secrets
cp .env.example .env
$EDITOR .env   # fill in SLACK_XOXC_TOKEN, SLACK_XOXD_COOKIE, SLACK_WORKSPACE_DOMAIN

# Import cookies from your real browser (one-time; reissue when X invalidates them)
.venv/bin/python import_cookies.py chrome   # or safari, brave, firefox
# A macOS Keychain prompt will appear. Click Always Allow.

# Smoke test
.venv/bin/python pull.py
```

Schedule it (macOS):

```bash
cp ../plists/com.user.tweet-pipeline.plist ~/Library/LaunchAgents/
# Edit the absolute paths inside if your checkout isn't in ~/projects/memory-os
launchctl load ~/Library/LaunchAgents/com.user.tweet-pipeline.plist
```

## Where the auth trick lives

The X risk system blocks Playwright-launched logins (browser fingerprint screams "automation"; you'll get "Sorry, you are not allowed to log in at this time" even with the right password). The workaround in [`import_cookies.py`](import_cookies.py) is to never log in via Playwright at all — instead, decrypt cookies from your real browser's local DB using [`browser-cookie3`](https://github.com/borisbabic/browser_cookie3), filter to `x.com` only, save to Playwright's `storage_state.json` format. The headless Chromium then loads those cookies and looks like a logged-in browser. No login flow, no fingerprint mismatch.

Reading the cookie DB requires macOS Keychain access. You see one prompt the first time the script runs. Only x.com cookies are extracted; nothing else is read, persisted, or transmitted.

## Where the Slack-search trick lives

Slack's user-facing search endpoint (`search.modules`) accepts your browser-session tokens directly. Most automation defaults to bot tokens (`xoxb-...`), which can't see private channels or DMs the bot isn't in. Browser-session tokens (`xoxc-` + the `d` cookie) give you the same access your normal Slack client has. The trick is correct parsing: messages are nested in `item.messages[]`, not at the top level, and unfurled URLs come from `attachments[].from_url`/`original_url` in addition to message text.

[`pull.py`'s `slack_search_xcom_urls`](pull.py) is ~50 lines and handles pagination, deduplication, and date filtering with belt-and-braces (Slack's `after:` filter plus a Python-side cutoff).

## Topic classifier

Hand-tuned regex over keywords, with a backstop pass for entries that don't match any specific topic. Not ML, not embeddings — keyword routing is good enough for 222+ tweets and trivial to debug. Adjust the `TOPICS` list at the top of `pull.py` to match your own taxonomy.

## What gets touched in the vault

- **Appended to:** `Vault/Research/X Research/tweets-*.md` (your topic files — must already exist)
- **Appended to:** `Vault/log.md` (one canonical line per run: `TIMESTAMP | tweet-pipeline | event | body`)
- **Never modified:** `Vault/Research/X Research/Tweets-from-Slack.md` (the index — hand-curated)
- **Never deleted:** anything, ever

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `Slack search error: {... "error": "not_authed"}` | Slack tokens stale (rotated, you logged out) | Re-extract `xoxc` + `xoxd` from your browser devtools and update `.env` |
| `!! STOP — 3 consecutive failures` after a few clean weeks | X cookies invalidated (you logged out, X cycled session) | Re-run `import_cookies.py <browser>` |
| `topic file ... doesn't exist — skipping append` | Vault topic file missing | Create it once with frontmatter + a `## <channel-id>` heading, then re-run |
| Run silently exits with `Another run is in flight` | Previous run hung; lockdir not cleaned up | Lockdir auto-clears after 2h. To force: `rm -rf /tmp/tweet-pipeline.lock` |

## Caveats and limits

- **Slack ToS:** automation against Slack with browser-session tokens is in a grey area. Slack tolerates personal-use scripts but reserves the right not to. Your tokens, your account.
- **X ToS:** view-only scraping with your own session at human pace is also grey. The cron does 10-20 reads/week — far below any rate limit. Risk scales with volume.
- **Cookies expire.** Couple of weeks typically, sometimes faster if X cycles sessions or you log out elsewhere. The fail-fast trip wire stops the run after 3 consecutive empties so you don't hammer the auth wall.
- **Mac-only schedule.** The pipeline scripts are portable Python; the `launchd` plist is macOS-specific. Adapt for `cron`/`systemd` if needed.

## File map

| File | Purpose | Gitignored? |
|---|---|---|
| `config.py` | Reads `.env`, hardcodes vault paths (memory-os convention) | no |
| `pull.py` | Main pipeline. Idempotent. Lockdir-protected. | no |
| `import_cookies.py` | One-time + recurring cookie importer | no |
| `requirements.txt` | Pinned deps (Playwright, browser-cookie3, requests) | no |
| `.env.example` | Template for required secrets | no |
| `.env` | Your actual secrets | **yes** |
| `storage_state.json` | Playwright auth state from your browser cookies | **yes** |
| `state.json` | Set of all URLs already processed | **yes** |
| `runs.log` | Per-run log lines | **yes** |
| `.venv/` | Python venv | **yes** |
