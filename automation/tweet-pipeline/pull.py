#!/usr/bin/env python3
"""Weekly tweet pipeline:

1. Slack search API → find x.com URLs shared in the workspace, last LOOKBACK_DAYS
2. Diff against state.json (URLs already processed)
3. For each new URL: Playwright + saved cookies → extract tweet body + thread
4. Classify into topic, append to the right tweets-<topic>.md file
5. Update state.json + vault log

Designed to run unattended via launchd. Idempotent — re-running is safe.
Concurrency-safe via mkdir lockdir (memory-os convention).
"""
import asyncio
import datetime as dt
import json
import os
import random
import re
import shutil
import sys
import time
import traceback
from collections import OrderedDict

import requests
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    SLACK_XOXC_TOKEN, SLACK_XOXD_COOKIE, SLACK_WORKSPACE_DOMAIN,
    X_RESEARCH_DIR, MASTER_INDEX, VAULT_LOG,
    STORAGE_STATE_FILE, PROCESSED_URLS_FILE, RUN_LOG,
    LOCK_DIR, LOCK_STALE_SECONDS,
    LOOKBACK_DAYS, SCRAPE_TIMEOUT_MS,
    INTRA_SCRAPE_SLEEP_MIN_S, INTRA_SCRAPE_SLEEP_MAX_S,
    MAX_CONSECUTIVE_FAILS,
)

URL_RE = re.compile(r"https://x\.com/[A-Za-z0-9_]+/status/\d+")


# ─── Logging ────────────────────────────────────────────────────────────────

def log(msg, also_print=True):
    """Per-run script log. Pretty-printed for human eyeballs."""
    line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
    if also_print:
        print(line, flush=True)
    with open(RUN_LOG, "a") as f:
        f.write(line + "\n")


def vault_log(event, body):
    """memory-os canonical vault-log format: YYYY-MM-DDTHH:MM:SSZ | script | event | body"""
    ts = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts} | tweet-pipeline | {event} | {body}\n"
    try:
        with open(VAULT_LOG, "a") as f:
            f.write(line)
    except Exception as e:
        log(f"Vault log write failed: {e}")


# ─── Lockdir (memory-os concurrency pattern) ────────────────────────────────

def acquire_lock():
    """mkdir-based lock. Returns True if acquired, False if held by a recent run."""
    if os.path.exists(LOCK_DIR):
        try:
            age = time.time() - os.path.getmtime(LOCK_DIR)
            if age > LOCK_STALE_SECONDS:
                log(f"Stale lock found ({age:.0f}s old) — clearing")
                shutil.rmtree(LOCK_DIR, ignore_errors=True)
            else:
                return False
        except FileNotFoundError:
            pass
    try:
        os.makedirs(LOCK_DIR, exist_ok=False)
        return True
    except FileExistsError:
        return False


def release_lock():
    shutil.rmtree(LOCK_DIR, ignore_errors=True)


# ─── Slack search ────────────────────────────────────────────────────────────

