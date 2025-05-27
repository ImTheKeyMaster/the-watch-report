import feedparser
import json
import os
from datetime import datetime

# Define all RSS sources
RSS_FEEDS = [
    # Watch news websites
    ("Hodinkee", "https://www.hodinkee.com/feed"),
    ("WatchTime", "https://www.watchtime.com/feed/"),
    ("Revolution", "https://revolutionwatch.com/feed/"),
    ("Europa Star", "https://europastar.com/spip.php?page=backend"),
    ("A Blog to Watch", "https://www.ablogtowatch.com/feed/"),
    ("Time+Tide", "https://timeandtidewatches.com/feed/"),

    # YouTube Channels (RSS feeds)
    ("Teddy Baldassarre", "https://www.youtube.com/feeds/videos.xml?channel_id=UCq8xk0iPzJeFGzznpt3wqDw"),
    ("Jenni Elle", "https://www.youtube.com/feeds/videos.xml?channel_id=UC0n4hzHPL2Exn4UmkYb6QDQ"),
    ("Nico Leonard", "https://www.youtube.com/feeds/videos.xml?channel_id=UCS9nnC8mN6k1cYXYj4ZNTXw"),
    ("The Time Teller", "https://www.youtube.com/feeds/videos.xml?channel_id=UCL2lt5SYWzGtvzM5hWJlt3w"),
    ("Andrew Morgan", "https://www.youtube.com/feeds/videos.xml?channel_id=UCkWgIEj2p63rVkrWnQf18_w"),
    ("HSNY", "https://www.youtube.com/feeds/videos.xml?channel_id=UCFvjSnYFqEwglrmoEUwRekg")
]

# Parse all feeds
articles = []

for source, url in RSS_FEEDS:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Try to find image
            image_url = None

            if 'media_thumbnail' in entry:
                image_url = entry.media_thumbnail[0]['url']
            elif 'media_content' in entry and isinstance(entry.media_content, list):
                image_url = entry.media_content[0].get('url')
            elif 'summary' in entry and 'img src="' in entry.summary:
                start = entry.summary.find('img src="') + 9
                end = entry.summary.find('"', start)
                image_url = entry.summary[start:end]

            if not image_url or 'default' in image_url:
                continue

            published = entry.get('published_parsed') or entry.get('updated_parsed')
            pub_date = datetime(*published[:6]).isoformat() if published else datetime.utcnow().isoformat()

            articles.append({
                'title': entry.title,
                'link': entry.link,
                'image': image_url,
                'source': source,
                'published': pub_date
            })
    except Exception as e:
        print(f"Error processing {url}: {e}")

# Sort by date descending
articles.sort(key=lambda x: x['published'], reverse=True)

# Save to JSON file
os.makedirs("data", exist_ok=True)
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"Fetched {len(articles)} articles.")
