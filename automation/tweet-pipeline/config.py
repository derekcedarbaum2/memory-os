"""Pipeline config. Tokens come from .env; paths are hardcoded per the
memory-os 'configuration is the artifact' principle — when you adopt this,
you edit the paths directly so the assumptions stay visible in the code.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


# ─── Secrets from .env ───────────────────────────────────────────────────────

def _load_env():
    """Minimal .env loader so we don't depend on python-dotenv."""
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        return
    for line in open(env_path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()


def _required(key):
    val = os.environ.get(key)
    if not val:
        print(f"ERROR: missing required env var {key}. Copy .env.example to .env and fill in.", file=sys.stderr)
        sys.exit(2)
    return val


# Slack browser-session tokens (xoxc/xoxd) — extract from your browser's
# devtools while logged into Slack. Bot tokens won't work here.
SLACK_XOXC_TOKEN = _required("SLACK_XOXC_TOKEN")
SLACK_XOXD_COOKIE = _required("SLACK_XOXD_COOKIE")

# Your workspace slug — the part before `.slack.com`
SLACK_WORKSPACE_DOMAIN = _required("SLACK_WORKSPACE_DOMAIN")


# ─── Vault paths (hardcoded — edit for your setup) ───────────────────────────

VAULT_ROOT = os.path.join(HOME, "Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault")
X_RESEARCH_DIR = os.path.join(VAULT_ROOT, "Research/X Research")
MASTER_INDEX = os.path.join(X_RESEARCH_DIR, "Tweets-from-Slack.md")
VAULT_LOG = os.path.join(VAULT_ROOT, "log.md")


# ─── Pipeline state (lives next to this file, gitignored) ────────────────────

STORAGE_STATE_FILE = os.path.join(ROOT, "storage_state.json")
PROCESSED_URLS_FILE = os.path.join(ROOT, "state.json")
RUN_LOG = os.path.join(ROOT, "runs.log")
LOCK_DIR = "/tmp/tweet-pipeline.lock"
LOCK_STALE_SECONDS = 2 * 60 * 60  # 2 hours


# ─── Scraping knobs ──────────────────────────────────────────────────────────

LOOKBACK_DAYS = 8  # weekly cron + slight overlap to avoid edge misses
SCRAPE_TIMEOUT_MS = 15000
INTRA_SCRAPE_SLEEP_MIN_S = 3
INTRA_SCRAPE_SLEEP_MAX_S = 7
MAX_CONSECUTIVE_FAILS = 3