def slack_search_xcom_urls(days_back):
    """Hit Slack's search.modules with xoxc/xoxd. Returns OrderedDict url -> meta."""
    headers = {
        "Cookie": f"d={SLACK_XOXD_COOKIE}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    after = (dt.date.today() - dt.timedelta(days=days_back)).isoformat()
    cutoff_ts = (dt.datetime.now() - dt.timedelta(days=days_back)).timestamp()
    seen = OrderedDict()

    page = 1
    while True:
        data = {
            "token": SLACK_XOXC_TOKEN,
            "module": "messages",
            "query": f"x.com after:{after}",
            "count": "100",
            "page": str(page),
            "highlight": "0",
            "extracts": "1",
            "sort": "timestamp",
            "sort_dir": "desc",
        }
        resp = requests.post(
            f"https://{SLACK_WORKSPACE_DOMAIN}.slack.com/api/search.modules",
            headers=headers, data=data, timeout=30,
        )
        resp.raise_for_status()
        j = resp.json()
        if not j.get("ok"):
            log(f"Slack search error: {j}")
            break

        items = j.get("items", [])
        if not items:
            break

        for item in items:
            channel = item.get("channel", {})
            ch_id = channel.get("id", "")
            ch_name = channel.get("name", "")
            for msg in item.get("messages", []):
                text = msg.get("text", "") or ""
                ts = msg.get("ts", "")
                permalink = msg.get("permalink", "")
                try:
                    if ts and float(ts) < cutoff_ts:
                        continue
                except ValueError:
                    pass
                # Also harvest URLs from attachment unfurls (from_url / original_url)
                attach_urls = []
                for att in msg.get("attachments", []):
                    for k in ("from_url", "original_url"):
                        u = att.get(k)
                        if u:
                            attach_urls.append(u)
                all_urls = URL_RE.findall(text) + [u for u in attach_urls for u in URL_RE.findall(u)]
                for u in all_urls:
                    if u not in seen:
                        seen[u] = {
                            "channel_id": ch_id,
                            "channel_name": ch_name,
                            "ts": ts,
                            "permalink": permalink,
                            "share_date": dt.datetime.fromtimestamp(float(ts)).date().isoformat() if ts else "",
                        }

        pagination = j.get("pagination", {})
        if page >= pagination.get("page_count", 1):
            break
        page += 1

    return seen


# ─── Tweet scraping ──────────────────────────────────────────────────────────

async def scrape_tweet(context, url):
    page = await context.new_page()
    try:
        await page.goto(url, timeout=SCRAPE_TIMEOUT_MS, wait_until="domcontentloaded")
        try:
            await page.wait_for_selector('article[data-testid="tweet"]', timeout=SCRAPE_TIMEOUT_MS)
        except Exception:
            pass
        tweets = await page.evaluate("""
            () => {
                const articles = document.querySelectorAll('article[data-testid="tweet"]');
                const out = [];
                for (const a of articles) {
                    let handle = '';
                    const userEl = a.querySelector('div[data-testid="User-Name"]');
                    if (userEl) {
                        const handleSpan = userEl.querySelector('a[href^="/"] span');
                        if (handleSpan) handle = (handleSpan.innerText || '').trim();
                    }
                    let text = '';
                    const textEl = a.querySelector('div[data-testid="tweetText"]');
                    if (textEl) text = (textEl.innerText || '').trim();
                    let permalink = '';
                    let datetime = '';
                    const timeEl = a.querySelector('time');
                    if (timeEl) {
                        datetime = timeEl.getAttribute('datetime') || '';
                        const a2 = timeEl.closest('a');
                        if (a2) permalink = a2.getAttribute('href') || '';
                    }
                    out.push({ handle, text, permalink, datetime });
                }
                return out;
            }
        """)
        return tweets
    finally:
        await page.close()


def extract_handle_and_id(url):
    parts = url.split("/")
    return parts[3], parts[5].split("?")[0]


def build_entry(url, scraped_tweets, slack_meta):
    handle, tid = extract_handle_and_id(url)
    main = None
    own_thread = []
    for t in scraped_tweets:
        if not t["permalink"]:
            continue
        perm_id = t["permalink"].rstrip("/").split("/")[-1]
        if perm_id == tid:
            main = t
        elif handle.lower() in (t["handle"] or "").lower().replace("@", ""):
            own_thread.append(t)
    if main is None and scraped_tweets:
        main = scraped_tweets[0]

    body = (main or {}).get("text", "") or "_(could not extract tweet text)_"
    author = (main or {}).get("handle", "") or f"@{handle}"
    date = ""
    if main and main.get("datetime"):
        date = main["datetime"][:10]
    elif slack_meta.get("share_date"):
        date = slack_meta["share_date"]
    name = author if author.startswith("@") else f"@{author}"

    lines = [f"- **[{name}]({url})** — {date}"]
    for line in body.split("\n"):
        lines.append(f"  > {line.strip()}" if line.strip() else "  >")
    if own_thread:
        lines.append("  >")
        lines.append("  > _Thread continuation:_")
        for t in own_thread:
            for line in (t.get("text", "") or "").split("\n"):
                if line.strip():
                    lines.append(f"  > {line.strip()}")

    ch_label = f"{slack_meta.get('channel_id','')} (#{slack_meta.get('channel_name','')})"
    return ch_label, "\n".join(lines) + "\n"


# ─── Classification (mirrors the original split logic) ──────────────────────

TOPICS = [
    ("on-prem-and-specialists", [
        r"\bon[- ]?prem\b", r"\bair[- ]?gap", r"\bsovereign\b", r"\bot network\b", r"\bcui\b",
        r"\bitar\b", r"\bclassified\b", r"\bdefense\b", r"\bvectorai\b", r"\bin[- ]?house\s+(open[- ]source\s+)?model",
        r"\blocal(?:ly)?\s+(?:run|host|deploy)", r"\bon[- ]?device\b", r"\bllama\s+\d", r"\bqwen\b", r"\bm5\s*max\b",
        r"\bsub[- ]?quadratic\b", r"\beval(?:s|uation)?\b", r"\bpost[- ]?training\b", r"\bfine[- ]?tune",
        r"\bspecialist\s+model", r"\bautoresearch\b", r"\brl\b", r"\bramp\s+fast", r"\bchroma\s+context",
    ]),
    ("ai-services-business", [
        r"\$999\b", r"\$10k\b", r"\baudit\b", r"\bretainer\b", r"\bservice[- ]as[- ]?a[- ]?software\b",
        r"\bservice business\b", r"\bagency\b", r"\bfractional\b", r"\bcaio\b",
        r"\bvoice\s+agent", r"\bhvac\b", r"\bplumb", r"\bpest control", r"\blandscap",
        r"\bcold\s+out", r"\boutbound\b", r"\bprospect", r"\bpostcard", r"\blinkedin\b",
        r"\bcodie\s+sanchez", r"\bcorey\s+ganim",
    ]),
    ("strategy-and-counter-narratives", [
        r"\byc\b", r"\bw26\b", r"\bdemo\s+day", r"\bbatch\b", r"\blump\s+of\s+labor\b",
        r"\bdark\s+code\b", r"\bagent\s+deployer\b", r"\bcontext\s+farm", r"\bdoomer",
        r"\bfounder[- ]market\s+fit\b", r"\bcompressible\b", r"\bmoat\b", r"\bdistribution\s+is\b",
        r"\bcommodit", r"\bcompress",
    ]),
    ("media-and-design", [
        r"\bclaude\s+design\b", r"\bchatgpt\s+image", r"\bnano\s+banana\b", r"\bstitch\s+by\s+google\b",
        r"\bdall[- ]?e\b", r"\bseedance\b", r"\bkling\b", r"\bsora\b", r"\bveo\b", r"\bmidjourney\b",
        r"\bgamma\b", r"\bcanva\b", r"\bslides?\b", r"\bvideo\s+(?:gen|model|tool)",
        r"\bimage\s+(?:gen|model)", r"\belevenlabs\b", r"\baqua\s+voice\b",
    ]),
    ("claude-code-workflows", [
        r"\bclaude\s+code\b", r"\bcodex\b", r"\bcursor\b", r"\b/loop\b", r"\b/goal\b",
        r"\b/schedule\b", r"\broutine", r"\bskills?\.?(?:md|json|folder)?\b",
        r"\bsubagent", r"\bplugin\s+marketplace\b", r"\bhook\b", r"\bdispatch\b",
        r"\bralph\s+loop\b", r"\bclaude\.md\b", r"\bopus\s+\d", r"\bsonnet\s+\d", r"\bhaiku\s+\d",
    ]),
    ("company-brain-memory", [
        r"\bcompany\s+brain\b", r"\bcompany\s+os\b", r"\bgbrain\b", r"\bhivemind\b", r"\bnanomem\b",
        r"\bsecond\s+brain\b", r"\bllm[- ]?wiki\b", r"\bagentic\s+micro\s+company\b", r"\bamc\b",
        r"\bcontext\s+graph\b", r"\bobsidian\b", r"\btolaria\b", r"\bmemory\s+system",
    ]),
    ("agent-infrastructure", [
        r"\bagent\s+vault\b", r"\bagent\s+(?:os|operating)", r"\bbrowser\s+harness\b", r"\bbrowser\s+use\b",
        r"\bcomputer\s+use\b", r"\bagent[- ]?browser\b", r"\bmesa\b", r"\bmcp\s+server",
        r"\bstripe\s+link\b", r"\bheadless\s+(?:saas|api|360|browser)", r"\bagentforce\b",
        r"\bmanaged\s+agents?\b", r"\bcloud\s+agents?\b",
    ]),
]

BACKSTOP = [
    ("claude-code-workflows", [
        r"\banthropic\b", r"\bopenai\b", r"\bgpt[- ]?\d", r"\bclaude\b", r"\bcode\b", r"\bcli\b",
        r"\bdev(?:eloper)?", r"\bide\b", r"\bnpm\b", r"\bvibe[- ]?cod",
    ]),
    ("agent-infrastructure", [
        r"\bagent", r"\binfra", r"\bplatform", r"\bapi\b", r"\bsdk\b", r"\bstack\b", r"\bruntim", r"\bdeploy",
    ]),
]


def classify(entry_text):
    et = entry_text.lower()
    scores = {}
    for topic, patterns in TOPICS:
        s = sum(len(re.findall(p, et)) for p in patterns)
        if s:
            scores[topic] = s
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    for topic, patterns in BACKSTOP:
        if sum(len(re.findall(p, et)) for p in patterns):
            return topic
    return "agent-infrastructure"


def append_to_topic_file(topic, channel_label, entry_md):
    fp = os.path.join(X_RESEARCH_DIR, f"tweets-{topic}.md")
    if not os.path.exists(fp):
        log(f"  WARN: topic file {fp} doesn't exist — skipping append")
        return
    with open(fp) as f:
        content = f.read()
    heading = f"## {channel_label}"
    if heading in content:
        idx = content.find(heading)
        nl = content.find("\n", idx)
        insert_at = nl + 2 if content[nl+1:nl+2] == "\n" else nl + 1
        new_content = content[:insert_at] + "\n" + entry_md + content[insert_at:]
    else:
        new_content = content.rstrip() + f"\n\n{heading}\n\n{entry_md}"
    with open(fp, "w") as f:
        f.write(new_content)


# ─── Main pipeline ───────────────────────────────────────────────────────────

async def run():
    log(f"--- Pipeline run start (lookback {LOOKBACK_DAYS} days) ---")
    vault_log("start", f"lookback={LOOKBACK_DAYS}d")

    if os.path.exists(PROCESSED_URLS_FILE):
        processed = set(json.load(open(PROCESSED_URLS_FILE)))
    else:
        bak = MASTER_INDEX + ".bak"
        seed = set(URL_RE.findall(open(bak).read())) if os.path.exists(bak) else set()
        processed = seed
        log(f"First run — seeded {len(processed)} URLs from {bak}")
        vault_log("seed", f"{len(processed)} URLs seeded from {os.path.basename(bak)}")

    try:
        all_urls = slack_search_xcom_urls(LOOKBACK_DAYS)
    except Exception as e:
        log(f"Slack search FAILED: {e}")
        traceback.print_exc()
        vault_log("error", f"slack search failed: {e}")
        return

    log(f"Found {len(all_urls)} unique x.com URLs in Slack window")
    new_urls = OrderedDict((u, m) for u, m in all_urls.items() if u not in processed)
    log(f"  {len(new_urls)} are new")
    if not new_urls:
        vault_log("done", "no new URLs")
        return

    if not os.path.exists(STORAGE_STATE_FILE):
        log(f"ERROR: no storage state at {STORAGE_STATE_FILE}. Run import_cookies.py first.")
        vault_log("error", "no storage_state.json — run import_cookies.py")
        return

    consecutive_fails = 0
    appended_to = set()
    n_added = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=STORAGE_STATE_FILE)
        try:
            for i, (url, meta) in enumerate(new_urls.items(), 1):
                log(f"  [{i}/{len(new_urls)}] scraping {url}")
                try:
                    tweets = await scrape_tweet(context, url)
                    if not tweets:
                        log("    no tweets extracted (auth lapsed? page blank?)")
                        consecutive_fails += 1
                    else:
                        channel_label, entry_md = build_entry(url, tweets, meta)
                        topic = classify(entry_md)
                        append_to_topic_file(topic, channel_label, entry_md)
                        appended_to.add(topic)
                        processed.add(url)
                        n_added += 1
                        log(f"    ✓ classified {topic}, appended to tweets-{topic}.md ({len(entry_md)} chars)")
                        consecutive_fails = 0
                except Exception as e:
                    log(f"    ERROR: {e}")
                    consecutive_fails += 1
                if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                    log(f"!! STOP — {consecutive_fails} consecutive failures (auth may have lapsed; re-run import_cookies.py)")
                    vault_log("error", f"stopped after {consecutive_fails} consecutive fails — re-run import_cookies.py")
                    break
                if i < len(new_urls):
                    await asyncio.sleep(random.uniform(INTRA_SCRAPE_SLEEP_MIN_S, INTRA_SCRAPE_SLEEP_MAX_S))
        finally:
            await browser.close()

    with open(PROCESSED_URLS_FILE, "w") as f:
        json.dump(sorted(processed), f, indent=2)
    log(f"State saved: {len(processed)} total processed URLs")

    if appended_to:
        vault_log("done", f"added={n_added} topics={','.join(sorted(appended_to))}")
    else:
        vault_log("done", "no entries appended")

    log(f"--- Pipeline run done. {n_added} URLs added across {len(appended_to)} topic files ---")


def main():
    if not acquire_lock():
        log("Another run is in flight or stale lock < 2h old. Exiting clean.")
        sys.exit(0)
    try:
        asyncio.run(run())
    finally:
        release_lock()


if __name__ == "__main__":
    main()
