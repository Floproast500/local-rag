import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# A pool of modern user-agent strings (desktop + mobile).
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36 Edg/114.0.1823.51",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    # Chrome on Android
    "Mozilla/5.0 (Linux; Android 13; SM-G973F) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.5735.199 Mobile Safari/537.36",
    # iPhone Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    # iPad Safari
    "Mozilla/5.0 (iPad; CPU OS 16_3 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
]

def get_random_user_agent():
    """Pick a random user agent from the pool."""
    return random.choice(USER_AGENTS)

def fetch_url_with_rotating_ua(url, timeout=10):
    """Fetch a URL with a random User-Agent, returning the response."""
    headers = {
        "User-Agent": get_random_user_agent()
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()  # raise if 4xx/5xx
    return resp

def fetch_sitemap_urls(sitemap_url, visited=None):
    """
    Recursively expand a (Yoast) sitemap index or a normal sitemap
    to get final page URLs.
    Uses rotating user agents for each request.
    """
    if visited is None:
        visited = set()
    if sitemap_url in visited:
        return []

    visited.add(sitemap_url)
    page_urls = []

    try:
        response = fetch_url_with_rotating_ua(sitemap_url)
    except Exception as e:
        print(f"Error fetching sitemap {sitemap_url}: {e}")
        return page_urls

    soup = BeautifulSoup(response.text, "xml")
    sitemap_index = soup.find("sitemapindex")
    if sitemap_index:
        # It's a sitemap index with multiple <sitemap> entries
        sitemaps = sitemap_index.find_all("sitemap")
        for sm in sitemaps:
            loc = sm.find("loc")
            if loc:
                sub_sitemap_url = loc.get_text(strip=True)
                page_urls.extend(fetch_sitemap_urls(sub_sitemap_url, visited=visited))
    else:
        # Possibly a normal sitemap with <urlset> or just <loc> tags
        urls = soup.find_all("url")
        if urls:
            for u in urls:
                loc = u.find("loc")
                if loc:
                    page_urls.append(loc.get_text(strip=True))
        else:
            # fallback approach: parse all <loc> tags if no <url>
            loc_tags = soup.find_all("loc")
            for loc in loc_tags:
                page_urls.append(loc.get_text(strip=True))

    return page_urls

def fetch_page_content(page_url):
    """
    Retrieve the HTML content of a single page using rotating user agents,
    and return the entire visible text.
    """
    try:
        resp = fetch_url_with_rotating_ua(page_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        content = soup.get_text(separator=" ", strip=True)
        return content
    except Exception as e:
        print(f"Failed to fetch {page_url}: {e}")
        return ""