import os
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from openai import OpenAI

# === CONFIGURATION ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY"
OUTPUT_PATH = "data/news.json"
NEWS_SOURCES = [
    "https://www.hodinkee.com",
    "https://www.watchtime.com",
    "https://www.revolution.watch",
    "https://www.europastar.com"
]
PLACEHOLDER_IMAGE = "https://via.placeholder.com/800x400?text=No+Image"

# === FUNCTIONS ===

def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
    return None

def extract_links(source_html, base_url):
    soup = BeautifulSoup(source_html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("http"):
            full_url = href
        elif href.startswith("/"):
            full_url = base_url + href
        else:
            continue
        title = a.get_text(strip=True)
        if title and len(title.split()) > 3:
            links.append({"url": full_url, "title": title})
    return links[:10]

def validate_image_url(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200 and 'image' in r.headers.get('Content-Type', '')
    except:
        return False

def get_summary_from_openai(client, article_url):
    prompt = f"""You are a watch enthusiast and expert summarizer. Summarize the most recent article from this URL in 1-2 sentences. Also extract the title and a high-quality image URL if available.

URL: {article_url}

Respond in JSON format like this:
{{
  "title": "Title of the article",
  "summary": "A 1-2 sentence summary",
  "image_url": "https://link-to-image.jpg"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        result = json.loads(response.choices[0].message.content)
        result["url"] = article_url

        # Image validation
        if not validate_image_url(result.get("image_url", "")):
            result["image_url"] = PLACEHOLDER_IMAGE

        return result
    except Exception as e:
        print(f"OpenAI summary failed for {article_url}: {e}")
        return None

# === MAIN ===

def main():
    client = OpenAI(api_key=OPENAI_API_KEY)

    all_articles = []

    for site in NEWS_SOURCES:
        print(f"Fetching from {site}...")
        html = fetch_html(site)
        if not html:
            continue

        base_url = site.rstrip('/')
        links = extract_links(html, base_url)

        for link in links:
            print(f"Summarizing: {link['title']}")
            summary = get_summary_from_openai(client, link["url"])
            if summary:
                all_articles.append(summary)

    print(f"Writing {len(all_articles)} articles to {OUTPUT_PATH}")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
