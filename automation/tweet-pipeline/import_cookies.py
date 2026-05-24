#!/usr/bin/env python3
"""Import x.com cookies from your real browser → Playwright storage_state.json.

Why this script exists: X's risk system blocks Playwright-launched logins
(automation-controlled Chromium has detectable fingerprints, and even password
entry will be rejected with "Sorry, you are not allowed to log in at this time").
So instead of logging in via automation, we lift the session cookies from your
actual Chrome/Safari/Brave where you're already logged in. The macOS Keychain
prompts once for the Chrome encryption key — click Always Allow.

Only x.com cookies are read. Nothing else is touched, persisted, or transmitted.

Usage:
    .venv/bin/python import_cookies.py [chrome|safari|brave|firefox]

Default browser is chrome.
"""
import json
import os
import sys

import browser_cookie3 as bc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import STORAGE_STATE_FILE

BROWSERS = {
    "chrome":  bc.chrome,
    "safari":  bc.safari,
    "brave":   bc.brave,
    "firefox": bc.firefox,
}


def main():
    browser = sys.argv[1] if len(sys.argv) > 1 else "chrome"
    if browser not in BROWSERS:
        print(f"Unknown browser: {browser}. Options: {list(BROWSERS)}")
        sys.exit(1)

    print(f"Reading x.com cookies from {browser} …")
    print("(macOS may prompt for Keychain access — click Always Allow.)")
    try:
        cj = BROWSERS[browser](domain_name="x.com")
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        print(f"   If '{browser}' isn't where you're logged into X, try another:")
        for alt in BROWSERS:
            if alt != browser:
                print(f"     python import_cookies.py {alt}")
        sys.exit(2)

    cookies = []
    for c in cj:
        # Belt + braces: only keep x.com cookies even though browser_cookie3 filters
        if "x.com" not in (c.domain or ""):
            continue
        cookies.append({
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path or "/",
            "expires": c.expires if c.expires else -1,
            "httpOnly": bool(getattr(c, "_rest", {}).get("HttpOnly"))
                        or bool(getattr(c, "_rest", {}).get("httponly")),
            "secure": bool(c.secure),
            "sameSite": "Lax",
        })

    if not cookies:
        print(f"\n❌ Found 0 x.com cookies in {browser}.")
        print(f"   Are you logged into X in {browser}? Try a different browser if not.")
        sys.exit(3)

    has_auth = any(c["name"] in ("auth_token", "ct0") for c in cookies)
    with open(STORAGE_STATE_FILE, "w") as f:
        json.dump({"cookies": cookies, "origins": []}, f, indent=2)
    os.chmod(STORAGE_STATE_FILE, 0o600)

    print(f"\n✓ Saved {len(cookies)} x.com cookies to {STORAGE_STATE_FILE}")
    print(f"  Permissions set to 600 (owner-read-only).")
    if has_auth:
        print(f"  ✓ Found session cookie (auth_token / ct0) — auth should work.")
    else:
        print(f"  ⚠ No auth_token / ct0 cookie. You may not be logged in,")
        print(f"    or {browser} is using a different profile. Try another browser.")


if __name__ == "__main__":
    main()
