"""
TakeMeter data collector for r/soccer.
Uses Reddit's public JSON API — no API key or account required.

Usage:
    pip install requests
    python collect_data.py
"""

import csv
import json
import os
import re
import time
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (takemeter-collector/1.0)"}
BASE = "https://www.reddit.com/r/soccer"


def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def clean(text):
    text = re.sub(r"\s+", " ", text).strip()
    return text[:600]


def collect():
    posts = []

    def add(text, source):
        text = clean(text)
        if len(text) < 25:
            return
        posts.append({"text": text, "label": "", "source": source, "notes": ""})

    # ── top posts (month) ──────────────────────────────────────────────────────
    print("Fetching top posts (month)...")
    after = None
    for _ in range(3):  # 3 pages × ~25 posts
        url = f"{BASE}/top.json?t=month&limit=25"
        if after:
            url += f"&after={after}"
        try:
            data = fetch_json(url)
            items = data["data"]["children"]
            after = data["data"].get("after")
            for item in items:
                p = item["data"]
                body = p.get("selftext", "")
                if body and body not in ("[removed]", "[deleted]", ""):
                    add(body, f"post:{p['id']}")
                else:
                    add(p["title"], f"title:{p['id']}")
            time.sleep(1.5)
        except Exception as e:
            print(f"  Error: {e}")
            break

    # ── hot posts ──────────────────────────────────────────────────────────────
    print("Fetching hot posts...")
    try:
        data = fetch_json(f"{BASE}/hot.json?limit=50")
        for item in data["data"]["children"]:
            p = item["data"]
            body = p.get("selftext", "")
            if body and body not in ("[removed]", "[deleted]", ""):
                add(body, f"post:{p['id']}")
            else:
                add(p["title"], f"title:{p['id']}")
        time.sleep(1.5)
    except Exception as e:
        print(f"  Error: {e}")

    # ── top posts (year) ───────────────────────────────────────────────────────
    print("Fetching top posts (year)...")
    try:
        data = fetch_json(f"{BASE}/top.json?t=year&limit=50")
        for item in data["data"]["children"]:
            p = item["data"]
            body = p.get("selftext", "")
            if body and body not in ("[removed]", "[deleted]", ""):
                add(body, f"post:{p['id']}")
            else:
                add(p["title"], f"title:{p['id']}")
        time.sleep(1.5)
    except Exception as e:
        print(f"  Error: {e}")

    # ── comments from recent match threads ────────────────────────────────────
    print("Fetching match thread comments...")
    try:
        search = fetch_json(f"{BASE}/search.json?q=Match+Thread&sort=top&t=month&limit=5")
        for item in search["data"]["children"]:
            post_id = item["data"]["id"]
            try:
                thread = fetch_json(f"{BASE}/comments/{post_id}.json?limit=40&depth=1")
                comments = thread[1]["data"]["children"]
                for c in comments[:30]:
                    if c.get("kind") == "t1":
                        body = c["data"].get("body", "")
                        if body not in ("[removed]", "[deleted]", ""):
                            add(body, f"comment:{c['data']['id']}")
                time.sleep(1.5)
            except Exception as e:
                print(f"  Comment fetch error: {e}")
    except Exception as e:
        print(f"  Search error: {e}")

    # ── discussion flair posts ─────────────────────────────────────────────────
    print("Fetching discussion posts...")
    for query in ["tactical analysis formation", "unpopular opinion soccer",
                  "xG statistics pressing", "transfer window debate"]:
        try:
            data = fetch_json(f"{BASE}/search.json?q={query.replace(' ', '+')}&sort=top&t=year&limit=15")
            for item in data["data"]["children"]:
                p = item["data"]
                body = p.get("selftext", "")
                if body and body not in ("[removed]", "[deleted]", ""):
                    add(body, f"post:{p['id']}")
                else:
                    add(p["title"], f"title:{p['id']}")
            time.sleep(1.5)
        except Exception as e:
            print(f"  Search error for '{query}': {e}")

    # ── deduplicate ────────────────────────────────────────────────────────────
    seen = set()
    unique = []
    for p in posts:
        key = p["text"][:80].lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)

    os.makedirs("data", exist_ok=True)
    outfile = "data/raw_posts.csv"
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "source", "notes"])
        writer.writeheader()
        writer.writerows(unique)

    print(f"\nDone. {len(unique)} unique posts/comments saved to {outfile}")
    print("Next step: run  python annotate.py  to auto-label them.")


if __name__ == "__main__":
    collect()
