"""
US/Europe News Aggregator
- RSS feeds se latest news fetch karta hai
- Google Gemini (free tier) se title/summary rewrite karta hai (original content ke liye)
- news_data.json mein store karta hai
- templates/index_template.html se index.html generate karta hai
"""

import os
import json
import time
import hashlib
from datetime import datetime, timezone

import feedparser
import requests
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

DATA_FILE = "news_data.json"
MAX_ITEMS = 60          # kitni news total website par dikhengi
MAX_NEW_PER_RUN = 8     # ek run mein max kitni nayi news rewrite hongi (free API limits ka khayal)

# US + Europe RSS feeds
RSS_FEEDS = {
    "USA": [
        "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
        "https://feeds.npr.org/1004/rss.xml",
        "https://moxie.foxnews.com/google-publisher/world.xml",
    ],
    "Europe": [
        "https://feeds.bbci.co.uk/news/world/europe/rss.xml",
        "https://www.euronews.com/rss?level=theme&name=news",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ],
}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_existing_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def make_id(link):
    return hashlib.md5(link.encode("utf-8")).hexdigest()


def rewrite_with_gemini(title, summary):
    """Gemini free tier se title/summary rewrite karta hai.
    Agar API key na ho ya call fail ho, original text wapas kar deta hai."""
    if not GEMINI_API_KEY:
        return title, summary

    prompt = (
        "Rewrite the following news headline and summary in clear, original "
        "English wording (do not copy phrases verbatim). Keep facts accurate. "
        "Respond ONLY in JSON format like: "
        '{"title": "...", "summary": "..."}\n\n'
        f"Headline: {title}\nSummary: {summary}"
    )

    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        resp = requests.post(GEMINI_URL, json=body, timeout=30)
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
        parsed = json.loads(text)
        new_title = parsed.get("title", title).strip()
        new_summary = parsed.get("summary", summary).strip()
        return new_title or title, new_summary or summary
    except Exception as e:
        print(f"  [Gemini rewrite failed: {e}] -> using original text")
        return title, summary


def fetch_feed_items(region, url):
    items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            link = entry.get("link", "").strip()
            published = entry.get("published", "") or entry.get("updated", "")
            if not title or not link:
                continue
            items.append({
                "region": region,
                "title": title,
                "summary": summary,
                "link": link,
                "published": published,
                "source": feed.feed.get("title", url),
            })
    except Exception as e:
        print(f"  [Feed error: {url} -> {e}]")
    return items


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    existing = load_existing_data()
    existing_ids = {item["id"] for item in existing}

    new_items = []
    for region, feeds in RSS_FEEDS.items():
        for url in feeds:
            print(f"Fetching {region} feed: {url}")
            for raw in fetch_feed_items(region, url):
                item_id = make_id(raw["link"])
                if item_id in existing_ids:
                    continue
                raw["id"] = item_id
                new_items.append(raw)
                existing_ids.add(item_id)

    print(f"Found {len(new_items)} new items.")

    rewritten_count = 0
    for item in new_items:
        if rewritten_count < MAX_NEW_PER_RUN:
            print(f"  Rewriting: {item['title'][:60]}...")
            new_title, new_summary = rewrite_with_gemini(item["title"], item["summary"])
            item["title"] = new_title
            item["summary"] = new_summary
            rewritten_count += 1
            time.sleep(1)  # rate-limit ke liye chota wait
        item["fetched_at"] = datetime.now(timezone.utc).isoformat()

    combined = new_items + existing
    # Sort by fetched_at (newest first), trim to MAX_ITEMS
    combined.sort(key=lambda x: x.get("fetched_at", ""), reverse=True)
    combined = combined[:MAX_ITEMS]

    save_data(combined)
    render_site(combined)


def render_site(data):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("index_template.html")

    usa_news = [i for i in data if i["region"] == "USA"]
    europe_news = [i for i in data if i["region"] == "Europe"]

    html = template.render(
        usa_news=usa_news,
        europe_news=europe_news,
        updated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("index.html generated.")


if __name__ == "__main__":
    main()
