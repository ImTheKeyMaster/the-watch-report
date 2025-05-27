import feedparser
import json
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

# List of RSS feed URLs from watch-related websites
WATCH_FEEDS = [
    "https://hodinkee.com/feed",
    "https://www.ablogtowatch.com/feed/",
    "https://monochrome-watches.com/feed/",
    "https://wornandwound.com/feed/",
    "https://timeandtidewatches.com/feed/",
    "https://watchtime.com/feed/"
]

# YouTube channels to include (one latest video per channel)
YOUTUBE_CHANNELS = {
    "Teddy Baldassarre": "UCPsgQZxEACESR0ogWm0dUFw",
    "Jenni Elle": "UCvIIb5YF8sUnm1D62jCvVVw",
    "Nico Leonard": "UC-IVpEe1GQYclVEGLgPd82Q",
    "The Time Teller": "UCt4id9K_t9zu-O23182P4vQ",
    "Andrew Morgan": "UCOu5VKZIHDXS-cHn9TOC0Qg",
    "Horological Society of New York": "UC0E08avdHIH-7AMeVcBGRPQ",
}

def fetch_rss_articles():
    articles = []
    for feed_url in WATCH_FEEDS:
        feed = feedparser.parse(feed_url)
        print(f"Fetched {len(feed.entries)} entries from {feed_url}")
        for entry in feed.entries:
            article = {
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "thumbnail": extract_thumbnail(entry),
                "source": urlparse(feed_url).netloc.replace("www.", "")
            }
            articles.append(article)
    return articles

def fetch_youtube_articles():
    articles = []
    for name, channel_id in YOUTUBE_CHANNELS.items():
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(url)
        print(f"Fetched {len(feed.entries)} entries from {url}")

        if feed.entries:
            entry = feed.entries[0]  # only latest video
            video_id = entry.get("yt_videoid")
            if not video_id:
                continue

            article = {
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "source": name
            }
            articles.append(article)
    return articles

def extract_thumbnail(entry):
    media_content = entry.get("media_content", [])
    if media_content:
        return media_content[0].get("url")
    if "media_thumbnail" in entry:
        return entry["media_thumbnail"][0].get("url")
    return None

def parse_date(article):
    try:
        return datetime(*article["published_parsed"][:6], tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)

def main():
    rss_articles = fetch_rss_articles()
    youtube_articles = fetch_youtube_articles()
    all_articles = rss_articles + youtube_articles

    # Attempt to parse published date properly
    for article in all_articles:
        if "published_parsed" not in article:
            parsed = feedparser.parse(article["link"])
            if parsed.entries:
                article["published_parsed"] = parsed.entries[0].get("published_parsed")
        if "published_parsed" not in article:
            article["published_parsed"] = datetime.now(timezone.utc).timetuple()

    # Sort by date
    all_articles = sorted(all_articles, key=lambda x: x["published_parsed"], reverse=True)

    # Save to JSON
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "news.json"), "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
