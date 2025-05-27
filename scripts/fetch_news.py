import feedparser
import json
import os
import nltk
nltk.download('punkt')
from datetime import datetime, timezone
from newspaper import Article, Config
from slugify import slugify

# RSS feeds to parse
rss_feeds = [
    "https://www.hodinkee.com/articles/rss",
    "https://monochrome-watches.com/feed/",
    "https://wornandwound.com/feed/",
    "https://www.ablogtowatch.com/feed/",
    "https://www.fratellowatches.com/feed/",
    "https://watchclicker.com/feed/",
    "https://www.timeandwatches.com/feeds/posts/default",
    "https://www.revolution.watch/feed/"
]

youtube_channels = [
    "UCPsgQZxEACESR0ogWm0dUFw",  # Teddy Baldassarre
    "UCvIIb5YF8sUnm1D62jCvVVw",  # Jenni Elle
    "UC-IVpEe1GQYclVEGLgPd82Q",  # Nico Leonard
    "UCt4id9K_t9zu-O23182P4vQ",  # The Time Teller
    "UCOu5VKZIHDXS-cHn9TOC0Qg",  # Andrew Morgan
    "UC0E08avdHIH-7AMeVcBGRPQ"   # Horological Society of New York
]

max_articles_per_feed = 3

# Configure user-agent for newspaper3k
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
config = Config()
config.browser_user_agent = user_agent

all_articles = []

for url in rss_feeds:
    feed = feedparser.parse(url)
    print(f"Fetched {len(feed.entries)} entries from {url}")
    for entry in feed.entries[:max_articles_per_feed]:
        try:
            article = Article(entry.link, config=config)
            article.download()
            article.parse()
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            published_date = datetime.fromtimestamp(0, tz=timezone.utc)
            if published:
                published_date = datetime(*published[:6], tzinfo=timezone.utc)
            all_articles.append({
                "title": article.title,
                "link": entry.link,
                "source": feed.feed.get("title", ""),
                "published": published_date.isoformat(),
                "thumbnail": article.top_image if article.top_image else ""
            })
        except Exception as e:
            print(f"Error processing article: {entry.link}\n{e}")

for channel_id in youtube_channels:
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    print(f"Fetched {len(feed.entries)} entries from {feed_url}")
    for entry in feed.entries[:1]:  # Only latest video
        try:
            published = entry.get("published_parsed")
            published_date = datetime.fromtimestamp(0, tz=timezone.utc)
            if published:
                published_date = datetime(*published[:6], tzinfo=timezone.utc)
            media_thumbnail = entry.get("media_thumbnail", [{}])[0].get("url", "")
            all_articles.append({
                "title": f"(VIDEO) {entry.title}",
                "link": entry.link,
                "source": feed.feed.get("title", "YouTube"),
                "published": published_date.isoformat(),
                "thumbnail": media_thumbnail
            })
        except Exception as e:
            print(f"Error processing YouTube entry: {entry.link}\n{e}")

def parse_date(article):
    try:
        return datetime.fromisoformat(article["published"])
    except:
        return datetime.now(timezone.utc)

all_articles = sorted(all_articles, key=parse_date, reverse=True)

output_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "news.json"), "w", encoding="utf-8") as f:
    json.dump(all_articles, f, indent=2, ensure_ascii=False)
