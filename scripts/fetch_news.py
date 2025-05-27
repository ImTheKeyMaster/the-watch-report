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
    for a in soup.find_all("a",_
